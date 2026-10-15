package com.afc.companion.net

import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import org.json.JSONException
import org.json.JSONObject

/**
 * CONTRACT-AFC-P2-API client (backend/src/api/openapi.yaml). Bodies are at most 64 KiB both ways;
 * api_timeout is 10 s, the alerts long poll reads for alert_poll_wait + 5 s = 25 s; idempotent calls
 * (GET, PUT /v1/profile) retry 429/503 up to api_retry_max = 3 times with 1, 2, 4 s backoff. Link
 * confirmation and Watch reports are never retried. All network and parsing run on Dispatchers.IO.
 */
class ApiClient(
    val baseUrl: String,
    val sessionToken: () -> String? = { null },
    val openConnection: (URL) -> HttpURLConnection = { it.openConnection() as HttpURLConnection },
    val backoff: suspend (Long) -> Unit = { delay(it) },
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO,
) {
    private val base: String = baseUrl.trimEnd('/')

    init {
        val url = runCatching { URL(base) }.getOrNull()
        require(url != null && url.userInfo == null && url.query == null && url.ref == null &&
            (url.protocol == "https" || (url.protocol == "http" && url.host in LOOPBACK_HOSTS))) {
            "API base URL must be https (http only for loopback)"
        }
    }

    suspend fun request(method: String, path: String, body: JSONObject? = null): ApiResponse = withContext(ioDispatcher) {
        require(method in METHODS && path.startsWith("/v1/")) { "Unsupported operation" }
        val payload = body?.toString()?.toByteArray(Charsets.UTF_8)
        require(payload == null || payload.size <= MAX_BODY_BYTES) { "Request body exceeds 64 KiB" }
        val idempotent = method == "GET" || method == "PUT"
        var attempt = 0
        var response = send(method, path, payload)
        while (idempotent && response.status in TRANSIENT && attempt < RETRY_MAX) {
            backoff(BACKOFF_BASE_MS shl attempt)
            attempt++
            response = send(method, path, payload)
        }
        response
    }

    suspend fun envelope(body: JSONObject, heldRevision: Long? = null): Envelope? = Envelope.from(body, heldRevision)

    suspend fun issueLinkCode(): ApiResult<DeviceCode> = call("POST", "/v1/link", JSONObject(), DeviceCode::from)
    suspend fun pollLink(handle: String): ApiResult<LinkState> = call("GET", "/v1/link?handle=${encode(handle)}", null, LinkState::from)
    suspend fun confirmLink(confirm: LinkConfirm): ApiResult<LinkStatus> =
        call("POST", "/v1/link/confirm", confirm.toJson()) { json -> LinkStatus.Linked.takeIf { json.opt("state") == it.wire } }
    suspend fun getProfile(heldRevision: Long? = null): ApiResult<Profile> = call("GET", "/v1/profile", null) { Profile.from(it, heldRevision) }
    suspend fun putProfile(update: ProfileUpdate): ApiResult<Profile> =
        call("PUT", "/v1/profile", update.toJson()) { Profile.from(it, update.revision) }
    suspend fun getAlerts(cursor: String? = null): ApiResult<AlertsPage> =
        call("GET", "/v1/alerts" + (cursor?.let { "?cursor=${encode(it)}" } ?: ""), null, AlertsPage::from)
    suspend fun getPanel(teamLeague: String? = null, heldRevision: Long? = null): ApiResult<PanelState> =
        call("GET", "/v1/panel" + (teamLeague?.let { "?teamLeague=${encode(it)}" } ?: ""), null) { PanelState.from(it, heldRevision) }
    suspend fun getProvider(eventId: String? = null): ApiResult<ProviderRoute> =
        call("GET", "/v1/providers" + (eventId?.let { "?eventId=${encode(it)}" } ?: ""), null, ProviderRoute::from)
    suspend fun reportRoutingOutcome(report: RoutingOutcomeReport): ApiResult<Unit> = call("POST", "/v1/routing-outcome", report.toJson()) { }
    suspend fun reportInstalledApps(apps: InstalledApps): ApiResult<Unit> = call("POST", "/v1/installed-apps", apps.toJson()) { }

    private suspend fun <T : Any> call(method: String, path: String, body: JSONObject?, decode: (JSONObject) -> T?): ApiResult<T> {
        val response = request(method, path, body)
        if (response.status !in 200..299) return ApiResult(response.status, null, ApiError.from(response.body))
        val value = response.body?.let(decode) ?: throw IllegalArgumentException("Response does not match the API contract")
        return ApiResult(response.status, value, null)
    }

    private fun send(method: String, path: String, payload: ByteArray?): ApiResponse {
        val connection = openConnection(URL(base + path))
        try {
            connection.connectTimeout = TIMEOUT_MS
            connection.readTimeout = if (path.substringBefore('?') == "/v1/alerts") LONG_POLL_READ_MS else TIMEOUT_MS
            connection.instanceFollowRedirects = false
            connection.requestMethod = method
            connection.setRequestProperty("Accept", "application/json")
            if (path.substringBefore('?') !in PUBLIC_PATHS) {
                sessionToken()?.let { connection.setRequestProperty("Authorization", "Bearer $it") }
            }
            if (payload != null) {
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json")
                connection.outputStream.use { it.write(payload) }
            }
            val status = connection.responseCode
            val stream = if (status >= 400) connection.errorStream else connection.inputStream
            return ApiResponse(status, stream?.use { parse(readBounded(it)) })
        } finally {
            connection.disconnect()
        }
    }

    companion object {
        const val MAX_BODY_BYTES = 65_536
        const val TIMEOUT_MS = 10_000
        const val LONG_POLL_READ_MS = 25_000
        const val RETRY_MAX = 3
        const val BACKOFF_BASE_MS = 1_000L
        private val METHODS = setOf("GET", "POST", "PUT")
        private val TRANSIENT = setOf(429, 503)
        private val PUBLIC_PATHS = setOf("/v1/link", "/v1/link/confirm")
        private val LOOPBACK_HOSTS = setOf("127.0.0.1", "localhost")

        private fun encode(value: String): String = URLEncoder.encode(value, "UTF-8")

        private fun readBounded(input: InputStream): String {
            val bytes = input.readNBytesCompat(MAX_BODY_BYTES + 1)
            require(bytes.size <= MAX_BODY_BYTES) { "Response body exceeds 64 KiB" }
            return bytes.toString(Charsets.UTF_8)
        }

        // InputStream.readNBytes is API 33; read at most [limit] bytes by hand for minSdk 25.
        private fun InputStream.readNBytesCompat(limit: Int): ByteArray {
            val out = java.io.ByteArrayOutputStream()
            val buffer = ByteArray(8_192)
            while (out.size() < limit) {
                val read = read(buffer, 0, minOf(buffer.size, limit - out.size()))
                if (read < 0) break
                out.write(buffer, 0, read)
            }
            return out.toByteArray()
        }

        private fun parse(text: String): JSONObject? {
            if (text.isBlank()) return null
            return try {
                JSONObject(text)
            } catch (e: JSONException) {
                throw IllegalArgumentException("Response is not a JSON object", e)
            }
        }
    }
}

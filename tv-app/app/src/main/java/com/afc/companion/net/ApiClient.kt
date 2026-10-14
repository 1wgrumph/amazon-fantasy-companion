package com.afc.companion.net

import java.net.HttpURLConnection
import java.net.URL
import kotlinx.coroutines.delay
import org.json.JSONObject

// AFC-STUB: P2-A01 implements the frozen API contract after this red boundary.
class ApiClient(
    val baseUrl: String,
    val sessionToken: () -> String? = { null },
    val openConnection: (URL) -> HttpURLConnection = { it.openConnection() as HttpURLConnection },
    val backoff: suspend (Long) -> Unit = { delay(it) },
) {
    suspend fun request(method: String, path: String, body: JSONObject? = null): ApiResponse = ApiResponse(0, null)
    suspend fun envelope(body: JSONObject, heldRevision: Long? = null): Envelope? = null
}

data class ApiResponse(val status: Int, val body: JSONObject?)
data class Envelope(
    val schemaVersion: Int,
    val id: String,
    val revision: Long,
    val source: String,
    val updatedAt: String,
    val eventTime: String?,
    val data: JSONObject,
)

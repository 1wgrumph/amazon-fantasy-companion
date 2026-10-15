package com.afc.companion

import com.afc.companion.net.ApiClient
import java.net.HttpURLConnection
import java.util.concurrent.CopyOnWriteArrayList
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized

/** api_timeout=10s; alert_poll_wait+5s=25s; api_retry_max=3; exponential backoff=1,2,4s. */
class ApiPolicyTest {
    @Test fun setsNormalTimeoutsOnRealConnection() = runBlocking {
        assertTimeouts("/v1/profile", 10_000)
    }
    @Test fun setsLongPollReadTimeoutAboveServerWait() = runBlocking {
        assertTimeouts("/v1/alerts?cursor=fixture", 25_000)
    }
    private suspend fun assertTimeouts(path: String, readTimeout: Int) {
        val connections = CopyOnWriteArrayList<HttpURLConnection>()
        LocalApi(listOf(200 to envelopeFixture().toString())).use { server ->
            val result = ApiClient(server.baseUrl, openConnection = { url -> connect(url).also { connections.add(it) } }).request("GET", path)
            assertEquals("Missing behavior: complete HTTP request", 200, result.status)
            assertEquals(1, connections.size)
            assertEquals(10_000, connections.single().connectTimeout)
            assertEquals(readTimeout, connections.single().readTimeout)
        }
    }
    @Test fun opensAndReadsNetworkOffCallingUiThread() = runBlocking {
        val uiThread = Thread.currentThread().id
        val ioThreads = CopyOnWriteArrayList<Long>()
        LocalApi(listOf(200 to envelopeFixture().toString())).use { server ->
            val result = ApiClient(server.baseUrl, openConnection = { url ->
                ioThreads.add(Thread.currentThread().id); ObservedConnection(connect(url), ioThreads)
            }).request("GET", "/v1/profile")
            assertEquals("Missing behavior: request produces a response", 200, result.status)
            assertTrue("Network connection and reads must run away from UI caller", ioThreads.isNotEmpty() && ioThreads.all { it != uiThread })
            assertTrue("Real response-code/body reads must be observed", ioThreads.size >= 3)
        }
    }
    @Test fun rejectsMalformedJsonResponse() {
        LocalApi(listOf(200 to "{")).use { server ->
            assertThrows("Malformed input cannot be accepted", IllegalArgumentException::class.java) {
                runBlocking { ApiClient(server.baseUrl).request("GET", "/v1/profile") }
            }
        }
    }
    @Test fun rejectsResponseOverContract64KiB() {
        LocalApi(listOf(200 to JSONObject().put("padding", "x".repeat(65_536)).toString())).use { server ->
            assertThrows("Oversized input cannot be accepted", IllegalArgumentException::class.java) {
                runBlocking { ApiClient(server.baseUrl).request("GET", "/v1/profile") }
            }
        }
    }
    @Test fun rejectsRequestOverContract64KiBBeforeSending() {
        LocalApi(listOf(201 to "{}")).use { server ->
            assertThrows("Oversized output cannot cross the API boundary", IllegalArgumentException::class.java) {
                runBlocking { ApiClient(server.baseUrl).request("POST", "/v1/link", JSONObject().put("padding", "x".repeat(65_536))) }
            }
            assertTrue(server.requests.isEmpty())
        }
    }
    @Test fun defaultBackoffWaitsAtLeastThePrescribedOneSecond() = runBlocking {
        LocalApi(listOf(503 to "{\"error\":{\"code\":\"unavailable\",\"message\":\"retry\"}}", 200 to envelopeFixture().toString())).use { server ->
            val result = ApiClient(server.baseUrl).request("GET", "/v1/profile")
            assertEquals("Missing behavior: default retry succeeds", 200, result.status)
            assertEquals(2, server.requests.size)
            assertTrue("Default backoff must wait at least 1s; no upper timing bound on a loaded host",
                server.requests[1].atNanos - server.requests[0].atNanos >= 1_000_000_000L)
        }
    }
    @Test fun retriesPutWithTheSameRevisionAndBody() = runBlocking {
        val delays = mutableListOf<Long>()
        val body = JSONObject().put("revision", 4).put("data", JSONObject().put("scoringPreset", "halfPpr"))
        LocalApi(listOf(503 to "{\"error\":{\"code\":\"unavailable\",\"message\":\"retry\"}}", 200 to envelopeFixture(5).toString())).use { server ->
            val result = ApiClient(server.baseUrl, backoff = { delays.add(it) }).request("PUT", "/v1/profile", body)
            assertEquals("Missing behavior: retry an idempotent PUT", 200, result.status)
            assertEquals(listOf(1_000L), delays)
            assertEquals(2, server.requests.size)
            assertTrue(server.requests.all { sameJson(JSONObject(it.body), body) })
        }
    }
}
@RunWith(Parameterized::class)
class ApiRetryTest(private val transientStatus: Int) {
    companion object {
        @JvmStatic @Parameterized.Parameters(name = "transient {0}")
        fun statuses(): List<Array<Any>> = listOf(arrayOf(429), arrayOf(503))
    }
    @Test fun retriesIdempotentGetWithBoundedExponentialBackoff() = runBlocking {
        assertTrue(node("paths", "/v1/profile", "get", "responses").containsKey(transientStatus.toString()))
        val delays = mutableListOf<Long>()
        val error = "{\"error\":{\"code\":\"unavailable\",\"message\":\"retry\"}}"
        val success = envelopeFixture()
        LocalApi(List(3) { transientStatus to error } + (200 to success.toString())).use { server ->
            val result = ApiClient(server.baseUrl, backoff = { delays.add(it) }).request("GET", "/v1/profile")
            assertEquals("Missing behavior: recover on final permitted attempt", 200, result.status)
            assertEquals(listOf(1_000L, 2_000L, 4_000L), delays)
            assertEquals(4, server.requests.size)
            assertTrue(server.requests.all { it.method == "GET" && it.path == "/v1/profile" })
            assertTrue(sameJson(success, result.body))
        }
    }
    @Test fun stopsAfterThreeRetriesAndKeepsStructuredError() = runBlocking {
        val delays = mutableListOf<Long>()
        val error = JSONObject().put("error", JSONObject().put("code", "unavailable").put("message", "retry"))
        LocalApi(listOf(transientStatus to error.toString())).use { server ->
            val result = ApiClient(server.baseUrl, backoff = { delays.add(it) }).request("GET", "/v1/profile")
            assertEquals("Missing behavior: return final contract error", transientStatus, result.status)
            assertEquals(listOf(1_000L, 2_000L, 4_000L), delays)
            assertEquals(4, server.requests.size); assertTrue(sameJson(error, result.body))
        }
    }
}
@RunWith(Parameterized::class)
class ApiNoRetryTest(private val method: String, private val path: String, private val status: Int) {
    companion object {
        @JvmStatic @Parameterized.Parameters(name = "{0} {1} {2}")
        fun cases(): List<Array<Any>> = listOf(
            arrayOf("POST", "/v1/link", 503), arrayOf("POST", "/v1/link/confirm", 503),
            arrayOf("POST", "/v1/routing-outcome", 503), arrayOf("POST", "/v1/installed-apps", 503),
            arrayOf("GET", "/v1/link?handle=fixture", 400), arrayOf("GET", "/v1/profile", 401),
            arrayOf("GET", "/v1/profile", 403), arrayOf("PUT", "/v1/profile", 409),
            arrayOf("POST", "/v1/link/confirm", 410),
        )
    }
    @Test fun returnsPermanentOrNonIdempotentErrorWithoutRetry() = runBlocking {
        assertTrue(node("paths", path.substringBefore('?'), method.lowercase(), "responses").containsKey(status.toString()))
        val delays = mutableListOf<Long>()
        val error = JSONObject().put("error", JSONObject().put("code", "fixture_error").put("message", "safe fixture"))
        LocalApi(listOf(status to error.toString())).use { server ->
            val result = ApiClient(server.baseUrl, backoff = { delays.add(it) }).request(method, path, if (method == "GET") null else JSONObject())
            assertEquals("Missing behavior: preserve contract failure", status, result.status)
            assertEquals(1, server.requests.size); assertTrue(delays.isEmpty())
            assertTrue(sameJson(error, result.body))
        }
    }
}

package com.afc.companion

import com.afc.companion.net.ApiClient
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized

/** CONTRACT-AFC-P2-API: one operation per frozen OpenAPI operation, using a real HTTP peer. */
@RunWith(Parameterized::class)
class ApiOperationsTest(private val method: String, private val path: String, private val status: Int) {
    companion object {
        @JvmStatic @Parameterized.Parameters(name = "{0} {1}")
        fun operations(): List<Array<Any>> = listOf(
            arrayOf("POST", "/v1/link", 201), arrayOf("GET", "/v1/link?handle=fixture", 200),
            arrayOf("POST", "/v1/link/confirm", 200), arrayOf("GET", "/v1/profile", 200),
            arrayOf("PUT", "/v1/profile", 200), arrayOf("GET", "/v1/alerts?cursor=fixture", 200),
            arrayOf("GET", "/v1/panel", 200), arrayOf("GET", "/v1/providers", 200),
            arrayOf("POST", "/v1/routing-outcome", 200), arrayOf("POST", "/v1/installed-apps", 200),
        )
    }
    @Test fun sendsFrozenOperationAndDecodesJson() = runBlocking {
        val operation = node("paths", path.substringBefore('?'), method.lowercase())
        assertTrue("The real OpenAPI response declares this status", node("paths", path.substringBefore('?'), method.lowercase(), "responses").containsKey(status.toString()))
        val token = UUID.randomUUID().toString()
        val protected = !operation.containsKey("security")
        val response = when (path.substringBefore('?')) {
            "/v1/link" -> if (method == "POST") JSONObject().put("code", "ABCD2345").put("expires", "2026-10-14T12:10:00Z").put("handle", "fixture") else JSONObject().put("state", "codePending")
            "/v1/link/confirm" -> JSONObject().put("state", "linked")
            "/v1/profile", "/v1/panel" -> envelopeFixture()
            "/v1/alerts" -> JSONObject().put("alerts", org.json.JSONArray()).put("cursor", "fixture")
            else -> JSONObject()
        }
        val request = when (path.substringBefore('?')) {
            "/v1/link/confirm" -> JSONObject().put("code", "ABCD2345").put("passphrase", "synthetic").put("profileId", "fixture")
            "/v1/profile" -> JSONObject().put("revision", 4).put("data", JSONObject().put("scoringPreset", "halfPpr"))
            "/v1/routing-outcome" -> JSONObject().put("eventId", "fixture").put("outcome", "accessUnknown")
            "/v1/installed-apps" -> JSONObject().put("packages", org.json.JSONArray())
            else -> JSONObject()
        }
        LocalApi(listOf(status to response.toString())).use { server ->
            val result = ApiClient(server.baseUrl, { token }).request(method, path, if (method == "GET") null else request)
            assertEquals("Missing behavior: HTTP status for $method $path", status, result.status)
            assertNotNull("Missing behavior: JSON response", result.body)
            assertTrue(sameJson(response, result.body))
            assertEquals(1, server.requests.size)
            val sent = server.requests.single()
            assertEquals(method, sent.method); assertEquals(path, sent.path)
            assertEquals(if (protected) "Bearer $token" else null, sent.bearer)
            if (method != "GET") assertTrue(sameJson(request, JSONObject(sent.body)))
        }
    }
}

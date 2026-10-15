package com.afc.companion

import java.net.URL
import org.junit.Assert.*
import org.junit.Test

/** Real dependency proof before client scaffolding: the OS-bound HTTP peer produces the corpus. */
class FixtureCalibrationTest {
    @Test fun realHttpPeerProducesOpenApiEnvelopeAndStructuredError() {
        val body = envelopeFixture()
        LocalApi(listOf(200 to body.toString(), 503 to "{\"error\":{\"code\":\"unavailable\",\"message\":\"retry\"}}")).use { server ->
            val first = connect(URL(server.baseUrl + "/v1/profile"))
            try {
                first.connectTimeout = 10_000; first.readTimeout = 10_000
                assertEquals(200, first.responseCode)
                val received = org.json.JSONObject(first.inputStream.bufferedReader().use { it.readText() })
                assertTrue(sameJson(body, received))
                assertTrue((node("components", "schemas", "Envelope")["required"] as List<*>).all { received.has(it.toString()) })
            } finally { first.disconnect() }
            val second = connect(URL(server.baseUrl + "/v1/profile"))
            try {
                second.connectTimeout = 10_000; second.readTimeout = 10_000
                assertEquals(503, second.responseCode)
                val error = org.json.JSONObject(second.errorStream.bufferedReader().use { it.readText() }).getJSONObject("error")
                assertEquals("unavailable", error.getString("code")); assertEquals("retry", error.getString("message"))
            } finally { second.disconnect() }
            assertEquals(2, server.requests.size)
        }
    }
}

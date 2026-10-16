package com.afc.companion

import com.afc.companion.link.LinkFlow
import com.afc.companion.link.LinkPresentation
import com.afc.companion.link.LinkScreen
import com.afc.companion.net.ApiClient
import com.afc.companion.net.DeviceCode
import com.afc.companion.net.Envelope
import com.afc.companion.net.InstalledApps
import com.afc.companion.net.ProfileUpdate
import com.afc.companion.net.RoutingOutcomeReport
import com.afc.companion.net.Settings
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

/** Trust boundary: base URL scheme, body limits, request validation, link flow and shell start. */
class ClientBoundaryTest {
    @Test fun acceptsHttpsAndLoopbackOnly() {
        ApiClient("https://api.example.test/prod/"); ApiClient("http://localhost:8080")
        for (bad in listOf("http://api.example.test", "https://user:pw@api.example.test", "https://api.example.test?x=1", "ftp://api.example.test", "not a url", ""))
            assertThrows(bad, IllegalArgumentException::class.java) { ApiClient(bad) }
    }

    @Test fun acceptsResponseAtExactly64KiBAndEmptyBodyAsNull() {
        val padding = "x".repeat(65_536 - JSONObject().put("p", "").toString().length)
        val exact = JSONObject().put("p", padding)
        assertEquals(65_536, exact.toString().toByteArray().size)
        LocalApi(listOf(200 to exact.toString(), 200 to "")).use { server ->
            runBlocking {
                val client = ApiClient(server.baseUrl)
                assertTrue(sameJson(exact, client.request("GET", "/v1/profile").body))
                assertNull(client.request("GET", "/v1/profile").body)
            }
        }
    }

    @Test fun rejectsUnsupportedMethodOrPathBeforeSending() {
        LocalApi(listOf(200 to "{}")).use { server ->
            val client = ApiClient(server.baseUrl)
            assertThrows(IllegalArgumentException::class.java) { runBlocking { client.request("DELETE", "/v1/profile") } }
            assertThrows(IllegalArgumentException::class.java) { runBlocking { client.request("GET", "/admin") } }
            assertTrue(server.requests.isEmpty())
        }
    }

    @Test fun rejectsArrayResponseAndContractMismatch() {
        LocalApi(listOf(200 to "[]", 201 to "{\"code\":\"bad\"}")).use { server ->
            val client = ApiClient(server.baseUrl)
            assertThrows(IllegalArgumentException::class.java) { runBlocking { client.request("GET", "/v1/profile") } }
            assertThrows(IllegalArgumentException::class.java) { runBlocking { client.issueLinkCode() } }
        }
    }

    @Test fun validatesOutgoingDtos() {
        assertThrows(IllegalArgumentException::class.java) { InstalledApps(List(501) { "a.b$it" }) }
        assertThrows(IllegalArgumentException::class.java) { InstalledApps(listOf("bad package")) }
        assertThrows(IllegalArgumentException::class.java) { RoutingOutcomeReport("", com.afc.companion.net.RoutingOutcome.GameOpened) }
        assertThrows(IllegalArgumentException::class.java) { ProfileUpdate(-1, Settings()) }
        assertNull(DeviceCode.from(JSONObject().put("code", "ABCD2341").put("expires", "2026-10-14T12:10:00Z").put("handle", "h")))
        assertNull(DeviceCode.from(JSONObject().put("code", "ABCD2345").put("expires", "2026-13-14T12:10:00Z").put("handle", "h")))
        assertNotNull(Envelope.from(envelopeFixture().put("updatedAt", "2026-10-14T12:00:00.123+05:30")))
        assertNull(Envelope.from(envelopeFixture().put("eventTime", JSONObject.NULL)))
        assertNull(Envelope.from(envelopeFixture().put("id", "")))
        assertNull(Envelope.from(envelopeFixture().put("data", "{}")))
    }

    @Test fun linkFlowShowsCodeKeepsPollingAndStoresTokenOnce() {
        val token = UUID.randomUUID().toString()
        val replies = listOf(
            201 to JSONObject().put("code", "ABCD2345").put("expires", "2026-10-14T12:10:00Z").put("handle", "h").toString(),
            200 to JSONObject().put("state", "codePending").toString(),
            200 to JSONObject().put("state", "linked").put("sessionToken", token).toString(),
        )
        LocalApi(replies).use { server ->
            val shown = mutableListOf<LinkPresentation>(); val stored = mutableListOf<String>(); val sleeps = mutableListOf<Long>()
            runBlocking { LinkFlow(ApiClient(server.baseUrl), LinkScreen("page"), sleep = { sleeps.add(it) }).run({ shown.add(it) }, { stored.add(it) }) }
            assertEquals(listOf("codePending", "linked"), shown.map { it.state })
            assertEquals("ABCD2345", shown[0].code); assertTrue(shown[1].showProfile)
            assertEquals(listOf(token), stored); assertEquals(listOf(5_000L, 5_000L), sleeps)
            assertTrue(shown.none { it.toString().contains(token) })
        }
    }

    @Test fun linkFlowStopsOnExpiryErrorAndTokenlessLink() {
        val code = 201 to JSONObject().put("code", "ABCD2345").put("expires", "2026-10-14T12:10:00Z").put("handle", "h").toString()
        val cases = mapOf(
            listOf(code, 200 to "{\"state\":\"expired\"}") to "expired",
            listOf(code, 400 to "{\"error\":{\"code\":\"bad\",\"message\":\"m\"}}") to "error",
            listOf(code, 200 to "{\"state\":\"linked\"}") to "error",
            listOf(400 to "{\"error\":{\"code\":\"bad\",\"message\":\"m\"}}") to "error",
        )
        for ((replies, last) in cases) LocalApi(replies).use { server ->
            val shown = mutableListOf<LinkPresentation>(); val stored = mutableListOf<String>()
            runBlocking { LinkFlow(ApiClient(server.baseUrl), LinkScreen(), sleep = {}).run({ shown.add(it) }, { stored.add(it) }) }
            assertEquals(last, shown.last().state); assertTrue(stored.isEmpty()); assertFalse(shown.last().showProfile)
        }
    }

    @Test fun linkScreenRejectsInvalidResponses() {
        assertNull(LinkScreen().present(JSONObject().put("state", "hacked")))
        assertNull(LinkScreen().present(JSONObject().put("code", "short")))
        assertNull(LinkScreen().present(JSONObject().put("state", "linked").put("sessionToken", 7)))
    }

    @Test fun shellStartsAtLinkUntilASessionExistsAndRequiresAConfiguredBackend() {
        val shell = Shell()
        assertEquals(Destination.Link, shell.start(false)); assertEquals(Destination.ProfileSettings, shell.start(true))
        assertNull(shell.client("") { null }); assertNull(shell.client("http://api.example.test") { null })
        assertEquals("https://api.example.test", shell.client("https://api.example.test") { null }!!.baseUrl)
    }
}

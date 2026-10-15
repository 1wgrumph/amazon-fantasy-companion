package com.afc.companion

import com.afc.companion.net.AccessBasis
import com.afc.companion.net.ApiClient
import com.afc.companion.net.InstalledApps
import com.afc.companion.net.LinkConfirm
import com.afc.companion.net.LinkStatus
import com.afc.companion.net.ProfileUpdate
import com.afc.companion.net.RoutingOutcome
import com.afc.companion.net.RoutingOutcomeReport
import com.afc.companion.net.ScoringPreset
import com.afc.companion.net.Settings
import java.util.UUID
import kotlinx.coroutines.runBlocking
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

/** CONTRACT-AFC-P2-API typed operations over a real HTTP peer: request shape and decoded types. */
class TypedOperationsTest {
    private fun <T> serve(status: Int, body: JSONObject, token: String? = null, block: suspend (ApiClient) -> T): Pair<T, RecordedRequest> =
        LocalApi(listOf(status to body.toString())).use { server ->
            val result = runBlocking { block(ApiClient(server.baseUrl, { token })) }
            result to server.requests.single()
        }

    @Test fun issuesAndPollsLinkWithoutBearerAndRedactsToken() {
        val (code, sent) = serve(201, JSONObject().put("code", "ABCD2345").put("expires", "2026-10-14T12:10:00Z").put("handle", "h 1")) { it.issueLinkCode() }
        assertEquals("ABCD2345", code.value!!.code); assertNull(sent.bearer); assertEquals("POST", sent.method)
        val token = UUID.randomUUID().toString()
        val (state, poll) = serve(200, JSONObject().put("state", "linked").put("sessionToken", token), "held") { it.pollLink("h 1") }
        assertEquals("/v1/link?handle=h+1", poll.path); assertNull(poll.bearer)
        assertEquals(LinkStatus.Linked, state.value!!.state); assertEquals(token, state.value!!.sessionToken)
        assertFalse(state.value.toString().contains(token))
    }

    @Test fun confirmSendsAllFieldsOnceAndHidesPassphrase() {
        val confirm = LinkConfirm("ABCD2345", "synthetic", "fixture")
        val (result, sent) = serve(200, JSONObject().put("state", "linked")) { it.confirmLink(confirm) }
        assertEquals(LinkStatus.Linked, result.value)
        assertTrue(sameJson(confirm.toJson(), JSONObject(sent.body)))
        assertFalse(confirm.toString().contains("synthetic"))
    }

    @Test fun profileReadAndWriteCarryScoringPresetAndRevision() {
        val stored = envelopeFixture(5).put("data", JSONObject().put("scoringPreset", "ppr").put("voice", false))
        val token = UUID.randomUUID().toString()
        val (read, get) = serve(200, stored, token) { it.getProfile(4) }
        assertEquals("Bearer $token", get.bearer)
        assertEquals(ScoringPreset.Ppr, read.value!!.settings.scoringPreset); assertEquals(5L, read.value!!.envelope.revision)
        val update = ProfileUpdate(5, Settings(ScoringPreset.HalfPpr, JSONObject().put("voice", false)), "fixture")
        val (written, put) = serve(200, envelopeFixture(6)) { it.putProfile(update) }
        assertEquals("PUT", put.method); assertEquals(6L, written.value!!.envelope.revision)
        assertTrue(sameJson(JSONObject().put("revision", 5).put("profileId", "fixture")
            .put("data", JSONObject().put("voice", false).put("scoringPreset", "halfPpr")), JSONObject(put.body)))
    }

    @Test fun defaultsScoringPresetToHalfPprAndRejectsUnknownSettings() {
        assertEquals(ScoringPreset.HalfPpr, Settings.from(JSONObject())!!.scoringPreset)
        assertNull(Settings.from(JSONObject().put("chat", true)))
        assertNull(Settings.from(JSONObject().put("scoringPreset", "standard")))
        assertThrows(IllegalArgumentException::class.java) { Settings(controls = JSONObject().put("chat", true)) }
    }

    @Test fun alertsCarryRouteAndAccessBasisAndUnknownWhenAbsent() {
        val route = JSONObject().put("provider", "fixture").put("channel", JSONObject.NULL).put("accessBasis", "verified")
        val alerts = JSONArray().put(envelopeFixture().put("data", JSONObject().put("route", route))).put(envelopeFixture())
        val (page, sent) = serve(200, JSONObject().put("alerts", alerts).put("cursor", "next")) { it.getAlerts("c/1") }
        assertEquals("/v1/alerts?cursor=c%2F1", sent.path)
        assertEquals("next", page.value!!.cursor)
        assertEquals(AccessBasis.Verified, page.value!!.alerts[0].accessBasis); assertEquals("fixture", page.value!!.alerts[0].route!!.provider)
        assertEquals(AccessBasis.Unknown, page.value!!.alerts[1].accessBasis); assertNull(page.value!!.alerts[1].route)
    }

    @Test fun oneInvalidAlertRejectsTheWholePage() {
        val alerts = JSONArray().put(envelopeFixture()).put(envelopeFixture().put("source", "unverified"))
        assertThrows(IllegalArgumentException::class.java) {
            serve(200, JSONObject().put("alerts", alerts).put("cursor", "next")) { it.getAlerts() }
        }
    }

    @Test fun panelAndProviderDecode() {
        val (panel, p) = serve(200, envelopeFixture(7)) { it.getPanel("team 1", 6) }
        assertEquals("/v1/panel?teamLeague=team+1", p.path); assertEquals(7L, panel.value!!.envelope.revision)
        val (route, r) = serve(200, JSONObject().put("accessBasis", "customerConfirmed").put("route", JSONObject().put("uri", "x"))) { it.getProvider("e1") }
        assertEquals("/v1/providers?eventId=e1", r.path)
        assertEquals(AccessBasis.CustomerConfirmed, route.value!!.accessBasis); assertNull(route.value!!.provider)
        assertThrows(IllegalArgumentException::class.java) { serve(200, JSONObject().put("accessBasis", "assumed")) { it.getProvider() } }
    }

    @Test fun reportsOutcomeAndInstalledApps() {
        val (outcome, o) = serve(200, JSONObject()) { it.reportRoutingOutcome(RoutingOutcomeReport("e1", RoutingOutcome.AppAbsent, "fixture")) }
        assertEquals(200, outcome.status)
        assertTrue(sameJson(JSONObject().put("eventId", "e1").put("outcome", "appAbsent").put("profileId", "fixture"), JSONObject(o.body)))
        val (apps, a) = serve(200, JSONObject()) { it.reportInstalledApps(InstalledApps(listOf("com.example.tv"))) }
        assertEquals(200, apps.status)
        assertTrue(sameJson(JSONObject().put("packages", JSONArray().put("com.example.tv")), JSONObject(a.body)))
    }

    @Test fun contractErrorsKeepStatusAndStructuredError() {
        val error = JSONObject().put("error", JSONObject().put("code", "stale").put("message", "safe"))
        val (result, _) = serve(409, error) { it.putProfile(ProfileUpdate(1, Settings())) }
        assertEquals(409, result.status); assertNull(result.value)
        assertEquals("stale", result.error!!.code); assertEquals("safe", result.error!!.message)
    }

    @Test fun enumsMatchTheFrozenContract() {
        val schemas = node("components", "schemas")
        @Suppress("UNCHECKED_CAST") fun enumOf(vararg keys: String) = keys.fold(schemas as Map<String, Any>) { m, k -> m[k] as Map<String, Any> }["enum"] as List<*>
        assertEquals(enumOf("RoutingOutcome"), RoutingOutcome.entries.map { it.wire })
        assertEquals(enumOf("LinkState", "properties", "state"), LinkStatus.entries.map { it.wire })
        assertEquals(enumOf("Settings", "properties", "scoringPreset"), ScoringPreset.entries.map { it.wire })
        assertEquals((node("paths", "/v1/providers", "get", "responses", "200", "content", "application/json", "schema", "properties", "accessBasis")["enum"] as List<*>),
            AccessBasis.entries.map { it.wire })
        @Suppress("UNCHECKED_CAST")
        assertEquals((schemas["Settings"] as Map<String, Any>).let { (it["properties"] as Map<String, Any>).keys - "scoringPreset" }, Settings.CONTROLS)
    }
}

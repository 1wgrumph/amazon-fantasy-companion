package com.afc.companion.alerts

import com.afc.companion.net.Alert
import com.afc.companion.net.Envelope
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** G4 regression: payloads in the exact landed backend (B05) shape. See contract-check-G4. */
class AlertServerContractTest {

    private fun serverAlert(
        type: String,
        eventId: String,
        starters: List<String> = listOf("Sample Receiver"),
        commentary: String? = "Red-zone chance: ball at the 9, inside the 20. Score 24-27.",
    ): Alert {
        val starterArray = JSONArray(starters.map { name ->
            JSONObject().put("athlete_id", "9000001").put("name", name).put("team", "PHI").put("slot", "WR")
        })
        val data = JSONObject()
            .put("alertType", type)
            .put(
                "triggerContext", JSONObject()
                    .put("gameId", "401999001").put("eventId", eventId).put("source", "live")
                    .put("score", JSONObject().put("away", 24).put("home", 27))
                    .put("starters", starterArray)
                    .put("alertTypes", JSONArray(listOf(type))).put("basis", "profile-assumption"),
            )
            .put("commentary", commentary ?: JSONObject.NULL)
            .put(
                "route", JSONObject().put("provider", JSONObject.NULL).put("channel", JSONObject.NULL)
                    .put("route", JSONObject.NULL).put("accessBasis", "unknown")
                    .put("inputs", JSONObject().put("installed", false).put("localMarket", JSONObject.NULL)),
            )
        val envelopeJson = JSONObject().put("schemaVersion", 1).put("id", "2026-10-15T00:19:30Z#$eventId")
            .put("revision", 1).put("source", "live").put("updatedAt", "2026-10-15T00:19:30Z").put("data", data)
        return checkNotNull(Envelope.from(envelopeJson)?.let(Alert::from)) { "server fixture must decode" }
    }

    @Test fun serverRedZonePayloadIsPresented() {
        val text = AlertPresenter.text(serverAlert("RedZone", "401999001770"))
        assertNotNull("server RedZone must not be suppressed", text)
        assertEquals("Red-zone alert", text!!.headline)
        assertTrue("starter in context: ${text.context}", "Sample Receiver" in text.context)
        assertFalse("no fabricated matchup: ${text.context}", "—" in text.context)
    }

    @Test fun serverPlayerScorePayloadIsPresented() {
        val text = AlertPresenter.text(serverAlert("PlayerScore", "401999001771", commentary = "A score on a play listing your starter. Score 24-27."))
        assertNotNull(text); assertEquals("Score update", text!!.headline)
        assertTrue("Sample Receiver" in text.context)
    }

    @Test fun serverCloseGamePayloadIsPresented() {
        val text = AlertPresenter.text(serverAlert("CloseGame", "401999001772", commentary = "Close game in period 4: margin 3. Score 24-27."))
        assertNotNull(text); assertEquals("Close game alert", text!!.headline)
        assertTrue("Sample Receiver" in text.context)
    }

    @Test fun severalStartersAreAllShown() {
        val text = AlertPresenter.text(serverAlert("RedZone", "401999001770", starters = listOf("Sample Receiver", "Sample Runner")))
        assertNotNull(text)
        assertTrue("both starters: ${text!!.context}", "Sample Receiver" in text.context && "Sample Runner" in text.context)
    }

    @Test fun emptyStartersCorrectionIsPresentedWithoutFabrication() {
        val text = AlertPresenter.text(serverAlert("PlayerScore", "401999001771", starters = emptyList()))
        assertNotNull("correction must still present", text)
        assertFalse("no player claimed: ${text!!.context}", "Sample Receiver" in text.context)
        assertFalse("no fabricated matchup: ${text.context}", "—" in text.context)
        assertEquals("empty starters show no context wording", "", text.context)
    }

    @Test fun unsafeStarterNameIsNotRendered() {
        val text = AlertPresenter.text(serverAlert("RedZone", "401999001770", starters = listOf("Sample Receiver is on the field and will score")))
        assertEquals("unsafe starter suppresses presentation", null, text)
    }

    @Test fun watchEventIdComesFromTriggerContext() {
        assertEquals("401999001770", AlertNotifier.watchEventId(serverAlert("RedZone", "401999001770")))
    }

    private fun triggerOf(alert: Alert): JSONObject = alert.envelope.data.getJSONObject("triggerContext")

    // F1: the joined starter context is bounded, with the remainder counted, not spelled out.
    @Test fun manyLongStarterNamesAreBoundedWithRemainderCount() {
        val starters = (0 until 8).map { "Starter$it " + "a".repeat(65) }
        val text = AlertPresenter.text(serverAlert("RedZone", "401999001770", starters = starters))
        assertNotNull(text)
        assertTrue("context bounded (${text!!.context.length}): '${text.context}'", text.context.length <= 80)
        assertTrue("remainder counted: '${text.context}'", text.context.contains("more"))
    }

    // F2: an explicit null matchup is absent, not a suppression.
    @Test fun nullMatchupIsTreatedAsAbsent() {
        val alert = serverAlert("RedZone", "401999001770")
        triggerOf(alert).put("matchup", JSONObject.NULL)
        val text = AlertPresenter.text(alert)
        assertNotNull("null matchup must not suppress the alert", text)
        assertTrue("Sample Receiver" in text!!.context)
    }

    // F4: empty/blank trigger IDs fall back to the legacy key; the trigger key wins when both are valid.
    @Test fun watchEventIdFallsBackToLegacyDataKey() {
        val alert = serverAlert("RedZone", "401999001770")
        triggerOf(alert).remove("eventId")
        alert.envelope.data.put("eventId", "legacy-event")
        assertEquals("legacy-event", AlertNotifier.watchEventId(alert))
    }

    @Test fun watchEventIdPrefersTriggerContextOverLegacyKey() {
        val alert = serverAlert("RedZone", "401999001770")
        alert.envelope.data.put("eventId", "legacy-event")
        assertEquals("401999001770", AlertNotifier.watchEventId(alert))
    }

    @Test fun emptyOrBlankWatchEventIdFallsBackOrIsRejected() {
        val empty = serverAlert("RedZone", ""); empty.envelope.data.put("eventId", "legacy-event")
        assertEquals("legacy-event", AlertNotifier.watchEventId(empty))
        val blank = serverAlert("RedZone", "   "); blank.envelope.data.put("eventId", "legacy-event")
        assertEquals("legacy-event", AlertNotifier.watchEventId(blank))
        assertEquals(null, AlertNotifier.watchEventId(serverAlert("RedZone", "")))
    }

    // F5: a safety claim split across two starter names still suppresses the alert.
    @Test fun claimSplitAcrossStarterNamesIsNotRendered() {
        val text = AlertPresenter.text(serverAlert("RedZone", "401999001770", starters = listOf("Sample Will", "Score Sample")))
        assertEquals("split claim suppresses presentation", null, text)
    }

    // F5: one unsafe starter among several suppresses the whole alert, never just that starter.
    @Test fun oneUnsafeStarterAmongSeveralSuppressesTheWholeAlert() {
        val text = AlertPresenter.text(
            serverAlert("RedZone", "401999001770", starters = listOf("Sample Receiver", "Sample Runner will score")),
        )
        assertEquals(null, text)
    }

    // F5: a starter that is not an object, or has no name, suppresses the alert.
    @Test fun malformedStarterIsNotRendered() {
        val notObject = serverAlert("RedZone", "401999001770")
        triggerOf(notObject).put("starters", JSONArray(listOf("Sample Receiver")))
        assertEquals(null, AlertPresenter.text(notObject))
        val noName = serverAlert("RedZone", "401999001770")
        triggerOf(noName).put("starters", JSONArray().put(JSONObject().put("athlete_id", "9000001")))
        assertEquals(null, AlertPresenter.text(noName))
    }

    // F5: starters win over a legacy player field sent alongside them.
    @Test fun startersWinOverLegacyPlayerField() {
        val alert = serverAlert("RedZone", "401999001770", starters = listOf("Starter Name"))
        triggerOf(alert).put("player", "Legacy Player")
        val text = AlertPresenter.text(alert)
        assertNotNull(text)
        assertTrue("Starter Name" in text!!.context)
        assertFalse("legacy player not shown: '${text.context}'", "Legacy Player" in text.context)
    }
}

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
    }

    @Test fun unsafeStarterNameIsNotRendered() {
        val text = AlertPresenter.text(serverAlert("RedZone", "401999001770", starters = listOf("Sample Receiver is on the field and will score")))
        assertEquals("unsafe starter suppresses presentation", null, text)
    }

    @Test fun watchEventIdComesFromTriggerContext() {
        assertEquals("401999001770", AlertNotifier.watchEventId(serverAlert("RedZone", "401999001770")))
    }
}

package com.afc.companion.panel

import com.afc.companion.net.Alert
import com.afc.companion.net.Envelope
import java.io.File
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

/** F01: current committed envelopes and the existing decoded own-lineup authority. No shared resources. */
class AlertCardMappingTest {
    private val now = System.currentTimeMillis()
    private fun json() = JSONObject(File(System.getProperty("afc.repoRoot"), "backend/fixtures/alerts/player-score.json").readText())
        .getJSONArray("alerts").getJSONObject(0)
    private fun alert(json: JSONObject = json()) = requireNotNull(Alert.from(requireNotNull(Envelope.from(json))))
    private fun snapshot() = snap(rows = listOf(prow("9000001", 6.5).let {
        it.copy(points = it.points.copy(asOfMs = now))
    }))

    @Test fun committedEnvelopeUsesMatchingPanelValueSportAndEvent() {
        val notice = requireNotNull(alertCardNotice(alert(), snapshot()))
        assertEquals(6.5, notice.value, 0.0)
        assertEquals("NFL", notice.sport)
        assertEquals("401999001771", notice.watchEventId)
    }
    @Test fun untaggedNflSnapshotUsesItsScoringBasisForAlertSport() {
        val panel = snapshot().copy(sport = null)
        val notice = requireNotNull(alertCardNotice(alert(), panel))
        assertEquals("NFL", notice.sport)
        assertEquals(6.5, notice.value, 0.0)
        val declared = json().apply { getJSONObject("data").getJSONObject("triggerContext").put("sport", "nfl") }
        assertEquals("NFL", requireNotNull(alertCardNotice(alert(declared), panel)).sport)
    }

    @Test fun deployedSyntheticAlertEnvelopesUseMatchingFreshPanelAuthority() {
        for ((sport, basis) in listOf("nfl" to "halfPpr", "nba" to "nbaPoints")) {
            val wire = JSONObject(File(System.getProperty("afc.repoRoot"),
                "tv-app/app/src/androidTest/assets/alert-e2e/$sport-fire-e1.json").readText())
            val trigger = wire.getJSONObject("data").getJSONObject("triggerContext")
            assertFalse("real alert has no sport", trigger.has("sport"))
            val starter = trigger.getJSONArray("starters").getJSONObject(0)
            assertFalse("real alert has no inline points", starter.has("points"))
            val data = panelData(rows = listOf(row(starter.getString("athlete_id"), starter.getString("name"),
                value(20.0, asOf = java.time.Instant.now().toString()))), basis = basis)
            if (sport == "nba") data.put("sport", "nba")
            val panel = requireNotNull(decodePanel(state(data), nbaEnabled = true))
            if (sport == "nfl") assertNull(panel.sport)
            val notice = requireNotNull(alertCardNotice(alert(wire), panel))
            assertEquals(sport.uppercase(), notice.sport)
            assertEquals(20.0, notice.value, 0.0)
            assertEquals(if (sport == "nfl") "Runner 20" else "Guard 20", AlertCardText.label(notice.player, notice.value))
            assertNull("same exact envelope without fresh points must still fail closed", alertCardNotice(alert(wire),
                panel.copy(rows = panel.rows.map { it.copy(points = it.points.copy(asOfMs = now - 60_001)) })))
        }
    }

    @Test fun optionalBackendFieldsWorkWithoutAnyPanel() {
        val json = json()
        json.getJSONObject("data").getJSONObject("triggerContext").apply {
            put("sport", "nba")
            getJSONArray("starters").getJSONObject(0).put("shortName", "Guard").put("points", 20.0)
        }
        val notice = requireNotNull(alertCardNotice(alert(json), null))
        assertEquals("Guard 20", AlertCardText.label(notice.player, notice.value))
        assertEquals("NBA", notice.sport)
    }
    @Test fun absentOrMismatchedAuthorityNeverCreatesANameOnlyCard() {
        assertNull("missing panel must remain an explicit unresolved notice", alertCardNotice(alert(), null))
        assertNull("different starter cannot supply a number", alertCardNotice(alert(), snapshot().copy(rows = listOf(prow("other", 9.0)))))
        val json = json()
        json.getJSONObject("data").getJSONObject("triggerContext").put("sport", "nba")
        assertNull("NFL points must not be relabeled as NBA", alertCardNotice(alert(json), snapshot()))
    }
    @Test fun staleAndUndatedPanelPointsCannotBePresentedAsCurrent() {
        val panel = snapshot()
        for (asOf in listOf(now - 60_001, null)) {
            assertNull(alertCardNotice(alert(), panel.copy(rows = panel.rows.map { it.copy(points = it.points.copy(asOfMs = asOf)) })))
        }
    }
}

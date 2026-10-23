package com.afc.companion.panel

import com.afc.companion.alerts.AlertNotifier
import com.afc.companion.alerts.AlertPresenter
import com.afc.companion.net.Alert
import com.afc.companion.net.Envelope
import java.io.File
import kotlin.math.ceil
import kotlin.math.floor
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertSame
import org.junit.Assert.assertTrue
import org.junit.Test

/** Side-panel owner contract: pure window lifecycle; data stays in the existing PanelController. */
class OverlayControllerTest {
    @Test fun deniedShowReturnsPermissionNeededAndRoutesWithoutAddingAWindow() {
        val h = OverlayHarness(permitted = false)
        assertEquals("PermissionNeeded", h.call("show").toString())
        assertEquals(1, h.permissionRequests)
        assertEquals(0, h.added)
        assertEquals(0, h.removed)
        assertFalse(h.panel.visible)
        assertFalse("a denied overlay does not start panel fetching", h.panel.shouldFetch(0))
    }

    @Test fun showRechecksPermissionAfterTheUserGrantsIt() {
        val h = OverlayHarness(permitted = false)
        assertEquals("PermissionNeeded", h.call("show").toString())
        h.permitted = true
        assertEquals("Shown", h.call("show").toString())
        assertEquals(1, h.added)
        assertEquals(1, h.permissionRequests)
        assertTrue(h.panel.visible)
    }

    @Test fun repeatedShowAddsExactlyOneWindow() {
        val h = OverlayHarness()
        repeat(3) { assertEquals("Shown", h.call("show").toString()) }
        assertEquals(1, h.added)
        assertEquals(0, h.removed)
        assertEquals(0, h.permissionRequests)
    }

    @Test fun repeatedHideRemovesExactlyOneWindowAndStopsRefresh() {
        val h = OverlayHarness()
        assertEquals("Hidden", h.call("hide").toString())
        assertEquals(0, h.removed)
        h.call("show")
        assertTrue(h.panel.shouldFetch(0))
        h.panel.onFetched(snap(), 0)
        repeat(3) { assertEquals("Hidden", h.call("hide").toString()) }
        assertEquals(1, h.removed)
        assertFalse(h.panel.visible)
        assertFalse(h.panel.shouldFetch(30_000))
        h.call("show")
        assertEquals(2, h.added)
        assertTrue("show reuses the panel's immediate refresh", h.panel.shouldFetch(30_001))
    }

    @Test fun toggleShowsHidesAndShowsWithoutDuplicateWindows() {
        val h = OverlayHarness()
        assertEquals("Shown", h.call("toggle").toString())
        assertEquals("Hidden", h.call("toggle").toString())
        assertEquals("Shown", h.call("toggle").toString())
        assertEquals(2, h.added)
        assertEquals(1, h.removed)
        assertTrue(h.panel.visible)
    }

    @Test fun deniedToggleUsesTheSamePermissionPathAsShow() {
        val h = OverlayHarness(permitted = false)
        assertEquals("PermissionNeeded", h.call("toggle").toString())
        assertEquals(1, h.permissionRequests)
        assertEquals(0, h.added)
        assertFalse(h.panel.visible)
    }

    @Test fun overlayUsesTheSameSnapshotAndFormattingForNflAndNba() {
        for ((sport, basis) in listOf("nfl" to "halfPpr", "nba" to "nbaPoints")) {
            val h = OverlayHarness()
            h.call("show")
            val shared = h.sharedPanel()
            assertSame("there is one panel state source, not an overlay copy", h.panel, shared)
            val snapshot = checkNotNull(decodePanel(state(panelData(basis = basis).put("sport", sport)), nbaEnabled = true))
            h.panel.onFetched(snapshot, AS_OF_MS)
            assertSame(snapshot, shared.snapshot)
            assertEquals(snapshot.rows.map { it.name }, shared.snapshot!!.rows.map { it.name })
            for (now in listOf(AS_OF_MS, AS_OF_MS + 60_000)) {
                assertEquals(snapshot.rows.map { PanelText.value(it.points, now) }, shared.snapshot!!.rows.map { PanelText.value(it.points, now) })
                assertEquals(PanelText.value(snapshot.teamTotal, now), PanelText.value(shared.snapshot!!.teamTotal, now))
                assertEquals(PanelText.header(snapshot), PanelText.header(shared.snapshot!!))
            }
            assertTrue(PanelText.header(shared.snapshot!!).startsWith(sport.uppercase()))
            assertTrue(PanelText.value(shared.snapshot!!.rows.first().points, AS_OF_MS + 60_000).contains("stale"))
            assertEquals("Unavailable", PanelText.value(shared.snapshot!!.rows.last().points, AS_OF_MS))
            val next = snapshot.copy(revision = snapshot.revision + 1, teamTotal = snapshot.teamTotal.copy(value = 99.0))
            h.panel.onFetched(next, AS_OF_MS + 30_000)
            assertSame("later scores reach the overlay too", next, shared.snapshot)
        }
    }

    @Test fun arrivingNflAlertIsShownWithItsTitleAndWatchReference() {
        assertArrivingAlert(alertFixture("red-zone"))
    }

    @Test fun arrivingNbaScoreAlertIsShownWithItsTitleAndWatchReference() {
        // NBA uses the same PlayerScore wire contract; starter fields come from test_nba_sport_toggle.py.
        val nba = alertFixture("player-score")
        nba.getJSONObject("data").getJSONObject("triggerContext").apply {
            remove("matchup")
            put("starters", JSONArray().put(JSONObject().put("athlete_id", "9100001").put("name", "Sample Guard").put("team", "SHO").put("slot", "PG")))
        }
        assertArrivingAlert(nba)
    }

    private fun alertFixture(name: String): JSONObject = JSONObject(
        File(System.getProperty("afc.repoRoot"), "backend/fixtures/alerts/$name.json").readText(),
    ).getJSONArray("alerts").getJSONObject(0)

    private fun assertArrivingAlert(json: JSONObject) {
        val alert = checkNotNull(Envelope.from(json)?.let(Alert::from))
        val expectedTitle = checkNotNull(AlertPresenter.text(alert)).headline
        val eventId = checkNotNull(AlertNotifier.watchEventId(alert))
        val h = OverlayHarness()
        h.call("show")
        h.panel.onAlerts(emptyList())
        assertTrue(h.sharedPanel().panelAlerts.isEmpty())
        h.panel.onAlerts(panelAlerts(listOf(alert)))
        val shown = h.sharedPanel().panelAlerts.single()
        assertEquals(expectedTitle, shown.text.headline)
        assertEquals(alert.envelope.id, shown.id)
        assertTrue("Watch retains the alert identity, resolved via AlertInbox.find", shown.watchable)
        // The sport tab strip is on top; Watch is the next element down.
        h.sharedPanel().perform(PanelAction.FocusNext, 0)
        val watch = h.sharedPanel().select(confirmSwitch = false)
        assertEquals(AlertCommand.Watch(alert.envelope.id), watch)
        val referenced = listOf(alert).single { it.envelope.id == (watch as AlertCommand.Watch).alertId }
        assertEquals(eventId, AlertNotifier.watchEventId(referenced))
        assertEquals(1, h.added)
    }

    @Test fun geometryFitsOneSideWithinThirtyPercentAndTheFivePercentSafeZone() {
        for ((width, height) in listOf(1920 to 1080, 1280 to 720, 3840 to 2160, 1919 to 1079)) {
            val box = overlayBox(width, height)
            val safeLeft = ceil(width * 0.05).toInt()
            val safeTop = ceil(height * 0.05).toInt()
            val safeRight = floor(width * 0.95).toInt()
            val safeBottom = floor(height * 0.95).toInt()
            assertTrue("$width x $height: compact positive width", box.width > 0 && box.width <= floor(width * 0.30).toInt())
            assertTrue("$width x $height: positive height", box.height > 0)
            assertTrue("left edge in safe zone", box.left >= safeLeft)
            assertTrue("right edge in safe zone", box.right <= safeRight)
            assertTrue("top edge in safe zone", box.top >= safeTop)
            assertTrue("bottom edge in safe zone", box.bottom <= safeBottom)
            assertTrue("anchored to either safe side", box.left == safeLeft || box.right == safeRight)
        }
    }
}

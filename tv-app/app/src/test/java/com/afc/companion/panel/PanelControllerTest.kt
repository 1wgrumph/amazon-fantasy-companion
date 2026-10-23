package com.afc.companion.panel

import android.view.KeyEvent
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * AFC-PR-042/-043/-044/-061/-062: remote show/hide and team/league switch, every element focusable, refresh on show
 * and every panel_refresh (30 s) while visible, changed-row updates only, hidden panel suspends, bounded state.
 */
class PanelControllerTest {
    private val other = "league-b/team-2"

    /** Keys a Fire TV remote delivers to an app (HOME and the voice key are not delivered). */
    private val remoteKeys = setOf(
        KeyEvent.KEYCODE_DPAD_UP, KeyEvent.KEYCODE_DPAD_DOWN, KeyEvent.KEYCODE_DPAD_LEFT, KeyEvent.KEYCODE_DPAD_RIGHT,
        KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_BACK, KeyEvent.KEYCODE_MENU, KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE,
        KeyEvent.KEYCODE_MEDIA_REWIND, KeyEvent.KEYCODE_MEDIA_FAST_FORWARD,
    )

    private fun controller(visible: Boolean = true) = PanelController(listOf(TL, other), TL, visible)

    private fun keyFor(c: PanelController, action: PanelAction): Int {
        val key = c.bindings().entries.firstOrNull { it.value == action }?.key
        assertNotNull("Missing behavior: $action is bound to a remote key", key)
        return key!!
    }

    private fun loaded(c: PanelController = controller(), s: PanelSnapshot = snap()): PanelController {
        assertTrue("Missing behavior: a visible panel fetches", c.shouldFetch(0))
        c.onFetched(s, 0)
        assertNotNull("Missing behavior: a fetched snapshot is held", c.snapshot)
        return c
    }

    @Test fun initialStateReflectsTheProfileSettings() {
        val c = controller(visible = true)
        assertTrue("visible per panel prefs", c.visible)
        assertEquals("team/league per profile", TL, c.teamLeague)
        assertFalse("hidden per panel prefs", controller(visible = false).visible)
    }

    @Test fun everyPanelOperationIsBoundToAFireTvRemoteKey() {
        val c = controller()
        for (action in PanelAction.entries) {
            val key = keyFor(c, action)
            assertTrue("$action key $key is a Fire TV remote key", key in remoteKeys)
        }
    }

    @Test fun remoteTogglesVisibility() {
        val c = controller()
        val toggle = keyFor(c, PanelAction.ToggleVisibility)
        assertTrue("toggle key is consumed", c.onKey(toggle, 0))
        assertFalse("remote hides the panel", c.visible)
        assertTrue("toggle key is consumed while hidden", c.onKey(toggle, 1))
        assertTrue("remote shows the panel", c.visible)
    }

    @Test fun remoteSwitchesTeamLeagueAndCyclesBack() {
        val c = loaded()
        assertTrue(c.onKey(keyFor(c, PanelAction.NextTeamLeague), 1_000))
        assertEquals(other, c.teamLeague)
        assertNull("the old team's rows are not shown under the new team", c.snapshot)
        assertTrue("a switch fetches immediately", c.shouldFetch(1_000))
        assertTrue(c.onKey(keyFor(c, PanelAction.NextTeamLeague), 2_000))
        assertEquals(TL, c.teamLeague)
    }

    @Test fun pairsListedByThePanelJoinTheSwitchAndCycle() {
        val nba = "demo-nba/cle-phi-tonight"
        val nfl = "demo-nfl/ne-chi-tonight"
        val c = PanelController(listOf(nba), nba, true)
        assertFalse("one known pair: nothing to switch to yet", c.canSwitchTeamLeague)
        c.onFetched(snap(teamLeague = nba).copy(teamLeagues = listOf(nba, nfl)), 0)
        assertTrue(c.canSwitchTeamLeague)
        c.perform(PanelAction.NextTeamLeague, 1_000)
        assertEquals(nfl, c.teamLeague)
        c.onFetched(snap(teamLeague = nfl).copy(teamLeagues = listOf(nba, nfl)), 1_000)
        c.perform(PanelAction.NextTeamLeague, 2_000)
        assertEquals(nba, c.teamLeague)
    }

    @Test fun lateResponseForTheOldTeamIsDiscarded() {
        val c = loaded()
        c.perform(PanelAction.NextTeamLeague, 1_000)
        assertEquals(PanelDelta.NONE, c.onFetched(snap(revision = 8, teamLeague = TL), 1_100))
        assertNull("a response for another team/league is never shown", c.snapshot)
        val delta = c.onFetched(snap(teamLeague = other), 1_200)
        assertEquals(other, c.snapshot?.teamLeague)
        assertEquals(setOf("p-11", "p-23", "p-31"), delta.changedRows)
    }

    @Test fun cycleFollowsTheBackendOrderLiveGamesFirst() {
        val c = PanelController(listOf("l/done"), "l/done", true)
        c.onFetched(snap(teamLeague = "l/done").copy(teamLeagues = listOf("l/live", "l/later", "l/done")), 0)
        c.perform(PanelAction.NextTeamLeague, 0)
        assertEquals("double-tap goes to the live game", "l/live", c.teamLeague)
    }

    @Test fun everyElementIsFocusableAndReachableByDpad() {
        val c = loaded()
        // The total sits above the rows, which are in points order (owner design, 2026-10-23).
        val expected = listOf(FocusTarget.TeamLeagueSwitch, FocusTarget.Total, FocusTarget.Row("p-11"), FocusTarget.Row("p-31"),
            FocusTarget.Row("p-23"))
        assertEquals(expected, c.focusTargets())
        assertEquals("focus starts on the first element", expected.first(), c.focused)
        val down = keyFor(c, PanelAction.FocusNext)
        val visited = mutableListOf(c.focused)
        repeat(expected.size - 1) { assertTrue(c.onKey(down, 0)); visited += c.focused }
        assertEquals("D-pad reaches every element in order", expected, visited)
        c.onKey(down, 0)
        assertEquals("focus stays on the last element", FocusTarget.Row("p-23"), c.focused)
        c.onKey(keyFor(c, PanelAction.FocusPrevious), 0)
        assertEquals(FocusTarget.Row("p-31"), c.focused)
    }

    @Test fun focusMovesOffARemovedRow() {
        val c = loaded()
        repeat(3) { c.perform(PanelAction.FocusNext, 0) }
        assertEquals(FocusTarget.Row("p-31"), c.focused)
        c.onFetched(snap(revision = 8, rows = listOf(prow("p-11", 12.3), prow("p-23", -1.5))), 1)
        assertTrue("focus never points at a missing element: ${c.focused}", c.focused in c.focusTargets())
        assertNotNull(c.focused)
    }

    @Test fun hiddenPanelLeavesNavigationKeysToTheShell() {
        val c = loaded()
        c.perform(PanelAction.ToggleVisibility, 0)
        assertFalse("Missing behavior: toggle hides", c.visible)
        assertFalse("a hidden panel does not consume D-pad focus keys", c.onKey(keyFor(c, PanelAction.FocusNext), 1))
    }

    @Test fun refreshesOnShowAndEveryThirtySecondsWhileVisible() {
        val c = loaded()
        assertFalse("not before panel_refresh", c.shouldFetch(29_999))
        assertTrue("at panel_refresh", c.shouldFetch(30_000))
        c.onFetched(snap(revision = 8), 30_000)
        c.perform(PanelAction.ToggleVisibility, 40_000)
        assertFalse(c.visible)
        assertFalse("a hidden panel never fetches", c.shouldFetch(100_000))
        c.perform(PanelAction.ToggleVisibility, 100_000)
        assertTrue("show fetches immediately", c.shouldFetch(100_000))
    }

    @Test fun hiddenPanelSuspendsUpdatesAndRefreshesOnShow() {
        val c = loaded()
        c.perform(PanelAction.ToggleVisibility, 1_000)
        assertEquals("updates are not applied while hidden", PanelDelta.NONE, c.onFetched(snap(revision = 8, total = 99.0), 2_000))
        assertEquals(14.8, c.snapshot!!.teamTotal.value!!, 1e-9)
        c.perform(PanelAction.ToggleVisibility, 3_000)
        assertTrue(c.shouldFetch(3_000))
        val delta = c.onFetched(snap(revision = 8, total = 99.0), 3_000)
        assertTrue("shown panel applies the refresh", delta.totalsChanged)
        assertEquals(99.0, c.snapshot!!.teamTotal.value!!, 1e-9)
    }

    @Test fun onlyChangedRowsAreReported() {
        val c = loaded()
        val delta = c.onFetched(snap(revision = 8, rows = listOf(prow("p-11", 12.3), prow("p-23", 4.5), prow("p-31", 4.0)), total = 20.8), 1)
        assertEquals(setOf("p-23"), delta.changedRows)
        assertEquals(emptySet<String>(), delta.removedRows)
        assertTrue(delta.totalsChanged)
        assertEquals(4.5, c.snapshot!!.rows[1].points.value!!, 1e-9)
    }

    @Test fun firstSnapshotReportsEveryRow() {
        val c = controller()
        assertTrue("Missing behavior: a new panel fetches immediately", c.shouldFetch(0))
        val delta = c.onFetched(snap(), 0)
        assertEquals(setOf("p-11", "p-23", "p-31"), delta.changedRows)
        assertTrue(delta.totalsChanged)
    }

    @Test fun starterChangeReportsAddedAndRemovedRowsOnly() {
        val c = loaded()
        val delta = c.onFetched(snap(revision = 8, rows = listOf(prow("p-11", 12.3), prow("p-23", -1.5), prow("p-44", 0.0))), 1)
        assertEquals(setOf("p-44"), delta.changedRows)
        assertEquals(setOf("p-31"), delta.removedRows)
        assertEquals(listOf("p-11", "p-23", "p-44"), c.snapshot!!.rows.map { it.playerId })
    }

    @Test fun identicalOrOlderRevisionChangesNothing() {
        val c = loaded(s = snap(revision = 9))
        assertEquals(PanelDelta.NONE, c.onFetched(snap(revision = 9), 1))
        assertEquals("an older revision is ignored", PanelDelta.NONE, c.onFetched(snap(revision = 8, total = 0.0), 2))
        assertEquals(14.8, c.snapshot!!.teamTotal.value!!, 1e-9)
    }

    @Test fun burstOfUpdatesHoldsOneSnapshotAndReportsOnlyTheChangedRow() {
        val c = loaded()
        var last = PanelDelta.NONE
        for (i in 1..10_000) {
            last = c.onFetched(snap(revision = 7L + i, rows = listOf(prow("p-11", 12.3 + i), prow("p-23", -1.5), prow("p-31", 4.0))), i.toLong())
            assertEquals("update $i changes only p-11", setOf("p-11"), last.changedRows)
        }
        assertEquals("rows do not accumulate across updates", 3, c.snapshot!!.rows.size)
        assertEquals(10_012.3, c.snapshot!!.rows[0].points.value!!, 1e-6)
        assertEquals(10_007L, c.snapshot!!.revision)
        assertTrue(last.totalsChanged.not())
    }
}

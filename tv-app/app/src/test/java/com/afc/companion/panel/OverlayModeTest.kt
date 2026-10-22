package com.afc.companion.panel

import android.view.KeyEvent
import com.afc.companion.profile.customized
import com.afc.companion.profile.TeamLeague
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** Held-≡ state machine: card, small menu, expanded side panel; only the menu and panel take focus. */
class OverlayModeTest {
    private class Host(leagues: List<String> = listOf("league-a/team-7", "league-b/team-8"), var permitted: Boolean = true) {
        val panel = PanelController(leagues, leagues.firstOrNull(), false)
        var added = 0
        var removed = 0
        var permissionRequests = 0
        val controller = OverlayController(panel, { permitted }, { permissionRequests++ }, { added++ }, { removed++ })
    }

    @Test fun firstHoldShowsTheNonFocusableCard() {
        val h = Host()
        assertEquals(OverlayMode.Off, h.controller.mode)
        assertEquals(OverlayOutcome.Shown, h.controller.hold())
        assertEquals(OverlayMode.Card, h.controller.mode)
        assertFalse("plain card never takes the remote from the game", h.controller.focusable)
        assertEquals(1, h.added)
        assertTrue("the card reads the team total, so the panel feed runs", h.panel.visible)
    }

    @Test fun holdOnTheCardOpensTheFocusableMenuAndHoldAgainReturnsToTheCard() {
        val h = Host()
        h.controller.hold()
        h.controller.hold()
        assertEquals(OverlayMode.Menu, h.controller.mode)
        assertTrue(h.controller.focusable)
        assertEquals("menu opens on its first item", OverlayMenuItem.entries.first(), h.controller.menuFocus)
        h.controller.hold()
        assertEquals(OverlayMode.Card, h.controller.mode)
        assertFalse(h.controller.focusable)
        assertEquals("one surface, never re-added", 1, h.added)
        assertEquals(0, h.removed)
    }

    @Test fun leagueEntryRequiresTwoDistinctKnownPairsAndNavigationSkipsItOtherwise() {
        for (pairs in listOf(emptyList(), listOf("a/t"), listOf("a/t", "a/t"))) {
            val h = Host(pairs)
            h.controller.hold(); h.controller.hold()
            assertEquals(listOf(OverlayMenuItem.Expand, OverlayMenuItem.Hide), h.controller.menuItems)
            h.controller.onFocusedKey(KeyEvent.KEYCODE_DPAD_DOWN)
            assertEquals(OverlayMenuItem.Hide, h.controller.menuFocus)
            h.controller.onFocusedKey(KeyEvent.KEYCODE_DPAD_UP)
            assertEquals(OverlayMenuItem.Expand, h.controller.menuFocus)
        }
        assertEquals(OverlayMenuItem.entries, Host(listOf("a/t", "b/u")).controller.menuItems)
    }

    @Test fun dpadMovesMenuFocusWithinBoundsAndOkSelects() {
        val h = Host()
        h.controller.hold(); h.controller.hold()
        val items = OverlayMenuItem.entries
        repeat(items.size + 2) { assertTrue(h.controller.onFocusedKey(KeyEvent.KEYCODE_DPAD_DOWN)) }
        assertEquals(items.last(), h.controller.menuFocus)
        repeat(items.size + 2) { assertTrue(h.controller.onFocusedKey(KeyEvent.KEYCODE_DPAD_UP)) }
        assertEquals(items.first(), h.controller.menuFocus)
        while (h.controller.menuFocus != OverlayMenuItem.Expand) h.controller.onFocusedKey(KeyEvent.KEYCODE_DPAD_DOWN)
        assertTrue(h.controller.onFocusedKey(KeyEvent.KEYCODE_DPAD_CENTER))
        assertEquals(OverlayMode.Expanded, h.controller.mode)
        assertTrue("expanded side panel may take focus", h.controller.focusable)
    }

    @Test fun backFromMenuOrExpandedReturnsToTheCardAndReleasesFocus() {
        val h = Host()
        h.controller.hold(); h.controller.hold()
        assertTrue(h.controller.onFocusedKey(KeyEvent.KEYCODE_BACK))
        assertEquals(OverlayMode.Card, h.controller.mode)
        assertFalse(h.controller.focusable)
        h.controller.hold()
        h.controller.select(OverlayMenuItem.Expand)
        assertTrue(h.controller.onFocusedKey(KeyEvent.KEYCODE_BACK))
        assertEquals(OverlayMode.Card, h.controller.mode)
        assertFalse(h.controller.focusable)
        assertTrue("the card keeps its data feed", h.panel.visible)
    }

    @Test fun okOnTheExpandedPanelOpensTheMenuAndHoldReturnsToTheCard() {
        val h = Host()
        h.controller.hold(); h.controller.hold()
        h.controller.select(OverlayMenuItem.Expand)
        assertTrue(h.controller.onFocusedKey(KeyEvent.KEYCODE_ENTER))
        assertEquals(OverlayMode.Menu, h.controller.mode)
        h.controller.select(OverlayMenuItem.Expand)
        h.controller.hold()
        assertEquals(OverlayMode.Card, h.controller.mode)
    }

    @Test fun cardModeIgnoresFocusedKeysSoTheyBelongToTheGame() {
        val h = Host()
        h.controller.hold()
        for (key in listOf(KeyEvent.KEYCODE_BACK, KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_DPAD_DOWN)) {
            assertFalse(h.controller.onFocusedKey(key))
        }
        assertEquals(OverlayMode.Card, h.controller.mode)
    }

    @Test fun hideRemovesTheSurfaceAndStopsTheFeed() {
        val h = Host()
        h.controller.hold(); h.controller.hold()
        h.controller.select(OverlayMenuItem.Hide)
        assertEquals(OverlayMode.Off, h.controller.mode)
        assertFalse(h.controller.focusable)
        assertEquals(1, h.removed)
        assertFalse(h.panel.visible)
        assertEquals("the next hold shows the card again", OverlayOutcome.Shown, h.controller.hold())
        assertEquals(OverlayMode.Card, h.controller.mode)
    }

    @Test fun inAppButtonTogglesTheCardAndHidesFromAnyOpenSurface() {
        val h = Host()
        assertEquals(OverlayOutcome.Shown, h.controller.toggle())
        assertEquals("Show over game now shows the corner card", OverlayMode.Card, h.controller.mode)
        h.controller.hold(); h.controller.select(OverlayMenuItem.Expand)
        assertEquals(OverlayOutcome.Hidden, h.controller.toggle())
        assertEquals(OverlayMode.Off, h.controller.mode)
        assertEquals(1, h.removed)
    }

    @Test fun deniedHoldAsksForTheOverlayPermissionWithoutAWindow() {
        val h = Host(permitted = false)
        assertEquals(OverlayOutcome.PermissionNeeded, h.controller.hold())
        assertEquals(OverlayMode.Off, h.controller.mode)
        assertEquals(1, h.permissionRequests)
        assertEquals(0, h.added)
    }

    @Test fun leagueSwitcherCyclesTheProfileLeaguesThroughThePanelAndWraps() {
        val h = Host(listOf("league-a/team-7", "league-b/team-8", "league-c/team-9"))
        h.controller.hold(); h.controller.hold()
        h.panel.onFetched(snap(teamLeague = "league-a/team-7"), 0)
        h.controller.select(OverlayMenuItem.League)
        assertEquals("league-b/team-8", h.panel.teamLeague)
        assertEquals("switching drops the other league's rows", null, h.panel.snapshot)
        assertTrue("and refetches immediately", h.panel.shouldFetch(1))
        assertEquals("the menu stays open for another press", OverlayMode.Menu, h.controller.mode)
        h.controller.select(OverlayMenuItem.League)
        h.controller.select(OverlayMenuItem.League)
        assertEquals("league-a/team-7", h.panel.teamLeague)
    }

    @Test fun unpairedProfileListsNeverInventTeamLeagueAssociations() {
        val base = customized()
        val profile = base.copy(
            teamLeague = TeamLeague("league-b", "team-7"),
            selections = base.selections.copy(leagues = setOf("league-c", "league-a", "league-b")),
        )
        assertEquals(listOf("league-b/team-7"), overlayTeamLeagues(profile))
        assertEquals("selected pair only", listOf("league-b/team-7"), overlayTeamLeagues(profile.copy(selections = profile.selections.copy(leagues = emptySet()))))
        assertEquals("no pair, no switcher", emptyList<String>(), overlayTeamLeagues(profile.copy(teamLeague = null)))
        assertEquals(emptyList<String>(), overlayTeamLeagues(null))
        assertEquals("first entry is the existing panel key", panelTeamLeague(profile), overlayTeamLeagues(profile).first())
    }
}

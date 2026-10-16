package com.afc.companion.panel

import android.view.KeyEvent
import com.afc.companion.alerts.alertData
import com.afc.companion.alerts.alertJson
import com.afc.companion.net.Alert
import com.afc.companion.net.Envelope
import com.afc.companion.net.RoutingOutcome
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * P2-X02 FAILS (no heads-up on Fire OS 8.1): alerts are presented panel-only (AFC-PR-021,
 * DES-AFC-P2-ALERTPATH), at the top of the fullScreen panel, each with D-pad-reachable Watch and Dismiss.
 */
class PanelAlertsTest {
    private fun alertOf(id: String, eventId: Boolean = true, player: String = "Player Eleven"): Alert {
        val data = alertData(player = player).apply { if (!eventId) remove("eventId") }
        return checkNotNull(Envelope.from(alertJson(id, 1, data))?.let(Alert::from))
    }

    private fun controller(vararg alerts: Alert): PanelController =
        PanelController(listOf(TL), TL, true).apply {
            onFetched(snap(), 0)
            onAlerts(panelAlerts(alerts.toList()))
        }

    private fun press(c: PanelController, key: Int, times: Int = 1) = repeat(times) { assertTrue(c.onKey(key, 0)) }

    @Test fun alertsAreShownNewestFirstWithSanitizedTextOnly() {
        val shown = panelAlerts(listOf(alertOf("a1"), alertOf("a2"), alertOf("bad", player = "Player will score")))
        assertEquals("unsafe text is dropped whole, newest first", listOf("a2", "a1"), shown.map { it.id })
        assertEquals("Red-zone alert", shown.first().text.headline)
        assertEquals("Access: unknown", shown.first().text.access)
    }

    @Test fun panelShowsAtMostTheNewestThreeAlerts() {
        val shown = panelAlerts((1..5).map { alertOf("a$it") })
        assertEquals("bounded so the lineup stays on screen", listOf("a5", "a4", "a3"), shown.map { it.id })
    }

    @Test fun watchAndDismissAreReachableByDpadAboveTheLineup() {
        val c = controller(alertOf("a1"))
        assertEquals(
            listOf(FocusTarget.AlertWatch("a1"), FocusTarget.AlertDismiss("a1"), FocusTarget.TeamLeagueSwitch,
                FocusTarget.Row("p-11"), FocusTarget.Row("p-23"), FocusTarget.Row("p-31"), FocusTarget.Total),
            c.focusTargets(),
        )
        assertEquals("focus is not stolen by an arriving alert", FocusTarget.TeamLeagueSwitch, c.focused)
        press(c, KeyEvent.KEYCODE_DPAD_UP)
        assertEquals(FocusTarget.AlertDismiss("a1"), c.focused)
        assertEquals(AlertCommand.Dismiss("a1"), c.select(confirmSwitch = true))
        press(c, KeyEvent.KEYCODE_DPAD_UP)
        assertEquals(FocusTarget.AlertWatch("a1"), c.focused)
        assertEquals(AlertCommand.Watch("a1"), c.select(confirmSwitch = false))
    }

    @Test fun alertsAreReachableWithoutATeamLeague() {
        val c = PanelController(emptyList(), null, true).apply { onAlerts(panelAlerts(listOf(alertOf("a1")))) }
        press(c, KeyEvent.KEYCODE_DPAD_UP)
        assertEquals(FocusTarget.AlertDismiss("a1"), c.focused)
    }

    @Test fun selectKeyIsBoundToTheRemoteCenter() {
        assertEquals(PanelAction.Select, PanelController(listOf(TL), TL, true).bindings()[KeyEvent.KEYCODE_DPAD_CENTER])
    }

    @Test fun switchingConfirmationNeedsASecondPressAndFocusMoveCancelsIt() {
        val c = controller(alertOf("a1"))
        press(c, KeyEvent.KEYCODE_DPAD_UP, 2)
        assertNull("first press only asks for confirmation (AFC-PR-035)", c.select(confirmSwitch = true))
        assertEquals("a1", c.armedWatch)
        press(c, KeyEvent.KEYCODE_DPAD_DOWN)
        press(c, KeyEvent.KEYCODE_DPAD_UP)
        assertNull("moving focus cancels the pending confirmation", c.armedWatch)
        assertNull(c.select(confirmSwitch = true))
        assertEquals(AlertCommand.Watch("a1"), c.select(confirmSwitch = true))
        assertNull(c.armedWatch)
    }

    @Test fun alertWithoutAnEventOffersDismissOnly() {
        val c = controller(alertOf("a1", eventId = false))
        assertEquals("no event id means no attempt can be reported, so no Watch",
            listOf(FocusTarget.AlertDismiss("a1"), FocusTarget.TeamLeagueSwitch), c.focusTargets().take(2))
    }

    @Test fun dismissedAlertMovesFocusToAnExistingElement() {
        val c = controller(alertOf("a1"), alertOf("a2"))
        press(c, KeyEvent.KEYCODE_DPAD_UP)
        assertEquals(FocusTarget.AlertDismiss("a1"), c.focused)
        c.onAlerts(panelAlerts(listOf(alertOf("a2"))))
        assertTrue("focus never points at a dismissed alert: ${c.focused}", c.focused in c.focusTargets())
    }

    @Test fun hiddenPanelSelectsNothing() {
        val c = controller(alertOf("a1"))
        press(c, KeyEvent.KEYCODE_DPAD_UP)
        c.perform(PanelAction.ToggleVisibility, 0)
        assertNull(c.select(confirmSwitch = false))
        assertFalse(c.onKey(KeyEvent.KEYCODE_DPAD_CENTER, 0))
    }

    @Test fun watchOutcomeTextNeverClaimsTheGameOpenedUnlessReported() {
        assertEquals("Watch: could not confirm the game is playing.", PanelText.watchOutcome(RoutingOutcome.AccessUnknown))
        assertEquals("Watch: the provider app is not installed.", PanelText.watchOutcome(RoutingOutcome.AppAbsent))
        assertEquals("Watch: the provider app refused the launch.", PanelText.watchOutcome(RoutingOutcome.PlaybackDenied))
    }
}

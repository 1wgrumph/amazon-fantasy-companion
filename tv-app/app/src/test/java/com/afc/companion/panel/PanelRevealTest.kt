package com.afc.companion.panel

import com.afc.companion.MemoryPrefs
import com.afc.companion.alerts.alertData
import com.afc.companion.alerts.alertJson
import com.afc.companion.net.Alert
import com.afc.companion.net.Envelope
import com.afc.companion.profile.DeviceSettings
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** Owner decision 2026-10-16: the device-local "Show panel on new alert" setting, default on. */
class PanelRevealTest {
    private fun alertOf(id: String): Alert = checkNotNull(Envelope.from(alertJson(id, 1, alertData()))?.let(Alert::from))

    private fun hiddenPanel(reveal: Boolean, vararg held: Alert) = PanelController(listOf(TL), TL, false, revealOnNewAlert = reveal).apply {
        onAlerts(panelAlerts(held.toList()))
    }

    @Test fun settingOnReShowsAHiddenPanelForANewAlert() {
        val c = hiddenPanel(reveal = true, alertOf("a1"))
        assertFalse("alerts already held when the panel opens are not new", c.visible)
        c.onAlerts(panelAlerts(listOf(alertOf("a1"))))
        assertFalse("the same alert again is not new", c.visible)
        c.onAlerts(panelAlerts(listOf(alertOf("a1"), alertOf("a2"))))
        assertTrue(c.visible)
        assertTrue("a re-shown panel fetches its lineup", c.shouldFetch(0))
    }

    @Test fun settingOffKeepsTheHiddenPanelHidden() {
        val c = hiddenPanel(reveal = false, alertOf("a1"))
        c.onAlerts(panelAlerts(listOf(alertOf("a1"), alertOf("a2"))))
        assertFalse(c.visible)
        assertFalse(c.shouldFetch(0))
    }

    @Test fun dismissingAnAlertNeverReShowsThePanel() {
        val c = hiddenPanel(reveal = true, alertOf("a1"), alertOf("a2"))
        c.onAlerts(panelAlerts(listOf(alertOf("a2"))))
        assertFalse(c.visible)
    }

    @Test fun settingDefaultsOnAndPersistsOnThisDeviceAcrossRestart() {
        val prefs = MemoryPrefs()
        assertTrue("default on", DeviceSettings(prefs).showPanelOnNewAlert)
        DeviceSettings(prefs).showPanelOnNewAlert = false
        assertFalse("a new instance over the same file reads the stored choice", DeviceSettings(prefs).showPanelOnNewAlert)
        DeviceSettings(prefs).showPanelOnNewAlert = true
        assertTrue(DeviceSettings(prefs).showPanelOnNewAlert)
    }

    @Test fun onlyAFullScreenPanelIsReShown() {
        assertTrue(revealsOnNewAlert(setting = true, mode = PanelMode.FullScreen))
        assertFalse(revealsOnNewAlert(setting = false, mode = PanelMode.FullScreen))
        assertFalse(revealsOnNewAlert(setting = true, mode = PanelMode.ModeB))
    }

    @Test fun panelSettingLabelStatesItsStateAndThatItStaysOnThisTv() {
        assertEquals("Open lineup on alerts: On", DeviceSettings.label(true))
        assertEquals("Open lineup on alerts: Off", DeviceSettings.label(false))
        assertEquals("Applies immediately on this TV.", DeviceSettings.SCOPE_NOTE)
    }
}

package com.afc.companion

import com.afc.companion.alerts.profile
import com.afc.companion.profile.AlertType
import org.junit.Assert.assertEquals
import org.junit.Test

/** AFC-PR-009 / DES-AFC-P2-TV: the shell runs AlertService only with a session and an enabled alert type. */
class MonitoringTest {
    private class RecordingControl : MonitorControl {
        val calls = mutableListOf<String>()
        override fun start() { calls += "start" }
        override fun stop() { calls += "stop" }
    }

    private fun sync(hasSession: Boolean, alertTypes: Set<AlertType>?): List<String> {
        val control = RecordingControl()
        Shell().syncMonitoring(hasSession, alertTypes?.let { profile().copy(alertTypes = it) }, control)
        return control.calls
    }

    @Test fun startsAlertServiceWhenMonitoringIsEnabledAndASessionExists() {
        assertEquals(listOf("start"), sync(hasSession = true, alertTypes = setOf(AlertType.RedZone)))
    }

    @Test fun stopsAlertServiceWhenMonitoringIsDisabled() {
        assertEquals("no enabled alert type is no monitoring", listOf("stop"), sync(hasSession = true, alertTypes = emptySet()))
    }

    @Test fun stopsAlertServiceWithoutASession() {
        assertEquals(listOf("stop"), sync(hasSession = false, alertTypes = setOf(AlertType.RedZone)))
        assertEquals(listOf("stop"), sync(hasSession = false, alertTypes = null))
    }

    @Test fun unreadProfileLeavesMonitoringAsItIs() {
        assertEquals("a failed profile read is not a recorded enablement change", emptyList<String>(), sync(hasSession = true, alertTypes = null))
    }
}

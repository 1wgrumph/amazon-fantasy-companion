package com.afc.companion.alerts

import android.Manifest
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.afc.companion.net.Alert
import com.afc.companion.net.Envelope
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith

/**
 * AFC-PR-015 on the stick (CMD-TVAPP-INSTRUMENTED): with the default heads-up presentation, AlertNotifier posts a
 * high-importance notification with Watch and Dismiss actions. Needs the device; until it runs there this is
 * DEVICE_INSTALL_PENDING, never a pass. Over-playback display and no foregrounding stay with PROC-VISUAL-REVIEW.
 * Resource group: fire-tv-stick (one device, serialized under its lease).
 */
@RunWith(AndroidJUnit4::class)
class AlertNotifierDeviceTest {
    private val context: Context = InstrumentationRegistry.getInstrumentation().targetContext
    private val manager = context.getSystemService(NotificationManager::class.java)

    @Before fun grant() {
        if (Build.VERSION.SDK_INT >= 33) {
            InstrumentationRegistry.getInstrumentation().uiAutomation
                .grantRuntimePermission(context.packageName, Manifest.permission.POST_NOTIFICATIONS)
        }
        manager.cancelAll()
    }

    @After fun clear() = manager.cancelAll()

    @Test fun headsUpAlertPostsWatchAndDismissOnAHighImportanceChannel() {
        AlertNotifier(context).show(deviceAlert())
        val posted = manager.activeNotifications.singleOrNull()
        assertNotNull("one alert notification posted", posted)
        val notification = posted!!.notification
        assertEquals(listOf("Watch", "Dismiss"), notification.actions.orEmpty().map { it.title.toString() })
        if (Build.VERSION.SDK_INT >= 26) {
            val channel = manager.getNotificationChannel(notification.channelId)
            assertNotNull("alert channel exists", channel)
            assertEquals(NotificationManager.IMPORTANCE_HIGH, channel!!.importance)
        }
    }

    private fun deviceAlert(): Alert {
        val data = JSONObject().put("alertType", "redZone").put("eventId", "evt-device")
            .put("triggerContext", JSONObject().put("player", "Player Eleven").put("matchup", "KC at BUF"))
            .put("route", JSONObject().put("accessBasis", "unknown").put("provider", "provider-a"))
        val json = JSONObject().put("schemaVersion", 1).put("id", "alert-device").put("revision", 1).put("source", "replay")
            .put("updatedAt", "2026-10-15T00:20:00Z").put("data", data)
        return checkNotNull(Envelope.from(json)?.let(Alert::from))
    }
}

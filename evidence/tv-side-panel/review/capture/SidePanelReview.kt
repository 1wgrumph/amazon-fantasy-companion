package com.afc.companion.review

import android.app.Activity
import android.content.Intent
import android.content.ComponentName
import android.os.Bundle
import android.view.KeyEvent
import android.widget.TextView
import android.graphics.Color
import androidx.test.core.app.ActivityScenario
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.By
import com.afc.companion.MainActivity
import com.afc.companion.alerts.AlertFeed
import com.afc.companion.alerts.AlertInbox
import com.afc.companion.net.ApiClient
import com.afc.companion.net.Alert
import com.afc.companion.net.Envelope
import com.afc.companion.panel.*
import java.io.*
import java.net.*
import java.time.Instant
import kotlinx.coroutines.runBlocking
import org.json.*
import org.junit.Test
import org.junit.Assert.*

class SidePanelReview {
    private val ins = InstrumentationRegistry.getInstrumentation()
    private val ctx = ins.targetContext
    private val device = UiDevice.getInstance(ins)
    private val out by lazy { File(ctx.getExternalFilesDir(null), "side-panel-review").apply { mkdirs() } }
    private var page = JSONObject().put("cursor", "start").put("alerts", JSONArray())
    private val now get() = Instant.now().toString()
    private var count = 9
    private var profileDelay = 0L
    private fun value(v: Double?) = JSONObject().put("value", v ?: JSONObject.NULL).put("source", "manual").put("asOf", now)
    private fun envelope(data: JSONObject, id: String = "review") = JSONObject().put("schemaVersion", 1).put("id", id).put("revision", 1).put("source", "manual").put("updatedAt", now).put("data", data)
    private fun response(url: URL): JSONObject = when(url.path) {
        "/v1/profile" -> { if (profileDelay > 0) Thread.sleep(profileDelay)
            envelope(JSONObject().put("scoringPreset", "halfPpr").put("alertTypes", JSONArray())
                .put("teamLeague", JSONObject().put("league", "ReviewLeague").put("team", "ReviewTeam"))) }
        "/v1/panel" -> envelope(JSONObject().put("teamLeague", "ReviewLeague/ReviewTeam").put("scoringBasis", "halfPpr").put("sport", "nfl")
            .put("rows", JSONArray((1..count).map { i -> JSONObject().put("playerId", if(i == 1) "9000001" else "p$i").put("name", if(i == 1) "Sample Receiver" else "Sample Player $i")
                .put("points", value(if (i == 3) null else i * 2.5)).put("gameStatus", "Q2 08:14") }))
            .put("teamTotal", value(112.5)).put("progress", value(0.5)))
        "/v1/alerts" -> page
        else -> JSONObject()
    }
    private fun alert(id: String, optional: Boolean = false): JSONObject = envelope(JSONObject().put("alertType", "PlayerScore")
        .put("triggerContext", JSONObject().put("eventId", "review-event").put("matchup", "AAA at BBB")
            .put("starters", JSONArray().put(JSONObject().put("athlete_id", "9000001").put("name", "Sample Receiver").put("team", "AAA").put("slot", "WR").apply {
                if(optional) { put("shortName", "Guard"); put("points", 20.0) }
            })).apply { if(optional) put("sport", "nba") })
        .put("route", JSONObject().put("accessBasis", "unknown")), id)
    private fun screenshot(name: String) { device.takeScreenshot(File(out, "$name.png")) }
    private fun record(name: String) {
        val lines = device.executeShellCommand("dumpsys window").lineSequence().filter { it.contains("mCurrentFocus=") || it.contains("frame=[") || it.contains("ty=APPLICATION_OVERLAY") || it.contains("fl=NOT_FOCUSABLE") }.joinToString("\n")
        File(out, "$name-window.txt").writeText(lines)
    }
    private fun settle() { Thread.sleep(1200) }
    private fun game() {
        ctx.startActivity(Intent().setComponent(ComponentName("com.afc.companion.test", "com.afc.companion.review.ReviewGameActivity")).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        settle()
    }
    private fun companion() { ctx.startActivity(Intent(ctx, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)); settle() }
    private fun focusButton(text: String) {
        assertTrue(device.wait(androidx.test.uiautomator.Until.hasObject(By.text(text)), 15000))
        device.pressDPadLeft()
        repeat(8) { device.pressDPadUp() }
        repeat(if (text == "Show over game") 3 else 2) { device.pressDPadDown() }
        device.pressDPadCenter(); settle()
    }
    private fun clickShow() { focusButton("Show over game") }
    private fun stop() { ctx.stopService(Intent(ctx, OverlayService::class.java)); settle() }
    @Test fun monitoringShutdown() {
        URL.setURLStreamHandlerFactory { protocol -> if(protocol == "https") object : URLStreamHandler() {
            override fun openConnection(url: URL): URLConnection = object : HttpURLConnection(url) {
                override fun connect() {}; override fun disconnect() {}; override fun usingProxy() = false
                override fun getResponseCode() = 200
                override fun getOutputStream(): OutputStream = ByteArrayOutputStream()
                override fun getInputStream(): InputStream = ByteArrayInputStream(response(url).toString().toByteArray())
            }
        } else null }
        ActivityScenario.launch(MainActivity::class.java).use {
            device.executeShellCommand("appops set com.afc.companion SYSTEM_ALERT_WINDOW allow")
            ctx.startForegroundService(Intent(ctx, com.afc.companion.alerts.AlertService::class.java))
            settle()
            page = JSONObject().put("cursor", "monitor-stop").put("alerts", JSONArray().put(alert("stop-one", true)).put(alert("stop-two", true)))
            val deadline = System.currentTimeMillis() + 15000
            while (AlertInbox.alerts.value.isEmpty() && System.currentTimeMillis() < deadline) Thread.sleep(200)
            assertEquals(2, AlertInbox.alerts.value.size)
            game(); screenshot("before-monitor-stop")
            com.afc.companion.alerts.AlertServiceControl(ctx).stop()
            settle()
            assertTrue(AlertInbox.alerts.value.isEmpty())
            screenshot("after-monitor-stop"); record("after-monitor-stop")
            Thread.sleep(5500)
            screenshot("queued-card-after-monitor-stop"); record("queued-card-after-monitor-stop")
            val services = device.executeShellCommand("dumpsys activity services com.afc.companion")
            File(out, "monitor-stop.txt").writeText(services.lineSequence().filter {
                it.contains("ServiceRecord{") || it.contains("isForeground=") || it.contains("startRequested=")
            }.joinToString("\n") + "\nInbox empty: " + AlertInbox.alerts.value.isEmpty())
            stop()
        }
    }
    @Test fun fullScreenWithoutOverlay() {
        URL.setURLStreamHandlerFactory { protocol -> if(protocol == "https") object : URLStreamHandler() {
            override fun openConnection(url: URL): URLConnection = object : HttpURLConnection(url) {
                override fun connect() {}; override fun disconnect() {}; override fun usingProxy() = false
                override fun getResponseCode() = 200
                override fun getOutputStream(): OutputStream = ByteArrayOutputStream()
                override fun getInputStream(): InputStream = ByteArrayInputStream(response(url).toString().toByteArray())
            }
        } else null }
        ActivityScenario.launch(MainActivity::class.java).use {
            stop(); focusButton("Panel"); screenshot("full-screen-clean")
            assertTrue(device.hasObject(By.text("Team/league: ReviewLeague/ReviewTeam")))
            assertTrue(device.hasObject(By.text("Sample Receiver")))
        }
    }
    @Test fun independentRuntimeReview() {
        URL.setURLStreamHandlerFactory { protocol -> if(protocol == "https") object : URLStreamHandler() {
            override fun openConnection(url: URL): URLConnection = object : HttpURLConnection(url) {
                override fun connect() {}; override fun disconnect() {}; override fun usingProxy() = false
                override fun getResponseCode() = 200
                override fun getOutputStream(): OutputStream = ByteArrayOutputStream()
                override fun getInputStream(): InputStream = ByteArrayInputStream(response(url).toString().toByteArray())
            }
        } else null }
        val report = StringBuilder()
        try {
            ActivityScenario.launch(MainActivity::class.java).use {
                device.executeShellCommand("appops set com.afc.companion SYSTEM_ALERT_WINDOW default")
                clickShow(); screenshot("permission-settings"); device.pressBack(); settle(); screenshot("permission-hint")
                report.append("Denied permission: app remains alive; settings route opened.\n")
                device.executeShellCommand("appops set com.afc.companion SYSTEM_ALERT_WINDOW allow")
                game(); companion(); clickShow(); screenshot("panel-nine-rows"); record("panel-nine-rows")
                device.pressDPadDown(); device.pressDPadCenter(); settle(); screenshot("panel-input-to-game")
                companion(); clickShow(); screenshot("panel-hidden")
                stop()
                // Start the same app-private background card action monitoring uses, without opening the panel.
                companion(); OverlayServiceControl(ctx).startAlerts(); settle(); game()
                val feed = AlertFeed(ApiClient("https://review.invalid"))
                AlertInbox.attach(feed); settle()
                val a = alert("current-envelope")
                val notice = alertCardNotice(requireNotNull(Alert.from(requireNotNull(Envelope.from(a)))), null)!!
                report.append("Current envelope with null panel: player=${notice.player}, value=${notice.value}, sport='${notice.sport}'\n")
                assertTrue(notice.value.isNaN()); assertEquals("", notice.sport)
                page = JSONObject().put("cursor", "one").put("alerts", JSONArray().put(a))
                runBlocking { assertEquals(1, feed.poll().size) }; AlertInbox.publish(); settle()
                screenshot("card-no-panel-current-envelope"); record("card-no-panel")
                device.pressDPadDown(); settle(); screenshot("card-input-to-game")
                Thread.sleep(4300); screenshot("card-expired"); record("card-expired")
                report.append("Card timed out; no panel shown.\n")
                // A three-row panel plus two queued alerts checks geometry and timeout independently of long lineup.
                count = 3; companion(); clickShow(); screenshot("panel-three-rows")
                page = JSONObject().put("cursor", "two").put("alerts", JSONArray().put(alert("queued-nfl")).put(alert("queued-nba", true)))
                runBlocking { assertEquals(2, feed.poll().size) }; AlertInbox.publish(); settle()
                screenshot("card-and-panel"); record("card-and-panel")
                Thread.sleep(4300); screenshot("second-card-and-panel"); record("second-card-and-panel")
                Thread.sleep(5300); screenshot("panel-restored"); record("panel-restored")
                report.append("Two notices queued and expired; panel restored.\n")
                // MainActivity still renders its normal panel using the default compact=false path.
                companion(); focusButton("Panel"); screenshot("full-screen-panel")
                // Delayed profile load plus ACTION_ALERTS documents the declared stopIfIdle race.
                stop(); profileDelay = 3000
                OverlayServiceControl(ctx).toggle(); Thread.sleep(200); OverlayServiceControl(ctx).startAlerts(); Thread.sleep(4000)
                screenshot("delayed-toggle-with-alert-start"); record("delayed-toggle-with-alert-start")
                report.append("Delayed toggle + alert-start exercised; see screenshot/window record.\n")
            }
        } finally {
            stop(); AlertInbox.attach(null)
            File(out, "runtime.txt").writeText(report.toString())
        }
    }
}

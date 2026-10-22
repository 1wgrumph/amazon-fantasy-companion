package com.afc.companion.review

import android.app.Activity
import android.content.Intent
import android.content.ComponentName
import android.os.Bundle
import android.view.KeyEvent
import android.widget.TextView
import android.graphics.Color
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.requestFocus
import androidx.compose.ui.test.onAllNodesWithText
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

class SidePanelRepairCapture {
    @get:org.junit.Rule val compose = androidx.compose.ui.test.junit4.createEmptyComposeRule()
    private val ins = InstrumentationRegistry.getInstrumentation()
    private val ctx = ins.targetContext
    private val device = UiDevice.getInstance(ins)
    private val out by lazy { File(ctx.getExternalFilesDir(null), "side-panel-repair").apply { mkdirs() } }
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
        compose.onNodeWithText(text).requestFocus()
        device.pressDPadCenter(); settle()
    }
    private fun clickShow() { focusButton("Show over game") }
    private fun stop() { ctx.stopService(Intent(ctx, OverlayService::class.java)); settle() }
    private fun awaitText(text: String) {
        val deadline = System.currentTimeMillis() + 20_000
        while (System.currentTimeMillis() < deadline) {
            if (compose.onAllNodesWithText(text).fetchSemanticsNodes().isNotEmpty()) return
            Thread.sleep(100)
        }
        fail("Missing rendered text: $text")
    }
    @Test fun repairedOverlay() {
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
            // Actual remote button flow, then return to the independent synthetic game activity.
            clickShow(); awaitText("Team total: 112.5"); game()
            screenshot("side-panel-over-game"); record("side-panel")
            compose.mainClock.advanceTimeBy(5100); settle(); screenshot("compact-lineup-page-2")
            companion(); clickShow()
            OverlayServiceControl(ctx).startAlerts(); settle(); game()
            val feed = AlertFeed(ApiClient("https://review.invalid"))
            AlertInbox.attach(feed); settle()
            page = JSONObject().put("cursor", "hidden").put("alerts", JSONArray().put(alert("hidden")))
            runBlocking { assertEquals(1, feed.poll().size) }; AlertInbox.publish()
            awaitText("Receiver 2.5"); settle(); screenshot("alert-card-over-game"); record("hidden-card")
            device.pressDPadDown(); settle(); screenshot("card-remote-focus")
            Thread.sleep(5300); screenshot("card-expired")
            companion(); clickShow(); awaitText("Team total: 112.5"); game()
            page = JSONObject().put("cursor", "both").put("alerts", JSONArray().put(alert("both")))
            runBlocking { assertEquals(1, feed.poll().size) }; AlertInbox.publish()
            awaitText("Receiver 2.5"); settle(); screenshot("card-and-panel"); record("card-and-panel")
            Thread.sleep(5300); screenshot("panel-restored-after-card"); record("panel-restored")
            stop(); AlertInbox.attach(null)
            companion(); focusButton("Panel"); awaitText("Team/league: ReviewLeague/ReviewTeam"); screenshot("full-screen-panel")
            assertTrue(device.hasObject(By.text("Team/league: ReviewLeague/ReviewTeam")))
            assertTrue(device.hasObject(By.text("Sample Receiver")))
        }
    }
}

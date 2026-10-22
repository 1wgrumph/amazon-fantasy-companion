package com.afc.companion.review

import android.content.ComponentName
import android.content.Intent
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.test.performSemanticsAction
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.requestFocus
import androidx.test.core.app.ActivityScenario
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.By
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.Until
import com.afc.companion.MainActivity
import com.afc.companion.panel.OverlayService
import java.io.*
import java.net.*
import java.time.Instant
import org.json.*
import org.junit.Assert.*
import org.junit.Test

/** tv-branding visual capture: synthetic profile and panel served in-process; no network, no real accounts. */
class BrandingCapture {
    @get:org.junit.Rule val compose = androidx.compose.ui.test.junit4.createEmptyComposeRule()
    private val ins = InstrumentationRegistry.getInstrumentation()
    private val ctx = ins.targetContext
    private val device = UiDevice.getInstance(ins)
    private val out by lazy { File(ctx.getExternalFilesDir(null), "tv-branding").apply { mkdirs() } }
    private val now get() = Instant.now().toString()
    @Volatile private var profileDelay = 0L
    @Volatile private var hasTeam = true
    private fun value(v: Double?) = JSONObject().put("value", v ?: JSONObject.NULL).put("source", "manual").put("asOf", now)
    private fun envelope(data: JSONObject) = JSONObject().put("schemaVersion", 1).put("id", "review").put("revision", 1).put("source", "manual").put("updatedAt", now).put("data", data)
    private fun response(url: URL): JSONObject = when (url.path) {
        "/v1/profile" -> {
            if (profileDelay > 0) Thread.sleep(profileDelay)
            envelope(JSONObject().put("scoringPreset", "halfPpr").put("alertTypes", JSONArray()).apply {
                if (hasTeam) put("teamLeague", JSONObject().put("league", "SampleLeague").put("team", "SampleTeam"))
            })
        }
        "/v1/panel" -> envelope(JSONObject().put("teamLeague", "SampleLeague/SampleTeam").put("scoringBasis", "halfPpr").put("sport", "nfl")
            .put("rows", JSONArray((1..6).map { i -> JSONObject().put("playerId", "p$i").put("name", "Sample Player $i")
                .put("points", value(i * 2.5)).put("gameStatus", "Q2 08:14") }))
            .put("teamTotal", value(52.5)).put("progress", value(0.5)))
        "/v1/alerts" -> JSONObject().put("cursor", "start").put("alerts", JSONArray())
        else -> JSONObject()
    }
    private fun shot(name: String) { settle(); assertTrue(device.takeScreenshot(File(out, "$name.png"))) }
    private fun settle() { Thread.sleep(1500) }
    private fun awaitText(text: String) {
        val deadline = System.currentTimeMillis() + 20_000
        while (System.currentTimeMillis() < deadline) {
            if (compose.onAllNodesWithText(text).fetchSemanticsNodes().isNotEmpty()) return
            Thread.sleep(100)
        }
        fail("Missing rendered text: $text")
    }
    private fun press(text: String) {
        assertTrue(device.wait(Until.hasObject(By.text(text)), 15_000))
        // Rail buttons only (useUnmergedTree=false); the panel heading shares "My lineup" but has no click action.
        compose.onNode(hasText(text) and hasClickAction()).requestFocus().performSemanticsAction(SemanticsActions.OnClick); settle()
    }
    private fun game() {
        ctx.startActivity(Intent().setComponent(ComponentName("com.afc.companion.test", "com.afc.companion.review.ReviewGameActivity")).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        settle()
    }

    @Test fun branding() {
        URL.setURLStreamHandlerFactory { protocol -> if (protocol == "https") object : URLStreamHandler() {
            override fun openConnection(url: URL): URLConnection = object : HttpURLConnection(url) {
                override fun connect() {}; override fun disconnect() {}; override fun usingProxy() = false
                override fun getResponseCode() = 200
                override fun getOutputStream(): OutputStream = ByteArrayOutputStream()
                override fun getInputStream(): InputStream = ByteArrayInputStream(response(url).toString().toByteArray())
            }
        } else null }
        ActivityScenario.launch(MainActivity::class.java).use {
            device.executeShellCommand("appops set com.afc.companion SYSTEM_ALERT_WINDOW allow")
            hasTeam = false
            press("My lineup"); awaitText("No lineup yet. Choose a team and league in My setup."); settle(); shot("my-lineup-empty")
            hasTeam = true
            profileDelay = 8_000
            press("My setup"); awaitText("Loading profile…"); shot("loading")
            profileDelay = 0
            awaitText("Manage your teams, players and alert preferences."); settle(); shot("my-setup")
            compose.onNodeWithText("NFL alerts: on").performScrollTo(); settle(); shot("my-setup-sports")
            press("My lineup"); awaitText("Team total: 52.5"); awaitText("Lineup progress: 50%"); shot("my-lineup")
            press("Show over game"); awaitText("Team total: 52.5"); game(); settle(); shot("side-panel-over-game")
            ctx.stopService(Intent(ctx, OverlayService::class.java)); settle()
        }
    }
}

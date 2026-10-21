package com.afc.companion.visual

import android.app.NotificationManager
import android.view.KeyEvent
import androidx.activity.ComponentActivity
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.Modifier
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.unit.dp
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.UiDevice
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text
import com.afc.companion.Destination
import com.afc.companion.alerts.AlertFeed
import com.afc.companion.alerts.AlertInbox
import com.afc.companion.link.LinkView
import com.afc.companion.net.ApiClient
import com.afc.companion.panel.LineupPanel
import com.afc.companion.panel.PanelMode
import com.afc.companion.profile.ProfileSettingsScreen
import com.afc.companion.ui.theme.*
import java.io.*
import java.net.HttpURLConnection
import java.net.URL
import kotlinx.coroutines.runBlocking
import org.json.JSONArray
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

/** Synthetic in-process HTTP peer. No credentials, network, backend writes or provider launches. */
class FireDesignCapture {
    @get:Rule val rule = createAndroidComposeRule<ComponentActivity>()
    private val instrumentation = InstrumentationRegistry.getInstrumentation()

    @After fun clear() {
        AlertInbox.attach(null)
        instrumentation.targetContext.getSystemService(NotificationManager::class.java).cancelAll()
    }

    @Test fun link() {
        show { LinkView(client(), onLinked = { error("Fixture must never link") }) }
        waitText("ABCD2345")
        screenshot("link")
    }

    @Test fun profile() {
        show { ProfileSettingsScreen(client()) }
        waitText("LeagueOne")
        val button = rule.onNode(hasClickAction() and hasAnyDescendant(hasText("Show panel on new alert: on (this TV only)")), useUnmergedTree = true)
        button.performScrollTo().requestFocus().assertIsFocused()
        screenshot("profile-button")
        val field = rule.onNode(hasText("LeagueOne"))
        field.performScrollTo().requestFocus().assertIsFocused()
        screenshot("profile-field")
    }

    @Test fun lineup() {
        show { LineupPanel(client(), PanelMode.FullScreen) }
        waitText("Player Eleven")
        instrumentation.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_DOWN)
        rule.waitForIdle()
        screenshot("lineup")
    }

    @Test fun alert() {
        val peer = client()
        val feed = AlertFeed(peer)
        runBlocking { assertTrue(feed.poll().size == 1) }
        AlertInbox.attach(feed)
        show { LineupPanel(peer, PanelMode.FullScreen) }
        waitText("Red-zone alert")
        instrumentation.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_UP)
        instrumentation.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_UP)
        rule.waitForIdle()
        screenshot("alert")
    }

    // Match AppShell's available content area so screenshots also check clipping beside navigation.
    private fun show(content: @Composable () -> Unit) = rule.setContent {
        AfcTheme {
            Row(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).tvSafeZonePadding()) {
                Column(Modifier.padding(8.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    Destination.entries.forEach { destination -> TvButton(onClick = {}) { Text(destination.label) } }
                }
                Box(Modifier.weight(1f).fillMaxSize()) {
                    CompositionLocalProvider(LocalTvSafeZoneApplied provides true, content = content)
                }
            }
        }
    }

    private fun waitText(text: String) = rule.waitUntil(10_000) {
        rule.onAllNodes(hasText(text)).fetchSemanticsNodes().isNotEmpty()
    }

    private fun screenshot(name: String) {
        rule.waitForIdle()
        val device = UiDevice.getInstance(instrumentation)
        device.waitForIdle()
        assertTrue(device.takeScreenshot(File(instrumentation.targetContext.cacheDir, "fire-design-$name.png")))
    }

    private fun client() = ApiClient("https://fixture.invalid", openConnection = { url ->
        object : HttpURLConnection(url) {
            override fun connect() { connected = true }
            override fun disconnect() { connected = false }
            override fun usingProxy() = false
            override fun getResponseCode() = 200
            override fun getOutputStream(): OutputStream = ByteArrayOutputStream()
            override fun getInputStream(): InputStream = ByteArrayInputStream(response(url.path).toString().toByteArray())
        }
    }, backoff = {})

    private fun response(path: String): JSONObject = when (path) {
        "/v1/link" -> JSONObject().put("code", "ABCD2345").put("expires", "2026-10-22T20:00:00Z").put("handle", "visual-fixture")
        "/v1/profile" -> envelope(JSONObject().put("scoringPreset", "halfPpr")
            .put("teamLeague", JSONObject().put("league", "LeagueOne").put("team", "TeamOne")))
        "/v1/panel" -> envelope(JSONObject().put("teamLeague", "LeagueOne/TeamOne").put("scoringBasis", "halfPpr")
            .put("rows", JSONArray().put(row("p11", "Player Eleven", 12.3)).put(row("p23", "Player Twenty-Three", 8.5)))
            .put("teamTotal", value(20.8)).put("progress", value(0.5)))
        "/v1/alerts" -> JSONObject().put("cursor", "visual-fixture").put("alerts", JSONArray().put(envelope(
            JSONObject().put("alertType", "redZone").put("eventId", "event-fixture")
                .put("triggerContext", JSONObject().put("player", "Player Eleven").put("matchup", "KC at BUF"))
                .put("route", JSONObject().put("accessBasis", "unknown").put("provider", "provider-a")), "alert-fixture")))
        else -> error("Unexpected request: $path")
    }

    private fun envelope(data: JSONObject, id: String = "visual-fixture") = JSONObject()
        .put("schemaVersion", 1).put("id", id).put("revision", 1).put("source", "manual")
        .put("updatedAt", "2026-10-21T00:00:00Z").put("data", data)
    private fun value(number: Double) = JSONObject().put("value", number).put("source", "replay")
        .put("asOf", "2026-10-21T00:00:00Z")
    private fun row(id: String, name: String, points: Double) = JSONObject().put("playerId", id)
        .put("name", name).put("points", value(points)).put("gameStatus", "Q2 08:14")
}

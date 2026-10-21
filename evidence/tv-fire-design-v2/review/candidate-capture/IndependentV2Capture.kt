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
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.runBlocking
import org.json.JSONArray
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

/** Synthetic in-process HTTP peer. No credentials, network, backend writes or provider launches. */
class IndependentV2Capture {
    @get:Rule val rule = createAndroidComposeRule<ComponentActivity>()
    private val instrumentation = InstrumentationRegistry.getInstrumentation()

    private val holdProfile = CountDownLatch(1)
    private val holdPanel = CountDownLatch(1)

    @After fun clear() {
        holdProfile.countDown()
        holdPanel.countDown()
        AlertInbox.attach(null)
        instrumentation.targetContext.getSystemService(NotificationManager::class.java).cancelAll()
    }

    @Test fun link() {
        show { LinkView(client(), onLinked = { error("Fixture must never link") }) }
        waitText("ABCD2345")
        val nav = rule.onNode(hasClickAction() and hasAnyDescendant(hasText("Link")), useUnmergedTree = true)
        nav.requestFocus()
        instrumentation.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_DOWN)
        instrumentation.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_UP)
        rule.waitForIdle()
        screenshot("link")
    }

    @Test fun panelDataLoaderIsScreenCentered() {
        show { LineupPanel(client(holdData = true), PanelMode.FullScreen) }
        waitText("Loading panel…")
        assertCenteredLoadingLabel("Loading panel…")
    }
    @Test fun panelProfileLoaderIsScreenCentered() {
        show { LineupPanel(client(holdProfile = true), PanelMode.FullScreen) }
        waitText("Loading profile…")
        assertCenteredLoadingLabel("Loading profile…")
    }
    @Test fun localToggleRemainsAvailableWhileLoading() {
        show { ProfileSettingsScreen(client(holdProfile = true)) }
        waitText("Loading profile…")
        val toggles = rule.onAllNodes(hasText("Show panel on new alert:", substring = true)).fetchSemanticsNodes()
        assertTrue("Local device toggle must remain reachable while profile GET is pending", toggles.isNotEmpty())
    }
    private fun assertCenteredLoadingLabel(label: String) {
        val centerY = rule.onNode(hasText(label)).fetchSemanticsNode().boundsInRoot.center.y
        val density = instrumentation.targetContext.resources.displayMetrics.density
        // 80dp loop + 24dp gap + 30sp label: label centre is 52dp below the centred group.
        val expected = UiDevice.getInstance(instrumentation).displayHeight / 2f + 52f * density
        assertTrue("Loading label centre $centerY px, expected $expected px in the screen content viewport",
            kotlin.math.abs(centerY - expected) <= 4f * density)
    }
    @Test fun profileNavFocus() {
        show { ProfileSettingsScreen(client()) }
        waitText("LeagueOne")
        val nav = rule.onNode(hasClickAction() and hasAnyDescendant(hasText("Profile/Settings")), useUnmergedTree = true)
        nav.requestFocus()
        instrumentation.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_DOWN)
        instrumentation.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_UP)
        nav.assertIsFocused()
        screenshot("profile-nav-focus")
    }
    @Test fun profile() {
        show { ProfileSettingsScreen(client()) }
        waitText("LeagueOne")
        val button = rule.onNode(hasClickAction() and hasAnyDescendant(hasText("Show panel on new alert: on (this TV only)")), useUnmergedTree = true)
        button.performScrollTo().requestFocus().assertIsFocused()
        screenshot("profile-button")
        val field = rule.onNode(hasText("LeagueOne"))
        field.performScrollTo().requestFocus().assertIsFocused()
        instrumentation.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_DOWN)
        rule.onNode(hasText("TeamOne")).assertIsFocused()
        instrumentation.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_UP)
        field.assertIsFocused()
        screenshot("profile-field")
        val sports = rule.onNode(hasClickAction() and hasAnyDescendant(hasText("NBA alerts: on")), useUnmergedTree = true)
        sports.performScrollTo().requestFocus().assertIsFocused()
        screenshot("profile-sports")
        instrumentation.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_UP)
        rule.waitForIdle()
        screenshot("profile-nfl-focused")
        instrumentation.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_CENTER)
        rule.waitForIdle()
        screenshot("profile-nfl-toggled")
    }

    @Test fun loading() {
        show { ProfileSettingsScreen(client(holdProfile = true)) }
        waitText("Loading profile…")
        screenshot("loading")
        Thread.sleep(350)
        screenshot("loading-next-frame")
    }

    @Test fun panelProfileLoading() {
        show { LineupPanel(client(holdProfile = true), PanelMode.FullScreen) }
        waitText("Loading profile…")
        screenshot("panel-profile-loading")
    }
    @Test fun panelDataLoadingWithAlert() {
        val peer = client(holdData = true)
        val feed = AlertFeed(peer)
        runBlocking { assertTrue(feed.poll().size == 1) }
        AlertInbox.attach(feed)
        show { LineupPanel(peer, PanelMode.FullScreen) }
        waitText("Loading panel…")
        screenshot("panel-data-loading-alert")
    }
    @Test fun panelDataLoading() {
        show { LineupPanel(client(holdData = true), PanelMode.FullScreen) }
        waitText("Loading panel…")
        screenshot("panel-data-loading")
    }
    @Test fun profileError() {
        show { ProfileSettingsScreen(client(scenario = "error")) }
        waitText("Profile is unavailable. Check the connection and try again.")
        screenshot("profile-error")
    }
    @Test fun panelEmpty() {
        show { LineupPanel(client(scenario = "empty"), PanelMode.FullScreen) }
        waitText("Panel unavailable: no team/league is selected in Profile/Settings.")
        screenshot("panel-empty")
    }
    @Test fun panelError() {
        show { LineupPanel(client(scenario = "panel-error"), PanelMode.FullScreen) }
        waitText("Panel data unavailable.")
        screenshot("panel-error")
    }
    @Test fun lineupNfl() = lineup("nfl", "Player Eleven")

    @Test fun lineupNba() = lineup("nba", "Player Thirty")

    private fun lineup(sport: String, first: String) {
        show { LineupPanel(client(sport), PanelMode.FullScreen) }
        waitText(first)
        instrumentation.sendKeyDownUpSync(KeyEvent.KEYCODE_DPAD_DOWN)
        rule.waitForIdle()
        screenshot("lineup-$sport")
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
            Row(Modifier.fillMaxSize().afcBackground().tvSafeZonePadding()) {
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
        assertTrue(device.takeScreenshot(File(instrumentation.targetContext.cacheDir, "review-v2-$name.png")))
    }

    private fun client(sport: String = "nfl", holdProfile: Boolean = false, holdData: Boolean = false, scenario: String = "normal") = ApiClient("https://fixture.invalid", openConnection = { url ->
        // Holds the profile response open so the loading state stays on screen for its capture.
        if (holdProfile && url.path == "/v1/profile") this.holdProfile.await(30, TimeUnit.SECONDS)
        if (holdData && url.path == "/v1/panel") holdPanel.await(30, TimeUnit.SECONDS)
        object : HttpURLConnection(url) {
            override fun connect() { connected = true }
            override fun disconnect() { connected = false }
            override fun usingProxy() = false
            override fun getResponseCode() = 200
            override fun getOutputStream(): OutputStream = ByteArrayOutputStream()
            override fun getInputStream(): InputStream = ByteArrayInputStream((if (scenario == "error" && url.path == "/v1/profile" || scenario == "panel-error" && url.path == "/v1/panel") JSONObject() else if (scenario == "empty" && url.path == "/v1/profile") envelope(JSONObject()) else response(url.path, sport)).toString().toByteArray())
        }
    }, backoff = {})

    private fun response(path: String, sport: String): JSONObject = when (path) {
        "/v1/link" -> JSONObject().put("code", "ABCD2345").put("expires", "2026-10-22T20:00:00Z").put("handle", "visual-fixture")
        "/v1/profile" -> envelope(JSONObject().put("scoringPreset", "halfPpr")
            .put("teamLeague", JSONObject().put("league", "LeagueOne").put("team", "TeamOne")))
        "/v1/panel" -> if (sport == "nba") {
            envelope(JSONObject().put("teamLeague", "LeagueOne/TeamOne").put("scoringBasis", "nbaPoints").put("sport", "nba")
                .put("rows", JSONArray().put(row("p30", "Player Thirty", 31.5)).put(row("p7", "Player Seven", 18.0)))
                .put("teamTotal", value(49.5)).put("progress", value(0.6)))
        } else {
            envelope(JSONObject().put("teamLeague", "LeagueOne/TeamOne").put("scoringBasis", "halfPpr").put("sport", "nfl")
                .put("rows", JSONArray().put(row("p11", "Player Eleven", 12.3)).put(row("p23", "Player Twenty-Three", 8.5)))
                .put("teamTotal", value(20.8)).put("progress", value(0.5)))
        }
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

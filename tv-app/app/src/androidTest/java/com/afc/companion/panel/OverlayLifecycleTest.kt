package com.afc.companion.panel

import android.content.Intent
import android.os.SystemClock
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import org.junit.Rule
import androidx.test.core.app.ActivityScenario
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.By
import androidx.test.uiautomator.UiDevice
import com.afc.companion.MainActivity
import com.afc.companion.alerts.AlertFeed
import com.afc.companion.alerts.AlertInbox
import com.afc.companion.alerts.AlertService
import com.afc.companion.alerts.AlertServiceControl
import com.afc.companion.net.ApiClient
import java.io.*
import java.net.*
import java.time.Instant
import kotlinx.coroutines.runBlocking
import org.json.*
import org.junit.After
import org.junit.Before
import org.junit.BeforeClass
import org.junit.Test
import org.junit.Assert.*

/** F01/F03: real app services and inbox; current committed PlayerScore shape, synthetic own-lineup data.
 * Build with -PafcApiBaseUrl=https://review.invalid; the synthetic peer replaces HTTPS in-process.
 * Resource group: owned TV emulator display, serialized by the host's afc-tv-review lease/lock.
 */
class OverlayLifecycleTest {
    @get:Rule val compose = createEmptyComposeRule()
    private fun hasText(text: String) = compose.onAllNodesWithText(text).fetchSemanticsNodes().isNotEmpty()
    private val instrumentation = InstrumentationRegistry.getInstrumentation()
    private val context = instrumentation.targetContext
    private val device = UiDevice.getInstance(instrumentation)
    private lateinit var activity: ActivityScenario<MainActivity>
    @Before fun start() {
        page = JSONObject().put("cursor", "initial").put("alerts", JSONArray())
        team = "ReviewTeam"; sport = "nfl"; points = 2.5
        activity = ActivityScenario.launch(MainActivity::class.java)
        await("Companion foreground") { device.hasObject(By.text("Show over game")) }
        device.executeShellCommand("appops set com.afc.companion SYSTEM_ALERT_WINDOW allow")
    }
    @After fun stop() {
        context.stopService(Intent(context, AlertService::class.java))
        context.stopService(Intent(context, OverlayService::class.java))
        AlertInbox.attach(null)
        activity.close()
    }
    private fun await(message: String, ready: () -> Boolean) {
        val deadline = SystemClock.elapsedRealtime() + 20_000
        while (!ready() && SystemClock.elapsedRealtime() < deadline) SystemClock.sleep(100)
        assertTrue("$message; services=" + services(), ready())
    }
    private fun services() = device.executeShellCommand("dumpsys activity services com.afc.companion").lineSequence()
        .filter { it.contains("ServiceRecord{") || it.contains("isForeground=") }.joinToString("\n")
    private fun publish(feed: AlertFeed, id: String) {
        page = JSONObject().put("cursor", id).put("alerts", JSONArray().put(alert(id)))
        runBlocking { assertEquals(1, feed.poll().size) }
        AlertInbox.publish()
    }
    @Test fun hiddenPanelCardsUseCurrentSelectedProfileAcrossTeamAndSportChanges() {
        OverlayServiceControl(context).startAlerts()
        await("card host started") { services().contains(".panel.OverlayService}") }
        val feed = AlertFeed(ApiClient("https://review.invalid"))
        AlertInbox.attach(feed)
        publish(feed, "hidden-nfl")
        await("hidden-panel NFL card has number and sport") { hasText("Receiver 2.5") && hasText("NFL") }
        team = "OtherTeam"; points = 7.5
        publish(feed, "new-team")
        await("new selected team supplies fresh points") { hasText("Receiver 7.5") }
        sport = "nba"; points = 20.0
        publish(feed, "new-sport")
        await("new selected sport supplies fresh points and mark") { hasText("Receiver 20") && hasText("NBA") }
        assertFalse("card-only action must not create a panel", hasText("Team total: 112.5"))
    }
    @Test fun stoppingMonitoringRemovesCardsAndTheHiddenHost() {
        context.startForegroundService(Intent(context, AlertService::class.java))
        await("monitor and overlay started") { services().contains(".panel.OverlayService}") }
        page = JSONObject().put("cursor", "monitor").put("alerts", JSONArray().put(alert("monitor")))
        await("monitor delivered alert") { AlertInbox.alerts.value.isNotEmpty() }
        AlertServiceControl(context).stop()
        await("monitor stopped") { AlertInbox.alerts.value.isEmpty() }
        await("hidden overlay host stopped with monitoring") { !services().contains(".panel.OverlayService}") }
    }
    @Test fun stoppingMonitoringPreservesVisiblePanelUntilItIsToggledOff() {
        OverlayServiceControl(context).toggle()
        await("panel rendered") { hasText("Team total: 112.5") }
        context.startForegroundService(Intent(context, AlertService::class.java))
        await("monitor started") { services().contains(".alerts.AlertService}") }
        AlertServiceControl(context).stop()
        await("monitor stopped") { !services().contains(".alerts.AlertService}") }
        assertTrue(hasText("Team total: 112.5"))
        OverlayServiceControl(context).toggle()
        await("last overlay owner stopped") { !services().contains(".panel.OverlayService}") }
    }
    /** F04: sample actual compositor rectangles, including the observed window-move animation. */
    @Test fun cardArrivalReplacementAndExpiryNeverOverlapThePanel() {
        OverlayServiceControl(context).toggle()
        await("panel rendered") { hasText("Team total: 112.5") }
        OverlayServiceControl(context).startAlerts()
        device.pressHome()
        val feed = AlertFeed(ApiClient("https://review.invalid"))
        AlertInbox.attach(feed)
        val frames = ArrayList<String>()
        val ownFrame = Regex("com\\.afc\\.companion, frame=\\[(-?\\d+),(-?\\d+),(-?\\d+),(-?\\d+)\\]")
        val began = SystemClock.elapsedRealtime()
        var sawCard = false
        var restored = false
        try {
            publish(feed, "arrival")
            publish(feed, "replacement")
            while (SystemClock.elapsedRealtime() - began < 20_000) {
                val rects = ownFrame.findAll(device.executeShellCommand("dumpsys window"))
                    .map { match -> match.groupValues.drop(1).map(String::toInt) }.distinct().toList()
                val elapsed = SystemClock.elapsedRealtime() - began
                frames.add("$elapsed ms: $rects")
                if (rects.size == 2) {
                    sawCard = true
                    val (a, b) = rects
                    val overlap = a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3]
                    if (overlap) device.takeScreenshot(File(context.getExternalFilesDir(null), "f04-overlap.png"))
                    assertFalse("card/panel compositor overlap: ${frames.last()}", overlap)
                }
                // Observe both five-second cards, rather than ending at a replacement's transient remove.
                if (sawCard && elapsed >= 2 * AlertCardQueue.SHOW_MS && rects.size == 1 && rects[0][1] == 54) {
                    restored = true
                    break
                }
            }
            assertTrue("no two-window compositor frame was observed", sawCard)
            assertTrue("panel did not restore after both cards expired; last=${frames.lastOrNull()}", restored)
        } finally {
            File(context.getExternalFilesDir(null), "f04-frames.txt").writeText(frames.joinToString("\n"))
        }
    }
    companion object {
        @Volatile private var team = "ReviewTeam"
        @Volatile private var sport = "nfl"
        @Volatile private var points = 2.5
        @Volatile private var page = JSONObject()
        private fun value(number: Double) = JSONObject().put("value", number).put("source", "manual").put("asOf", Instant.now().toString())
        private fun envelope(data: JSONObject, id: String = "review") = JSONObject().put("schemaVersion", 1).put("id", id)
            .put("revision", 1).put("source", "manual").put("updatedAt", Instant.now().toString()).put("data", data)
        private fun alert(id: String) = envelope(JSONObject().put("alertType", "PlayerScore")
            .put("triggerContext", JSONObject().put("eventId", "review-event").put("matchup", "AAA at BBB")
                .put("starters", JSONArray().put(JSONObject().put("athlete_id", "9000001").put("name", "Sample Receiver").put("team", "AAA").put("slot", "WR"))))
            .put("route", JSONObject().put("accessBasis", "unknown")), id)
        private fun response(url: URL) = when (url.path) {
            "/v1/profile" -> envelope(JSONObject().put("scoringPreset", "halfPpr")
                .put("alertTypes", JSONArray()).put("teamLeague", JSONObject().put("league", "ReviewLeague").put("team", team)))
            "/v1/panel" -> envelope(JSONObject().put("teamLeague", "ReviewLeague/$team").put("scoringBasis", if (sport == "nba") "nbaPoints" else "halfPpr").put("sport", sport)
                .put("rows", JSONArray().put(JSONObject().put("playerId", "9000001").put("name", "Sample Receiver").put("points", value(points)).put("gameStatus", "Q2 08:14")))
                .put("teamTotal", value(112.5)).put("progress", value(0.5)))
            "/v1/alerts" -> page
            else -> JSONObject()
        }
        @BeforeClass @JvmStatic fun syntheticPeer() {
            URL.setURLStreamHandlerFactory { protocol -> if (protocol == "https") object : URLStreamHandler() {
                override fun openConnection(url: URL): URLConnection = object : HttpURLConnection(url) {
                    override fun connect() {}; override fun disconnect() {}; override fun usingProxy() = false
                    override fun getResponseCode() = 200
                    override fun getOutputStream(): OutputStream = ByteArrayOutputStream()
                    override fun getInputStream(): InputStream = ByteArrayInputStream(response(url).toString().toByteArray())
                }
            } else null }
        }
    }
}

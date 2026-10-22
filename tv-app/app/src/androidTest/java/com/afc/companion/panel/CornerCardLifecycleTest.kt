package com.afc.companion.panel

import androidx.compose.ui.test.onAllNodesWithText
import android.app.UiAutomation
import androidx.test.uiautomator.Configurator
import android.content.Intent
import android.content.ComponentName
import android.os.SystemClock
import androidx.test.core.app.ActivityScenario
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.By
import androidx.test.uiautomator.Until
import com.afc.companion.MainActivity
import com.afc.companion.alerts.AlertFeed
import com.afc.companion.alerts.AlertInbox
import com.afc.companion.net.ApiClient
import com.afc.companion.net.SessionStore
import com.afc.companion.panel.OverlayService
import com.afc.companion.panel.OverlayServiceControl
import java.io.*
import java.net.*
import java.time.Instant
import java.util.Collections
import kotlinx.coroutines.runBlocking
import org.json.*
import org.junit.Test
import org.junit.Assert.*

/** Real-window regressions for the accepted corner-card findings. Synthetic HTTPS peer, no provider app.
 * Run alone with -PafcApiBaseUrl=https://review.invalid on an owned 1920x1080 TV AVD.
 * Resource group: owned TV display, serialized by the host AVD lease; one warm engine, ~90 s.
 */
class CornerCardLifecycleTest {
    @get:org.junit.Rule val compose = androidx.compose.ui.test.junit4.createEmptyComposeRule()
    private fun hasText(text: String) = compose.onAllNodesWithText(text).fetchSemanticsNodes(atLeastOneRootRequired = false).isNotEmpty()
    private val ins = InstrumentationRegistry.getInstrumentation()
    private val ctx = ins.targetContext
    private val device = run {
        Configurator.getInstance().setUiAutomationFlags(UiAutomation.FLAG_DONT_SUPPRESS_ACCESSIBILITY_SERVICES)
        UiDevice.getInstance(ins)
    }
    private val out by lazy { File(ctx.getExternalFilesDir(null), "corner-repair").apply { mkdirs() } }
    private val requests = Collections.synchronizedList(ArrayList<String>())
    @Volatile private var page = JSONObject().put("cursor", "start").put("alerts", JSONArray())
    @Volatile private var exactAlertSport: String? = null
    private val now get() = Instant.now().toString()
    private fun value(v: Double?) = JSONObject().put("value", v ?: JSONObject.NULL).put("source", "manual").put("asOf", now)
    private fun envelope(data: JSONObject, id: String = "review") = JSONObject().put("schemaVersion",1).put("id",id).put("revision",1).put("source","manual").put("updatedAt",now).put("data",data)
    private fun response(url: URL): JSONObject {
        requests.add(url.path + (url.query?.let { "?$it" } ?: ""))
        return when(url.path) {
            "/v1/profile" -> envelope(JSONObject().put("scoringPreset","halfPpr").put("alertTypes",JSONArray())
                .put("teamLeague",JSONObject().put("league","LeagueA").put("team","TeamA"))
                .put("fantasySelections",JSONObject().put("leagues",JSONArray(listOf("LeagueA","LeagueB"))).put("teams",JSONArray(listOf("TeamA","TeamB"))).put("players",JSONArray()).put("favoriteTeams",JSONArray())))
            "/v1/panel" -> {
                val key = url.query?.substringAfter("teamLeague=")?.let { URLDecoder.decode(it,"UTF-8") } ?: "LeagueA/TeamA"
                val known = key == "LeagueA/TeamA" || key == "LeagueB/TeamB"
                val sport = exactAlertSport
                if (sport != null) return envelope(JSONObject().put("teamLeague", key)
                    .put("scoringBasis", if (sport == "nba") "nbaPoints" else "halfPpr")
                    .apply { if (sport == "nba") put("sport", "nba") }
                    .put("rows", JSONArray().put(JSONObject().put("playerId", "e2e-synth-ath-$sport-1")
                        .put("name", if (sport == "nfl") "Synth Runner" else "Synth Guard")
                        .put("points", value(20.0)).put("gameStatus", "Live")))
                    .put("teamTotal", value(20.0)).put("progress", value(0.5)))
                envelope(JSONObject().put("teamLeague",key).put("scoringBasis","halfPpr")
                    .put("rows",if (known) JSONArray((1..9).map { i -> JSONObject().put("playerId","p$i").put("name","Sample Receiver $i").put("points",value(i * 2.5)).put("gameStatus","Q2 08:14") }) else JSONArray())
                    .put("teamTotal",value(if (known) 112.5 else null)).put("progress",value(if(known) 0.5 else null)))
            }
            "/v1/alerts" -> page
            else -> JSONObject()
        }
    }
    private fun installPeer() = OverlayTestPeer.respondWith(::response)
    private fun settle() = SystemClock.sleep(900)
    private fun screenshot(name: String) { settle(); assertTrue(device.takeScreenshot(File(out,"$name.png"))); record(name) }
    private fun record(name: String) {
        val dump = device.executeShellCommand("dumpsys window")
        File(out,"$name-window.txt").writeText(dump.lineSequence().filter { it.contains("mCurrentFocus=") || it.contains("frame=[") || it.contains("ty=APPLICATION_OVERLAY") || it.contains("fl=NOT_FOCUSABLE") || it.contains("fl=NOT_TOUCH_MODAL") }.joinToString("\n"))
        device.dumpWindowHierarchy(File(out,"$name.xml"))
    }
    private fun game(dark: Boolean = false) {
        ctx.startActivity(Intent().setComponent(ComponentName("com.afc.companion.test","com.afc.companion.panel.CornerGameActivity"))
            .putExtra("dark",dark).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP)); settle()
    }
    private fun companion() { ctx.startActivity(Intent(ctx,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)); settle() }
    private fun click(text: String) {
        assertTrue("Missing $text",device.wait(Until.hasObject(By.text(text)),15000))
        device.pressDPadLeft(); repeat(12) { device.pressDPadUp() }
        repeat(when(text) { "Show over game" -> 3; "Expand over game" -> 4; else -> 2 }) { device.pressDPadDown() }
        device.pressDPadCenter(); settle()
    }
    private fun focus() = device.executeShellCommand("dumpsys window").lineSequence().firstOrNull { it.contains("mCurrentFocus=") }.orEmpty()
    private fun access(on: Boolean) {
        device.executeShellCommand("settings put secure enabled_accessibility_services ${if(on) "com.afc.companion/com.afc.companion.access.MenuHoldService" else "null"}")
        device.executeShellCommand("settings put secure accessibility_enabled ${if(on) 1 else 0}"); SystemClock.sleep(1800)
        var dump = device.executeShellCommand("dumpsys accessibility")
        val deadline = SystemClock.elapsedRealtime() + 15000
        while(on && !dump.substringAfter("Bound services:").substringBefore("Enabled services:").contains("capabilities=8,") && SystemClock.elapsedRealtime() < deadline) {
            SystemClock.sleep(500)
            dump = device.executeShellCommand("dumpsys accessibility")
        }
        File(out,"access-${if(on) "on" else "off"}.txt").writeText(dump.lineSequence().filter {
            it.contains("Bound services:") || it.contains("Enabled services:") || it.contains("Ui Automation")
        }.joinToString("\n"))
        if(on) assertTrue("Harness must preserve bound accessibility services", dump.substringAfter("Bound services:").substringBefore("Enabled services:").contains("capabilities=8,"))
    }
    private fun hardwareMenu(duration: Int, afterRelease: Int = 500) {
        val commands = listOf(
            JSONObject("""{"id":1,"command":"register","name":"AFC Review Remote","vid":1,"pid":1,"bus":"usb","configuration":[{"type":100,"data":[1]},{"type":101,"data":[139]}]}"""),
            JSONObject("""{"id":1,"command":"delay","duration":800}"""),
            JSONObject("""{"id":1,"command":"inject","events":[1,139,1,0,0,0]}"""),
            JSONObject().put("id",1).put("command","delay").put("duration",duration),
            JSONObject("""{"id":1,"command":"inject","events":[1,139,0,0,0,0]}"""),
            JSONObject().put("id",1).put("command","delay").put("duration",afterRelease))
        val file = File(out,"remote.jsonl").apply { writeText(commands.joinToString("\n") + "\n") }
        device.executeShellCommand("uinput ${file.absolutePath}"); settle()
    }
    private fun publish(feed: AlertFeed, id: String) {
        val a = envelope(JSONObject().put("alertType","PlayerScore").put("triggerContext",JSONObject().put("eventId","fictional-event").put("sport","nfl").put("matchup","AAA at BBB")
            .put("starters",JSONArray().put(JSONObject().put("athlete_id","p1").put("name","Sample Receiver").put("shortName","Receiver").put("points",2.5).put("team","AAA").put("slot","WR"))))
            .put("route",JSONObject().put("accessBasis","unknown")),id)
        page = JSONObject().put("cursor",id).put("alerts",JSONArray().put(a))
        runBlocking { assertEquals(1,feed.poll().size) }; AlertInbox.publish()
    }
    private fun await(label: String, ready: () -> Boolean) {
        val deadline = SystemClock.elapsedRealtime() + 20_000
        while (!ready() && SystemClock.elapsedRealtime() < deadline) SystemClock.sleep(100)
        assertTrue(label, ready())
    }
    private fun gameFocused() = focus().contains("CornerGameActivity")
    private fun overlayFocused() = Regex(""" u\d+ com\.afc\.companion\}""").containsMatchIn(focus())
    private fun assertBrightContrast(name: String) {
        val bitmap = android.graphics.BitmapFactory.decodeFile(File(out, "$name.png").absolutePath)
        val background = bitmap.getPixel(1805, 100)
        val histogram = HashMap<Int, Int>()
        for (x in 1550..1660) for (y in 85..120) {
            val pixel = bitmap.getPixel(x, y)
            if (android.graphics.Color.red(pixel) > 200 && android.graphics.Color.green(pixel) > 200 && android.graphics.Color.blue(pixel) > 200) {
                histogram[pixel] = (histogram[pixel] ?: 0) + 1
            }
        }
        val ink = histogram.maxByOrNull { it.value } ?: throw AssertionError("No rendered total text pixels")
        assertTrue("solid text samples", ink.value > 20)
        fun luminance(pixel: Int): Double {
            fun linear(channel: Int): Double {
                val c = channel / 255.0
                return if (c <= 0.04045) c / 12.92 else Math.pow((c + 0.055) / 1.055, 2.4)
            }
            return 0.2126 * linear(android.graphics.Color.red(pixel)) + 0.7152 * linear(android.graphics.Color.green(pixel)) + 0.0722 * linear(android.graphics.Color.blue(pixel))
        }
        val ratio = (luminance(ink.key) + 0.05) / (luminance(background) + 0.05)
        File(out, "rendered-contrast.txt").writeText("background=$background ink=${ink.key} samples=${ink.value} contrast=$ratio\n")
        assertTrue("actual compositor contrast $ratio", ratio >= 4.5f)
        bitmap.recycle()
    }
    @Test fun remoteCardMenuAndServiceOffFallback() {
        installPeer(); SessionStore(ctx).save("synthetic-review-session")
        val keyLogPath = "/sdcard/Android/data/com.afc.companion.test/files/menu-events.txt"
        fun keyEvents() = device.executeShellCommand("cat $keyLogPath").trim().lines()
        device.executeShellCommand("rm -f $keyLogPath")
        try {
            ActivityScenario.launch(MainActivity::class.java).use {
                device.executeShellCommand("appops set com.afc.companion SYSTEM_ALERT_WINDOW allow")
                access(false); game(); companion(); click("Show over game")
                await("service-off card and hint") { hasText("112.5") && hasText("Hold ≡ needs Accessibility") }
                assertTrue("card leaves game focused", gameFocused())
                screenshot("repair-01-service-off-card")
                companion(); click("Panel")
                await("in-app Expand control") { hasText("Expand over game") }
                click("Expand over game")
                await("fallback opens expanded content") { hasText("Team total: 112.5") }
                assertTrue("expanded overlay owns focus", overlayFocused())
                screenshot("repair-02-service-off-expand")
                device.pressBack(); await("Back releases expanded focus") { gameFocused() }
                ctx.stopService(Intent(ctx, OverlayService::class.java)); settle()
                access(true); game()
                hardwareMenu(150, 1500)
                assertFalse("short Menu must not show card", hasText("112.5"))
                val shortEvents = keyEvents()
                assertEquals("short down and up delivered", 2, shortEvents.size)
                assertTrue(shortEvents[0].startsWith("action=0 repeat=0"))
                assertTrue(shortEvents[1].startsWith("action=1"))
                screenshot("repair-03-short-menu")
                hardwareMenu(1000, 4000)
                await("held Menu shows NFL card from current untagged wire") { hasText("112.5") && hasText("NFL") }
                assertTrue("card never steals game focus", gameFocused())
                val heldEvents = keyEvents().drop(shortEvents.size)
                val ups = heldEvents.filter { it.startsWith("action=1") }
                assertTrue("initial held down reaches the game unchanged", heldEvents.first().startsWith("action=0 repeat=0"))
                assertEquals("one initial down", 1, heldEvents.count { it.startsWith("action=0 repeat=0 ") })
                assertEquals("one release while remote is still present", 1, ups.size)
                val releaseAt = ups.single().substringAfter("held=").toLong()
                assertTrue("release delivered at physical up, not device disconnect: $releaseAt", releaseAt in 900..1600)
                assertTrue("no repeats after release during four-second observation", heldEvents.last().startsWith("action=1"))
                assertTrue("intermediate events remain downs", heldEvents.dropLast(1).all { it.startsWith("action=0") })
                assertFalse("one hold cannot also open the menu", hasText("Expand"))
                File(out, "menu-events.txt").writeText(keyEvents().joinToString("\n"))
                screenshot("repair-04-card-bright"); assertBrightContrast("repair-04-card-bright")
                game(true); screenshot("repair-05-card-dark")
                hardwareMenu(1000)
                await("hold opens menu") { hasText("Expand") && hasText("Hide") }
                assertTrue("menu overlay takes focus", overlayFocused())
                assertFalse("unpaired selections never create a League row", hasText("League: LeagueA"))
                assertFalse(requests.any { it.contains("LeagueB%2FTeamA") })
                screenshot("repair-06-menu")
                device.pressDPadCenter()
                await("Expand shows shared panel") { hasText("Team total: 112.5") }
                assertTrue("expanded overlay owns focus", overlayFocused())
                screenshot("repair-07-expanded")
                device.pressBack(); await("Back from expanded restores game") { gameFocused() }
                screenshot("repair-08-back-to-game")
                hardwareMenu(1000); device.pressBack()
                await("Back from menu restores game") { gameFocused() }
                OverlayServiceControl(ctx).startAlerts(); settle()
                val feed = AlertFeed(ApiClient("https://review.invalid")); AlertInbox.attach(feed); settle()
                publish(feed, "repair-alert")
                await("alert with declared sport rendered") { hasText("Receiver 2.5") }
                screenshot("repair-09-card-plus-alert")
                val frames = Regex("com\\.afc\\.companion, frame=\\[(-?\\d+),(-?\\d+),(-?\\d+),(-?\\d+)\\]")
                    .findAll(device.executeShellCommand("dumpsys window")).map { it.groupValues.drop(1).map(String::toInt) }.distinct().toList()
                assertEquals("two actual overlay frames", 2, frames.size)
                val (a, b) = frames
                assertFalse("actual card and alert cannot overlap", a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3])
                for (r in frames) assertTrue("safe zone: $r", r[0] >= 96 && r[1] >= 54 && r[2] <= 1824 && r[3] <= 1026)
                await("alert expires") { !hasText("Receiver 2.5") }
                screenshot("repair-10-alert-expired")
            }
        } finally {
            ctx.stopService(Intent(ctx, OverlayService::class.java)); AlertInbox.attach(null); access(false)
        }
    }
    @Test fun deployedNflAndNbaAlertEnvelopesRenderActualCards() {
        installPeer(); SessionStore(ctx).save("synthetic-review-session")
        val feed = AlertFeed(ApiClient("https://review.invalid"))
        try {
            device.executeShellCommand("appops set com.afc.companion SYSTEM_ALERT_WINDOW allow")
            access(false); game()
            ctx.stopService(Intent(ctx, OverlayService::class.java)); settle()
            AlertInbox.attach(feed); settle()
            OverlayServiceControl(ctx).startAlerts(); settle()
            for ((index, sport) in listOf("nfl", "nba").withIndex()) {
                exactAlertSport = sport
                val wire = JSONObject(ins.context.assets.open("alert-e2e/$sport-fire-e1.json").bufferedReader().use { it.readText() })
                assertFalse("exact deployed alert has no sport", wire.getJSONObject("data").getJSONObject("triggerContext").has("sport"))
                page = JSONObject().put("cursor", wire.getString("id")).put("alerts", JSONArray().put(wire))
                runBlocking { assertEquals(1, feed.poll().size) }; AlertInbox.publish()
                val label = if (sport == "nfl") "Runner 20" else "Guard 20"
                await("actual $sport AlertCardOverlay from deployed envelope") { hasText(label) && hasText(sport.uppercase()) }
                assertTrue("alert does not steal game focus", gameFocused())
                screenshot("repair-${11 + index}-exact-$sport-alert")
                await("$sport card expires") { !hasText(label) }
            }
        } finally {
            ctx.stopService(Intent(ctx, OverlayService::class.java)); AlertInbox.attach(null); exactAlertSport = null
        }
    }

}

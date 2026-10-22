package com.afc.companion.cornerreview

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

/** Independent evidence harness. Product source and product tests remain unchanged. */
class CornerReview {
    private val ins = InstrumentationRegistry.getInstrumentation()
    private val ctx = ins.targetContext
    private val device = run {
        Configurator.getInstance().setUiAutomationFlags(UiAutomation.FLAG_DONT_SUPPRESS_ACCESSIBILITY_SERVICES)
        UiDevice.getInstance(ins)
    }
    private val out by lazy { File(ctx.getExternalFilesDir(null), "corner-review").apply { mkdirs() } }
    private val report = StringBuilder()
    private val requests = Collections.synchronizedList(ArrayList<String>())
    @Volatile private var tagNfl = true
    @Volatile private var page = JSONObject().put("cursor", "start").put("alerts", JSONArray())
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
                envelope(JSONObject().put("teamLeague",key).put("scoringBasis","halfPpr").put("sport","nfl")
                    .put("rows",if (known) JSONArray((1..9).map { i -> JSONObject().put("playerId","p$i").put("name","Sample Receiver $i").put("points",value(i * 2.5)).put("gameStatus","Q2 08:14") }) else JSONArray())
                    .put("teamTotal",value(if (known) 112.5 else null)).put("progress",value(if(known) 0.5 else null)).apply { if(!tagNfl) remove("sport") })
            }
            "/v1/alerts" -> page
            else -> JSONObject()
        }
    }
    private fun installPeer() {
        URL.setURLStreamHandlerFactory { protocol -> if(protocol == "https") object : URLStreamHandler() {
            override fun openConnection(url: URL): URLConnection = object : HttpURLConnection(url) {
                override fun connect() {}; override fun disconnect() {}; override fun usingProxy() = false
                override fun getResponseCode() = 200
                override fun getOutputStream(): OutputStream = ByteArrayOutputStream()
                override fun getInputStream(): InputStream = ByteArrayInputStream(response(url).toString().toByteArray())
            }
        } else null }
    }
    private fun settle() = SystemClock.sleep(900)
    private fun check(label: String, good: Boolean) { report.append("${if(good) "PASS" else "FAIL"}: $label\n") }
    private fun screenshot(name: String) { settle(); assertTrue(device.takeScreenshot(File(out,"$name.png"))); record(name) }
    private fun record(name: String) {
        val dump = device.executeShellCommand("dumpsys window")
        File(out,"$name-window.txt").writeText(dump.lineSequence().filter { it.contains("mCurrentFocus=") || it.contains("frame=[") || it.contains("ty=APPLICATION_OVERLAY") || it.contains("fl=NOT_FOCUSABLE") || it.contains("fl=NOT_TOUCH_MODAL") }.joinToString("\n"))
        device.dumpWindowHierarchy(File(out,"$name.xml"))
    }
    private fun game(dark: Boolean = false) {
        ctx.startActivity(Intent().setComponent(ComponentName("com.afc.companion.test","com.afc.companion.cornerreview.ReviewGameActivity"))
            .putExtra("dark",dark).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP)); settle()
    }
    private fun companion() { ctx.startActivity(Intent(ctx,MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)); settle() }
    private fun click(text: String) {
        assertTrue("Missing $text",device.wait(Until.hasObject(By.text(text)),15000))
        device.pressDPadLeft(); repeat(12) { device.pressDPadUp() }
        repeat(if(text == "Show over game") 3 else 2) { device.pressDPadDown() }
        device.pressDPadCenter(); settle()
    }
    private fun focus() = device.executeShellCommand("dumpsys window").lineSequence().firstOrNull { it.contains("mCurrentFocus=") }.orEmpty()
    private fun access(on: Boolean) {
        device.executeShellCommand("settings put secure enabled_accessibility_services ${if(on) "com.afc.companion/com.afc.companion.access.MenuHoldService" else "null"}")
        device.executeShellCommand("settings put secure accessibility_enabled ${if(on) 1 else 0}"); SystemClock.sleep(1800)
        var dump = device.executeShellCommand("dumpsys accessibility")
        val deadline = SystemClock.elapsedRealtime() + 15000
        while(on && !dump.substringAfter("Bound services:").substringBefore("Enabled services:").contains("capabilities=8") && SystemClock.elapsedRealtime() < deadline) {
            SystemClock.sleep(500)
            dump = device.executeShellCommand("dumpsys accessibility")
        }
        File(out,"access-${if(on) "on" else "off"}.txt").writeText(dump)
        if(on) assertTrue("Harness must preserve bound accessibility services", dump.substringAfter("Bound services:").substringBefore("Enabled services:").contains("capabilities=8"))
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
    @Test fun wireShapeAndRelease() {
        tagNfl = false
        installPeer(); SessionStore(ctx).save("synthetic-review-session")
        try {
            companion()
            ctx.stopService(Intent(ctx,OverlayService::class.java)); settle()
            device.executeShellCommand("appops set com.afc.companion SYSTEM_ALERT_WINDOW allow")
            access(true); game()
            hardwareMenu(1000, 4000)
            screenshot("18-nfl-wire-card-after-release")
            File(out,"wire-shape.txt").writeText("NFL fixture matches backend/src/panel/__init__.py: HalfPpr, no sport property. Physical Menu down duration 1000 ms, device remains present 4000 ms after up. Screenshot and separate foreground menu-events log are the behavioral oracle; UiAutomator does not expose nonfocusable overlay text reliably.\n")
        } finally {
            ctx.stopService(Intent(ctx,OverlayService::class.java)); access(false)
        }
    }
    @Test fun nativeFlows() {
        installPeer(); SessionStore(ctx).save("synthetic-review-session")
        try {
            ActivityScenario.launch(MainActivity::class.java).use {
                device.executeShellCommand("appops set com.afc.companion SYSTEM_ALERT_WINDOW allow")
                access(false); game(); companion(); click("Show over game")
                screenshot("01-service-off-card")
                check("service-off actual Show over game displays card",device.hasObject(By.text("112.5")))
                check("service-off hint visible",device.hasObject(By.text("Hold ≡ needs Accessibility")))
                check("plain card leaves game focused",focus().contains("ReviewGameActivity"))
                // Service-off card has no menu/Expand route; actual app screens are captured for review.
                companion(); click("Panel"); screenshot("02-service-off-in-app-panel")
                ctx.stopService(Intent(ctx,OverlayService::class.java)); settle(); access(true); game()
                hardwareMenu(150); screenshot("03-short-menu")
                check("short press does not start overlay",!focus().contains("com.afc.companion/com.afc.companion"))
                hardwareMenu(1000); screenshot("04-card-bright")
                check("first real hold shows card",device.hasObject(By.text("112.5")))
                check("card after hold leaves game focused",focus().contains("ReviewGameActivity"))
                game(true); screenshot("05-card-dark")
                hardwareMenu(1000); screenshot("06-menu")
                check("second hold opens menu",device.hasObject(By.text("Expand")))
                check("menu owns focus",focus().contains("com.afc.companion") && !focus().contains("ReviewGameActivity"))
                device.pressDPadCenter(); screenshot("07-expanded")
                check("Expand shows shared panel",device.hasObject(By.text("Team total: 112.5")))
                device.pressBack(); screenshot("08-back-to-game")
                check("Back from expanded returns focus to game",focus().contains("ReviewGameActivity"))
                device.pressDPadCenter(); screenshot("09-game-gets-ok")
                hardwareMenu(1000); device.pressDPadDown(); device.pressDPadCenter(); screenshot("10-league-switched")
                check("league menu stays open",device.hasObject(By.text("League: LeagueB")))
                check("league switch synthesizes LeagueB/TeamA",requests.any { it.contains("LeagueB%2FTeamA") })
                device.pressBack(); screenshot("11-back-from-menu")
                check("Back from menu returns focus to game",focus().contains("ReviewGameActivity"))
                // Restore original pair, start real card queue and inspect geometry during arrival and expiry.
                hardwareMenu(1000); device.pressDPadDown(); device.pressDPadCenter(); device.pressBack()
                OverlayServiceControl(ctx).startAlerts(); settle()
                val feed=AlertFeed(ApiClient("https://review.invalid")); AlertInbox.attach(feed); settle()
                publish(feed,"review-alert"); SystemClock.sleep(350); screenshot("12-card-plus-alert")
                SystemClock.sleep(5200); screenshot("13-alert-expired")
                // Companion's real key-down handler must not run for an AFC-owned hold.
                companion(); click("Panel"); screenshot("14-companion-panel-before-short")
                hardwareMenu(150); screenshot("15-companion-panel-after-short")
                check("short Menu reaches real Companion Panel",device.hasObject(By.text("Panel hidden. Press Menu to show it.")))
                hardwareMenu(1000); screenshot("16-companion-panel-after-hold")
                check("long Menu must leave underlying Panel hidden",device.hasObject(By.text("Panel hidden. Press Menu to show it.")))
                device.pressBack(); screenshot("17-companion-after-back")
            }
        } finally {
            File(out,"observations.txt").writeText(report.toString())
            File(out,"requests.txt").writeText(requests.joinToString("\n"))
            ctx.stopService(Intent(ctx,OverlayService::class.java)); AlertInbox.attach(null); access(false)
        }
    }
}

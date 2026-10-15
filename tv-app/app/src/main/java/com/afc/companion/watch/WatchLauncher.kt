package com.afc.companion.watch

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import com.afc.companion.net.ApiClient
import com.afc.companion.net.ProviderRoute
import com.afc.companion.net.RoutingOutcome
import com.afc.companion.net.RoutingOutcomeReport
import com.afc.companion.panel.PanelMode
import org.json.JSONObject

/** Fire OS side of a Watch launch. Its current-app report is untrusted: it never proves the game opened. */
interface LaunchPlatform {
    fun isInstalled(packageName: String): Boolean
    /** Starts one registry launch (`type` intent or uri); false when the platform refused it. */
    fun start(packageName: String, type: String, value: String): Boolean
    /** Package the platform reports in the foreground, or null. */
    fun currentApp(): String?
    /** Moves the companion app out of the foreground. */
    fun leaveApp()
}

/**
 * LAUNCHER (DES-AFC-P2-WATCH; CONTRACT-AFC-P2-PROVIDER-REGISTRY). Registry routes are untrusted:
 * only a `verified` own-platform (`fire_os`) entry with a well-formed package and intent|uri launch
 * is executed. No current-attempt observation mechanism is supported yet (P2-X03 pending), so a
 * started launch is `accessUnknown` whatever the registry's historical `verified_outcome` or the
 * platform's current-app report says; neither ever establishes `gameOpened` (RISK-AFC-P2-10).
 */
class WatchLauncher(private val platform: LaunchPlatform) {
    constructor(context: Context) : this(AndroidLaunchPlatform(context))

    /** No event id or client here, so no attempt can be reported; [watch] is the attempt path. */
    fun launch(route: ProviderRoute): RoutingOutcome = RoutingOutcome.AccessUnknown

    /**
     * One customer Watch attempt for [eventId]: executes only the route's `fire_os` entry and reports
     * exactly one RoutingOutcome through [client]. Null when the customer declined the switch (no attempt).
     */
    suspend fun watch(
        eventId: String,
        route: ProviderRoute,
        client: ApiClient,
        switchingConfirm: Boolean,
        mode: PanelMode,
        confirm: suspend () -> Boolean,
    ): RoutingOutcome? {
        if (switchingConfirm && !confirm()) return null
        var started = false
        val outcome = launchOnce(eventId, route) { started = true }
        client.reportRoutingOutcome(RoutingOutcomeReport(eventId, outcome))
        if (started && mode == PanelMode.FullScreen) platform.leaveApp()
        return outcome
    }

    /** Single pass: an uncertain outcome never relaunches (AFC-PR-031). */
    private fun launchOnce(eventId: String, route: ProviderRoute, onStarted: () -> Unit): RoutingOutcome {
        val entry = route.route?.optJSONObject("platform_routes")?.optJSONObject("fire_os")
            ?: return RoutingOutcome.AccessUnknown
        val launch = verifiedLaunch(eventId, route.channel, entry) ?: return RoutingOutcome.AccessUnknown
        if (!platform.isInstalled(launch.first)) return RoutingOutcome.AppAbsent
        if (!platform.start(launch.first, launch.second, launch.third)) return RoutingOutcome.PlaybackDenied
        onStarted()
        return RoutingOutcome.AccessUnknown
    }

    private fun verifiedLaunch(eventId: String, channel: String?, entry: JSONObject): Triple<String, String, String>? {
        if (entry.opt("status") != "verified") return null
        val packageName = (entry.opt("package") as? String)?.takeIf { PACKAGE.matches(it) } ?: return null
        val launch = entry.optJSONObject("launch") ?: return null
        val type = (launch.opt("type") as? String)?.takeIf { it == "intent" || it == "uri" } ?: return null
        val template = (launch.opt("value") as? String)?.takeIf { it.isNotEmpty() } ?: return null
        if ("{channel}" in template && channel.isNullOrEmpty()) return null
        val value = template.replace("{event}", eventId).replace("{channel}", channel.orEmpty())
        return Triple(packageName, type, value)
    }

    private companion object {
        val PACKAGE = Regex("^[A-Za-z0-9._]{1,255}$")
    }
}

/** Alexa-assisted tuning is offered only over an enabled, P2-X11-verified route (AFC-PR-036). */
fun alexaTuningOffered(voiceEnabled: Boolean, routeVerified: Boolean): Boolean = voiceEnabled && routeVerified

// shortcut: an intent value's "?query" suffix is dropped and currentApp() reports nothing until the
// P2-X03 stick verdict names the documented launch/observation forms; on-stick launch is DEVICE_INSTALL_PENDING.
private class AndroidLaunchPlatform(private val context: Context) : LaunchPlatform {
    override fun isInstalled(packageName: String): Boolean = try {
        @Suppress("DEPRECATION") context.packageManager.getPackageInfo(packageName, 0)
        true
    } catch (e: PackageManager.NameNotFoundException) {
        false
    }

    override fun start(packageName: String, type: String, value: String): Boolean {
        val intent = when (type) {
            "uri" -> Intent(Intent.ACTION_VIEW, Uri.parse(value))
            else -> Intent(value.substringBefore('?'))
        }.setPackage(packageName).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        return try {
            context.startActivity(intent)
            true
        } catch (e: ActivityNotFoundException) {
            false
        } catch (e: SecurityException) {
            false
        }
    }

    override fun currentApp(): String? = null

    override fun leaveApp() {
        (context as? Activity)?.moveTaskToBack(true)
    }
}

package com.afc.companion.watch

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import com.afc.companion.net.AccessBasis
import com.afc.companion.net.ApiClient
import com.afc.companion.net.ProviderRoute
import com.afc.companion.net.RoutingOutcome
import com.afc.companion.net.RoutingOutcomeReport
import com.afc.companion.panel.PanelMode
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.withContext
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
 * is executed. P2-X03 found no current-attempt observation mechanism (`currentAttemptObservation: none`), so a
 * started launch is `accessUnknown` whatever the registry's historical `verified_outcome` or the
 * platform's current-app report says; neither ever establishes `gameOpened` (RISK-AFC-P2-10).
 */
class WatchLauncher(private val platform: LaunchPlatform) {
    constructor(context: Context) : this(AndroidLaunchPlatform(context))

    /**
     * Watch on one alert (panel or notification): the alert's own resolved route when it carries one,
     * otherwise GET /v1/providers for [eventId]. An unresolvable route still runs [watch], which then
     * launches nothing and reports accessUnknown.
     */
    suspend fun watchAlert(
        eventId: String,
        alertRoute: ProviderRoute?,
        client: ApiClient,
        switchingConfirm: Boolean,
        mode: PanelMode,
        confirm: suspend () -> Boolean,
    ): RoutingOutcome? {
        val route = alertRoute?.takeIf { it.route != null } ?: try {
            client.getProvider(eventId).value
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            null
        } ?: ProviderRoute(null, null, null, AccessBasis.Unknown)
        return watch(eventId, route, client, switchingConfirm, mode, confirm)
    }

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
        // The launch already happened: neither a report failure nor the caller's cancellation (the provider
        // backgrounding the panel) may swallow its one report or the leave below.
        withContext(NonCancellable) {
            try {
                client.reportRoutingOutcome(RoutingOutcomeReport(eventId, outcome))
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                // Best-effort report; the known local outcome still stands.
            }
            if (started && mode == PanelMode.FullScreen) platform.leaveApp()
        }
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
        launchSpec(packageName, type, value) ?: return null
        return Triple(packageName, type, value)
    }

    private companion object {
        val PACKAGE = Regex("^[A-Za-z0-9._]{1,255}$")
    }
}

/** Alexa-assisted tuning is offered only over an enabled, P2-X11-verified route (AFC-PR-036). */
fun alexaTuningOffered(voiceEnabled: Boolean, routeVerified: Boolean): Boolean = voiceEnabled && routeVerified

/** The Intent one registry launch becomes; [data] is the VIEW URI, null for an `intent` action. */
internal data class LaunchSpec(val action: String, val data: String?, val packageName: String)

/**
 * Null for anything but a registry `uri` or `intent` launch. A bare MAIN with only a package does not
 * resolve on the stick (P2-X03), so it is never a launch.
 */
internal fun launchSpec(packageName: String, type: String, value: String): LaunchSpec? = when (type) {
    "uri" -> LaunchSpec(ACTION_VIEW, value, packageName)
    // shortcut: an intent value's "?query" suffix is dropped; carry it as extras once a registry intent route needs them.
    "intent" -> value.substringBefore('?').takeIf { it.isNotEmpty() && it != ACTION_MAIN }?.let { LaunchSpec(it, null, packageName) }
    else -> null
}

private const val ACTION_VIEW = "android.intent.action.VIEW"
private const val ACTION_MAIN = "android.intent.action.MAIN"

// currentApp() reports nothing: P2-X03 found no supported current-attempt observation on Fire OS.
private class AndroidLaunchPlatform(private val context: Context) : LaunchPlatform {
    override fun isInstalled(packageName: String): Boolean = try {
        @Suppress("DEPRECATION") context.packageManager.getPackageInfo(packageName, 0)
        true
    } catch (e: PackageManager.NameNotFoundException) {
        false
    }

    override fun start(packageName: String, type: String, value: String): Boolean {
        val spec = launchSpec(packageName, type, value) ?: return false
        val intent = Intent(spec.action).apply { spec.data?.let { data = Uri.parse(it) } }
            .setPackage(spec.packageName).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
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

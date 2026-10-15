package com.afc.companion.watch

import android.content.Context
import com.afc.companion.net.ApiClient
import com.afc.companion.net.ProviderRoute
import com.afc.companion.net.RoutingOutcome
import com.afc.companion.panel.PanelMode

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

// AFC-STUB: P2-A04 implements LAUNCHER (registry route to intent/URI); nothing launches, so nothing is verified.
class WatchLauncher(private val platform: LaunchPlatform) {
    // AFC-STUB: P2-A04 backs this with the Fire OS PackageManager / startActivity platform.
    constructor(context: Context) : this(Unlaunched)

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
    ): RoutingOutcome? = RoutingOutcome.AccessUnknown
}

// AFC-STUB: P2-A04 gates Alexa-assisted tuning on voice enablement and a P2-X11-verified route (AFC-PR-036).
fun alexaTuningOffered(voiceEnabled: Boolean, routeVerified: Boolean): Boolean = false

private object Unlaunched : LaunchPlatform {
    override fun isInstalled(packageName: String): Boolean = false
    override fun start(packageName: String, type: String, value: String): Boolean = false
    override fun currentApp(): String? = null
    override fun leaveApp() {}
}

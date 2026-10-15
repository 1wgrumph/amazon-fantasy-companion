package com.afc.companion.watch

import com.afc.companion.net.ProviderRoute
import org.json.JSONObject

/**
 * Synthetic route in the B06 wire shape (CONTRACT-AFC-P2-PROVIDER-REGISTRY: the whole platform_routes map,
 * each entry `verified` or REGISTRY_ROUTE_GAP). Not a provider document; registry.json on main is empty.
 */
internal const val PROVIDER_PACKAGE = "test.beta.firetv"
internal const val VEGA_PACKAGE = "test.beta.vega"
internal const val EVENT_ID = "evt-401"

internal fun fireOsEntry(
    packageName: String = PROVIDER_PACKAGE,
    type: String = "intent",
    value: String = "test.beta.firetv.WATCH?event={event}",
    verifiedOutcome: String = "gameOpened",
    status: String? = "verified",
): JSONObject = JSONObject()
    .put("package", packageName)
    .put("launch", JSONObject().put("type", type).put("value", value))
    .put("doc_source", "test fixture, not a provider document")
    .put("verified_outcome", verifiedOutcome)
    .put("verified_at", "2026-10-14T19:00:00Z")
    .put("currentAttemptObservation", "none")
    .apply { status?.let { put("status", it) } }

internal val vegaEntry: JSONObject get() = JSONObject()
    .put("package", VEGA_PACKAGE)
    .put("launch", JSONObject().put("type", "uri").put("value", "test-beta://watch/{event}"))
    .put("verified_outcome", "gameOpened").put("verified_at", "2026-10-14T19:30:00Z").put("status", "verified")

internal val gapEntry: JSONObject get() = JSONObject().put("status", "REGISTRY_ROUTE_GAP")

/** Decoded through the production ProviderRoute decoder, as the alert or GET /v1/providers delivers it. */
internal fun routeOf(fireOs: JSONObject = fireOsEntry(), vega: JSONObject = vegaEntry, channel: String? = "ESPN"): ProviderRoute {
    val json = JSONObject().put("provider", "beta_tv").put("accessBasis", "verified")
        .put("route", JSONObject().put("platform_routes", JSONObject().put("fire_os", fireOs).put("vega", vega)))
    channel?.let { json.put("channel", it) }
    return checkNotNull(ProviderRoute.from(json)) { "fixture route must decode" }
}

/**
 * Stand-in for the Fire OS launch platform: the real PackageManager / startActivity path needs the stick
 * (DEVICE_INSTALL_PENDING). Records every call in order so tests see what was launched and when.
 */
internal class RecordingPlatform(
    private val installed: Set<String> = setOf(PROVIDER_PACKAGE, VEGA_PACKAGE),
    private val accepts: Boolean = true,
    private val foreground: String? = null,
) : LaunchPlatform {
    val calls = mutableListOf<String>()
    val starts = mutableListOf<Triple<String, String, String>>()
    override fun isInstalled(packageName: String): Boolean = packageName in installed
    override fun start(packageName: String, type: String, value: String): Boolean {
        calls.add("start")
        starts.add(Triple(packageName, type, value))
        return accepts
    }
    override fun currentApp(): String? = foreground
    override fun leaveApp() { calls.add("leave") }
}

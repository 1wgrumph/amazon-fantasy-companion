package com.afc.companion.watch

import com.afc.companion.LocalApi
import com.afc.companion.net.AccessBasis
import com.afc.companion.net.Alert
import com.afc.companion.net.AlertsPage
import com.afc.companion.net.ApiClient
import com.afc.companion.net.ProviderRoute
import com.afc.companion.net.RoutingOutcome
import com.afc.companion.panel.PanelMode
import com.afc.companion.repo
import java.nio.file.Files
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * The alert's Watch (panel or notification WatchActivity) runs [WatchLauncher.watchAlert]: the alert's resolved
 * route, else GET /v1/providers for its event, executed through the real attempt path that reports exactly one
 * RoutingOutcome. P2-X03: Prime Video's verified fire_os route is VIEW https://watch.amazon.com/search.
 */
class WatchAlertTest {
    private val prime = "com.amazon.firebat"
    private val primeSearch = "https://watch.amazon.com/search"

    /** GET /v1/providers as the deployed resolver serves the P2-X03 registry (entry marked verified, vega a gap). */
    private val primeProviders: String = JSONObject()
        .put("provider", "prime_video").put("channel", "Prime Video").put("accessBasis", "unknown")
        .put("inputs", JSONObject().put("installed", true).put("localMarket", JSONObject.NULL))
        .put("route", JSONObject().put("platform_routes", JSONObject()
            .put("fire_os", JSONObject().put("package", prime)
                .put("launch", JSONObject().put("type", "uri").put("value", primeSearch))
                .put("verified_outcome", "searchOpened").put("verified_at", "2026-10-16T20:10:00Z")
                .put("currentAttemptObservation", "none").put("status", "verified"))
            .put("vega", JSONObject().put("status", "REGISTRY_ROUTE_GAP"))))
        .toString()

    /** backend/fixtures/alerts/red-zone.json: the deployed G4 alert shape, route unresolved at alert time. */
    private val serverAlert: Alert = checkNotNull(
        AlertsPage.from(JSONObject(String(Files.readAllBytes(repo.resolve("backend/fixtures/alerts/red-zone.json")), Charsets.UTF_8)))?.alerts?.single(),
    )
    private val serverEvent = "401999001770"

    private class Run(val outcome: RoutingOutcome?, val paths: List<String>, val reports: List<JSONObject>)

    private fun run(platform: RecordingPlatform, alertRoute: ProviderRoute?, vararg replies: Pair<Int, String>): Run = runBlocking {
        LocalApi(replies.toList()).use { api ->
            val outcome = WatchLauncher(platform).watchAlert(
                serverEvent, alertRoute, ApiClient(api.baseUrl, { "session-fixture" }), false, PanelMode.FullScreen,
            ) { true }
            Run(
                outcome,
                api.requests.map { "${it.method} ${it.path}" },
                api.requests.filter { it.path == "/v1/routing-outcome" }.map { JSONObject(it.body) },
            )
        }
    }

    @Test fun unresolvedAlertRouteIsResolvedThroughProvidersAndLaunchesTheVerifiedPrimeUri() {
        val platform = RecordingPlatform(installed = setOf(prime))
        val result = run(platform, serverAlert.route, 200 to primeProviders, 200 to "{}")
        assertEquals(listOf("GET /v1/providers?eventId=$serverEvent", "POST /v1/routing-outcome"), result.paths)
        assertEquals("the registry launch, never a bare package MAIN", listOf(Triple(prime, "uri", primeSearch)), platform.starts)
        assertEquals("no current-attempt observation: searchOpened is history, not this attempt", RoutingOutcome.AccessUnknown, result.outcome)
        assertEquals(1, result.reports.size)
        assertEquals(serverEvent, result.reports.single().getString("eventId"))
        assertEquals("accessUnknown", result.reports.single().getString("outcome"))
        assertEquals("fullScreen leaves the companion after a started launch", listOf("start", "leave"), platform.calls)
    }

    @Test fun alertCarryingAResolvedRouteIsLaunchedWithoutAnotherLookup() {
        val platform = RecordingPlatform(installed = setOf(prime))
        val inline = checkNotNull(ProviderRoute.from(JSONObject(primeProviders)))
        val result = run(platform, inline, 200 to "{}")
        assertEquals(listOf("POST /v1/routing-outcome"), result.paths)
        assertEquals(listOf(Triple(prime, "uri", primeSearch)), platform.starts)
    }

    @Test fun failedProviderLookupLaunchesNothingAndStillReportsOnce() {
        val platform = RecordingPlatform(installed = setOf(prime))
        val unavailable = 500 to """{"error":{"code":"internal","message":"unavailable"}}"""
        val result = run(platform, ProviderRoute(null, null, null, AccessBasis.Unknown), unavailable, 200 to "{}")
        assertTrue(platform.starts.isEmpty())
        assertEquals(RoutingOutcome.AccessUnknown, result.outcome)
        assertEquals(listOf("accessUnknown"), result.reports.map { it.getString("outcome") })
    }

    @Test fun registryBareMainIntentIsNeverLaunched() {
        val platform = RecordingPlatform()
        val bareMain = routeOf(fireOsEntry(type = "intent", value = "android.intent.action.MAIN"))
        val result = run(platform, bareMain, 200 to "{}")
        assertTrue("a package-only MAIN does not resolve on the stick (P2-X03)", platform.starts.isEmpty())
        assertEquals(listOf("accessUnknown"), result.reports.map { it.getString("outcome") })
    }

    @Test fun platformStartBuildsTheRegistryLaunchIntent() {
        assertEquals(LaunchSpec("android.intent.action.VIEW", primeSearch, prime), launchSpec(prime, "uri", primeSearch))
        assertEquals(LaunchSpec("test.beta.firetv.WATCH", null, PROVIDER_PACKAGE),
            launchSpec(PROVIDER_PACKAGE, "intent", "test.beta.firetv.WATCH?event=$EVENT_ID"))
        assertNull("bare MAIN", launchSpec(prime, "intent", "android.intent.action.MAIN"))
        assertNull("bare MAIN with a query", launchSpec(prime, "intent", "android.intent.action.MAIN?x=1"))
        assertNull("empty action", launchSpec(prime, "intent", "?event=1"))
        assertNull("unknown launch type", launchSpec(prime, "shell", "am start"))
    }
}

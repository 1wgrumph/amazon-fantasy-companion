package com.afc.companion.watch

import com.afc.companion.LocalApi
import com.afc.companion.net.ApiClient
import com.afc.companion.net.ProviderRoute
import com.afc.companion.net.RoutingOutcome
import com.afc.companion.panel.PanelMode
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * LAUNCHER (DES-AFC-P2-WATCH; AFC-PR-030, -031, -035, -036, -048). The route is untrusted registry data:
 * only a verified `fire_os` entry is executed, and neither a launch call, the registry's historical
 * verified_outcome nor the platform's current-app report establishes gameOpened.
 */
class WatchLauncherTest {
    private class Attempt(val outcome: RoutingOutcome?, val reports: List<JSONObject>, val confirmAsked: Int)

    private fun attempt(
        platform: RecordingPlatform,
        route: ProviderRoute = routeOf(),
        switchingConfirm: Boolean = false,
        confirmAnswer: Boolean = true,
        mode: PanelMode = PanelMode.ModeB,
        reply: Pair<Int, String> = 200 to "{}",
    ): Attempt = runBlocking {
        LocalApi(listOf(reply)).use { server ->
            var asked = 0
            val outcome = WatchLauncher(platform).watch(
                EVENT_ID, route, ApiClient(server.baseUrl, { "session-fixture" }), switchingConfirm, mode,
            ) { asked++; platform.calls.add("confirm"); confirmAnswer }
            val reports = server.requests.filter { it.method == "POST" && it.path == "/v1/routing-outcome" }.map { JSONObject(it.body) }
            Attempt(outcome, reports, asked)
        }
    }

    private fun assertSingleReport(expected: RoutingOutcome, attempt: Attempt) {
        assertEquals("exactly one RoutingOutcome reported for the attempt", 1, attempt.reports.size)
        assertEquals(EVENT_ID, attempt.reports.single().optString("eventId"))
        assertEquals(expected.wire, attempt.reports.single().optString("outcome"))
        assertEquals("shown outcome equals the reported one", expected, attempt.outcome)
    }

    @Test fun executesOnlyTheFireOsRegistryLaunch() {
        val platform = RecordingPlatform()
        attempt(platform)
        assertEquals(listOf(Triple(PROVIDER_PACKAGE, "intent", "test.beta.firetv.WATCH?event=$EVENT_ID")), platform.starts)
        assertTrue("never the other platform's launch data", platform.starts.none { it.first == VEGA_PACKAGE || it.third.startsWith("test-beta://") })
    }

    @Test fun channelPlaceholderIsFilledFromTheResolvedChannel() {
        val platform = RecordingPlatform()
        attempt(platform, routeOf(fireOsEntry(type = "uri", value = "test-beta-fire://channel/{channel}")))
        assertEquals(listOf(Triple(PROVIDER_PACKAGE, "uri", "test-beta-fire://channel/ESPN")), platform.starts)
    }

    @Test fun ownPlatformGapLaunchesNothingAndReportsAccessUnknown() {
        val platform = RecordingPlatform()
        val result = attempt(platform, routeOf(fireOs = gapEntry))
        assertTrue("a fire_os gap is never filled from vega", platform.starts.isEmpty())
        assertSingleReport(RoutingOutcome.AccessUnknown, result)
    }

    @Test fun unverifiedOrMalformedEntryIsNeverLaunched() {
        val untrusted = listOf(
            fireOsEntry(status = null),
            fireOsEntry(status = "pending"),
            fireOsEntry(packageName = "bad package;rm"),
            fireOsEntry(type = "shell"),
        )
        for (entry in untrusted) {
            val platform = RecordingPlatform(installed = setOf(PROVIDER_PACKAGE, "bad package;rm"))
            val result = attempt(platform, routeOf(fireOs = entry))
            assertTrue("untrusted entry not launched: $entry", platform.starts.isEmpty())
            assertSingleReport(RoutingOutcome.AccessUnknown, result)
        }
    }

    @Test fun missingPackageReportsAppAbsent() {
        val platform = RecordingPlatform(installed = emptySet())
        val result = attempt(platform)
        assertTrue("nothing launched for an absent app", platform.starts.isEmpty())
        assertSingleReport(RoutingOutcome.AppAbsent, result)
    }

    @Test fun refusedLaunchReportsPlaybackDenied() {
        val platform = RecordingPlatform(accepts = false)
        val result = attempt(platform)
        assertEquals(1, platform.starts.size)
        assertSingleReport(RoutingOutcome.PlaybackDenied, result)
    }

    /** Negative check: a prior registry gameOpened plus an unconfirmed current-app launch is accessUnknown. */
    @Test fun priorGameOpenedPlusUnconfirmedCurrentAppIsAccessUnknown() {
        val platform = RecordingPlatform(foreground = PROVIDER_PACKAGE)
        val result = attempt(platform, routeOf(fireOsEntry(verifiedOutcome = "gameOpened")))
        assertEquals("the launch was made", 1, platform.starts.size)
        assertNotEquals("never a reused gameOpened", RoutingOutcome.GameOpened, result.outcome)
        assertSingleReport(RoutingOutcome.AccessUnknown, result)
    }

    @Test fun historicalVerifiedOutcomeIsNeverTheCurrentOutcome() {
        for (historical in RoutingOutcome.entries) {
            val platform = RecordingPlatform()
            val result = attempt(platform, routeOf(fireOsEntry(verifiedOutcome = historical.wire)))
            assertEquals("launched for verified_outcome=${historical.wire}", 1, platform.starts.size)
            assertSingleReport(RoutingOutcome.AccessUnknown, result)
        }
    }

    @Test fun eachAttemptReportsExactlyOneOutcome() = runBlocking {
        LocalApi(listOf(200 to "{}")).use { server ->
            val client = ApiClient(server.baseUrl, { "session-fixture" })
            val cases = listOf(RecordingPlatform(installed = emptySet()), RecordingPlatform(accepts = false), RecordingPlatform())
            val outcomes = cases.map { WatchLauncher(it).watch(EVENT_ID, routeOf(), client, false, PanelMode.ModeB) { true } }
            val reported = server.requests.filter { it.path == "/v1/routing-outcome" }.map { JSONObject(it.body).optString("outcome") }
            assertEquals(listOf("appAbsent", "playbackDenied", "accessUnknown"), reported)
            assertEquals(reported, outcomes.map { it?.wire })
        }
    }

    @Test fun noRelaunchAfterUncertainOutcome() {
        val platform = RecordingPlatform()
        val result = attempt(platform, reply = 503 to """{"error":{"code":"unavailable","message":"try later"}}""")
        assertEquals("launched once, never again after an uncertain outcome", 1, platform.starts.size)
        assertSingleReport(RoutingOutcome.AccessUnknown, result)
    }

    @Test fun switchingConfirmationBlocksTheSwitchUntilConfirmed() {
        val platform = RecordingPlatform()
        val result = attempt(platform, switchingConfirm = true, confirmAnswer = false)
        assertEquals("confirmation asked", 1, result.confirmAsked)
        assertTrue("declined switch launches nothing", platform.starts.isEmpty())
        assertNull("declined switch is not an attempt", result.outcome)
        assertTrue(result.reports.isEmpty())
    }

    @Test fun confirmedSwitchLaunchesAfterConfirmation() {
        val platform = RecordingPlatform()
        val result = attempt(platform, switchingConfirm = true, confirmAnswer = true)
        assertEquals(listOf("confirm", "start"), platform.calls.filter { it != "leave" })
        assertSingleReport(RoutingOutcome.AccessUnknown, result)
    }

    @Test fun confirmationOffNeverAsks() {
        val platform = RecordingPlatform()
        val result = attempt(platform, switchingConfirm = false)
        assertEquals(0, result.confirmAsked)
        assertEquals(1, platform.starts.size)
    }

    @Test fun fullScreenWatchLeavesTheCompanionApp() {
        val platform = RecordingPlatform()
        attempt(platform, mode = PanelMode.FullScreen)
        assertEquals("provider launched, then the companion app leaves", listOf("start", "leave"), platform.calls)
        assertEquals(PROVIDER_PACKAGE, platform.starts.single().first)
    }

    @Test fun fullScreenFailedLaunchStaysToShowTheOutcome() {
        val platform = RecordingPlatform(installed = emptySet())
        val result = attempt(platform, mode = PanelMode.FullScreen)
        assertTrue("stays in the app to show appAbsent", "leave" !in platform.calls)
        assertSingleReport(RoutingOutcome.AppAbsent, result)
    }

    @Test fun alexaTuningHiddenWithoutVerifiedRoute() {
        assertEquals(false, alexaTuningOffered(voiceEnabled = true, routeVerified = false))
        assertEquals(false, alexaTuningOffered(voiceEnabled = false, routeVerified = false))
        assertEquals(false, alexaTuningOffered(voiceEnabled = false, routeVerified = true))
    }

    @Test fun alexaTuningOfferedOverEnabledVerifiedRoute() {
        assertEquals(true, alexaTuningOffered(voiceEnabled = true, routeVerified = true))
    }
}

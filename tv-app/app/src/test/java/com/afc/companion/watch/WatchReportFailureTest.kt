package com.afc.companion.watch

import com.afc.companion.net.ApiClient
import com.afc.companion.net.RoutingOutcome
import com.afc.companion.panel.PanelMode
import java.net.ConnectException
import java.net.HttpURLConnection
import java.net.URL
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * A04-REV-001 regression: a report transport failure must not swallow the locally computed
 * outcome or skip the full-screen leave after the provider launch already started.
 */
class WatchReportFailureTest {
    private fun failingClient(failure: Exception, invocations: IntArray): ApiClient =
        ApiClient("http://127.0.0.1:9", { "session-fixture" }, { _: URL ->
            invocations[0]++
            throw failure
        } as (URL) -> HttpURLConnection)

    @Test fun reportConnectFailureStillReturnsAccessUnknownAndLeavesFullScreen() = runBlocking {
        val platform = RecordingPlatform()
        val reports = intArrayOf(0)
        val outcome = WatchLauncher(platform).watch(
            EVENT_ID, routeOf(), failingClient(ConnectException("Connection refused"), reports),
            false, PanelMode.FullScreen,
        ) { true }
        assertEquals(RoutingOutcome.AccessUnknown, outcome)
        assertEquals("launched once, then left despite the report failure", listOf("start", "leave"), platform.calls)
        assertEquals("exactly one report invocation", 1, reports[0])
    }

    @Test fun reportConnectFailureStillReturnsFailedLaunchOutcome() = runBlocking {
        val platform = RecordingPlatform(installed = emptySet())
        val reports = intArrayOf(0)
        val outcome = WatchLauncher(platform).watch(
            EVENT_ID, routeOf(), failingClient(ConnectException("Connection refused"), reports),
            false, PanelMode.FullScreen,
        ) { true }
        assertEquals(RoutingOutcome.AppAbsent, outcome)
        assertTrue("failed launch stays to show the outcome", "leave" !in platform.calls)
        assertEquals(1, reports[0])
    }

    @Test fun reportCancellationStillPropagates() {
        val platform = RecordingPlatform()
        val reports = intArrayOf(0)
        assertThrows(CancellationException::class.java) {
            runBlocking {
                WatchLauncher(platform).watch(
                    EVENT_ID, routeOf(), failingClient(CancellationException("cancelled"), reports),
                    false, PanelMode.FullScreen,
                ) { true }
            }
        }
        assertEquals(1, reports[0])
    }
}

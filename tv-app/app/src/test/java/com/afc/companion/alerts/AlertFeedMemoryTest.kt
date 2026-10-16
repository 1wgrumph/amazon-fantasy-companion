package com.afc.companion.alerts

import com.afc.companion.LocalApi
import com.afc.companion.MemoryPrefs
import com.afc.companion.net.ApiClient
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

/** AlertService builds a new AlertFeed on every start; dismissals and progress survive it (stop/start, START_STICKY). */
class AlertFeedMemoryTest {
    @Test fun dismissedAlertStaysDismissedAndPollingResumesAtTheCursorAfterARestart() = runBlocking {
        val prefs = MemoryPrefs()
        // The second page replays the history, as a no-cursor poll does on the backend.
        LocalApi(listOf(page("c1", alertJson("a1"), alertJson("a2")), page("c2", alertJson("a1"), alertJson("a2"), alertJson("a3")))).use { api ->
            val client = ApiClient(api.baseUrl, { "session-fixture" })
            val first = AlertFeed(client, prefs)
            first.poll()
            first.dismiss("a1")

            val restarted = AlertFeed(client, prefs)
            assertEquals("c1", restarted.cursor)
            val delivered = restarted.poll()
            assertEquals("the restarted feed resumes after its last page", "/v1/alerts?cursor=c1", api.requests[1].path)
            assertEquals("a dismissed alert is never re-delivered", listOf("a2", "a3"), delivered.map { it.envelope.id })
            assertEquals(listOf("a2", "a3"), restarted.queue.map { it.envelope.id })
        }
    }

    @Test fun newerRevisionOfADismissedAlertIsStillDeliveredAfterARestart() = runBlocking {
        val prefs = MemoryPrefs()
        LocalApi(listOf(page("c1", alertJson("a1")), page("c2", alertJson("a1", revision = 2)))).use { api ->
            val client = ApiClient(api.baseUrl, { "session-fixture" })
            AlertFeed(client, prefs).apply { poll(); dismiss("a1") }
            assertEquals(listOf(2L), AlertFeed(client, prefs).poll().map { it.envelope.revision })
        }
    }

    @Test fun unreadableOrOversizedMemoryStartsFromTheBeginning() {
        val client = ApiClient("http://127.0.0.1:9", { "session-fixture" })
        val prefs = MemoryPrefs()
        prefs.edit().putString(AlertFeed.MEMORY_KEY, "{not json").apply()
        assertNull(AlertFeed(client, prefs).cursor)
        prefs.edit().putString(AlertFeed.MEMORY_KEY, """{"cursor":"${"x".repeat(AlertFeed.MAX_CURSOR_LENGTH + 1)}","dismissed":[]}""").apply()
        assertNull("a cursor over the contract's 256 characters is not sent", AlertFeed(client, prefs).cursor)
    }

    @Test fun rememberedDismissalsStayBoundedToTheQueueSize() = runBlocking {
        val prefs = MemoryPrefs()
        val ids = (1..AlertFeed.QUEUE_MAX + 5).map { "a$it" }
        LocalApi(listOf(page("c1", *ids.map { alertJson(it) }.toTypedArray()))).use { api ->
            val feed = AlertFeed(ApiClient(api.baseUrl, { "session-fixture" }), prefs)
            feed.poll()
            feed.queue.forEach { feed.dismiss(it.envelope.id) }
        }
        val stored = org.json.JSONObject(checkNotNull(prefs.getString(AlertFeed.MEMORY_KEY, null)))
        val kept = stored.getJSONArray("dismissed")
        assertEquals(AlertFeed.QUEUE_MAX, kept.length())
        assertEquals("the newest dismissal is kept", "a25", kept.getJSONObject(kept.length() - 1).getString("id"))
    }
}

package com.afc.companion.alerts

import com.afc.companion.LocalApi
import com.afc.companion.net.ApiClient
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

/** P2-X02 FAILS: AlertService hands its retained queue to the panel, which is the only alert surface on Fire OS. */
class AlertInboxTest {
    @After fun detach() = AlertInbox.attach(null)

    @Test fun panelSeesTheServiceQueueAndDismissAcknowledgesLocally() = runBlocking {
        LocalApi(listOf(page("c1", alertJson("a1"), alertJson("a2")))).use { api ->
            val feed = AlertFeed(ApiClient(api.baseUrl, { "session-fixture" }))
            AlertInbox.attach(feed)
            feed.poll()
            AlertInbox.publish()
            assertEquals(listOf("a1", "a2"), AlertInbox.alerts.value.map { it.envelope.id })
            assertEquals("a2", AlertInbox.find("a2")?.envelope?.id)
            AlertInbox.dismiss("a1")
            assertEquals(listOf("a2"), AlertInbox.alerts.value.map { it.envelope.id })
            assertEquals(listOf("a2"), feed.queue.map { it.envelope.id })
            assertEquals("dismiss sends nothing", 1, api.requests.size)
        }
    }

    @Test fun dismissWaitsForAnInFlightPublishSoAStaleQueueNeverOverwritesIt() = runBlocking {
        LocalApi(listOf(page("c1", alertJson("a1"), alertJson("a2")))).use { api ->
            val feed = AlertFeed(ApiClient(api.baseUrl, { "session-fixture" }))
            AlertInbox.attach(feed)
            feed.poll()
            val dismisser = Thread { AlertInbox.dismiss("a1") }
            // Holding the inbox lock stands in for a poll-thread publish that has read [a1, a2] but not written it.
            synchronized(AlertInbox) {
                dismisser.start()
                val deadline = System.nanoTime() + 5_000_000_000L
                while (dismisser.state != Thread.State.BLOCKED && dismisser.isAlive && System.nanoTime() < deadline) Thread.sleep(1)
                assertEquals("dismiss must not interleave with a publish", Thread.State.BLOCKED, dismisser.state)
            }
            dismisser.join(5_000)
            assertEquals(listOf("a2"), AlertInbox.alerts.value.map { it.envelope.id })
        }
    }

    @Test fun stoppedServiceClearsThePanelAlerts() = runBlocking {
        LocalApi(listOf(page("c1", alertJson("a1")))).use { api ->
            val feed = AlertFeed(ApiClient(api.baseUrl, { "session-fixture" }))
            AlertInbox.attach(feed)
            feed.poll()
            AlertInbox.publish()
            AlertInbox.attach(null)
            assertEquals(emptyList<String>(), AlertInbox.alerts.value.map { it.envelope.id })
            assertNull(AlertInbox.find("a1"))
        }
    }
}

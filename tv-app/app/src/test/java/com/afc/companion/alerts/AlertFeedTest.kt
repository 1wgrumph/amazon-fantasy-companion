package com.afc.companion.alerts

import com.afc.companion.LocalApi
import com.afc.companion.net.ApiClient
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * DES-AFC-P2-ALERTPATH ALERTSVC: GET /v1/alerts?cursor= long poll (cursor maxLength 256 in openapi.yaml),
 * queue and history bounded by alert_queue_max = 20 (AFC-PR-062), burst updates coalesced per alert (AFC-PR-061).
 * Pages are untrusted: a bad page delivers nothing and leaves the cursor where it was.
 */
class AlertFeedTest {
    private fun feed(api: LocalApi) = AlertFeed(ApiClient(api.baseUrl, { "session-fixture" }))
    private fun paths(api: LocalApi, expected: Int): List<String> {
        assertEquals("Missing behavior: alert long-poll requests sent", expected, api.requests.size)
        return api.requests.map { it.path }
    }

    @Test fun firstPollSendsNoCursorAndEachNextPollSendsTheReturnedCursor() = runBlocking {
        LocalApi(listOf(page("c1", alertJson("a1")), page("c2"), page("c3"))).use { api ->
            val feed = feed(api)
            assertEquals(listOf("a1"), feed.poll().map { it.envelope.id })
            assertEquals("cursor adopted from the page", "c1", feed.cursor)
            assertEquals("empty page delivers nothing", emptyList<String>(), feed.poll().map { it.envelope.id })
            feed.poll()
            assertEquals(listOf("/v1/alerts", "/v1/alerts?cursor=c1", "/v1/alerts?cursor=c2"), paths(api, 3))
            assertEquals("c3", feed.cursor)
        }
    }

    @Test fun invalidPageDeliversNothingAndKeepsTheCursor() = runBlocking {
        val broken = alertJson("a2").apply { remove("schemaVersion") }
        LocalApi(listOf(page("c1", alertJson("a1")), page("c2", alertJson("a3"), broken), page("c3"))).use { api ->
            val feed = feed(api)
            assertEquals(listOf("a1"), feed.poll().map { it.envelope.id })
            assertEquals("no partial page applied", emptyList<String>(), feed.poll().map { it.envelope.id })
            assertEquals("cursor not advanced past a rejected page", "c1", feed.cursor)
            feed.poll()
            assertEquals("/v1/alerts?cursor=c1", paths(api, 3)[2])
            assertEquals(listOf("a1"), feed.queue.map { it.envelope.id })
        }
    }

    @Test fun errorStatusDeliversNothingAndKeepsTheCursor() = runBlocking {
        val unauthenticated = 401 to """{"error":{"code":"unauthenticated","message":"session rejected"}}"""
        LocalApi(listOf(page("c1", alertJson("a1")), unauthenticated, page("c2"))).use { api ->
            val feed = feed(api)
            assertEquals(listOf("a1"), feed.poll().map { it.envelope.id })
            assertEquals(emptyList<String>(), feed.poll().map { it.envelope.id })
            assertEquals("c1", feed.cursor)
            feed.poll()
            assertEquals("/v1/alerts?cursor=c1", paths(api, 3)[2])
        }
    }

    @Test fun cursorLongerThanTheContractIsNotAdopted() = runBlocking {
        LocalApi(listOf(page("c1"), page("x".repeat(257), alertJson("a1")), page("c2"))).use { api ->
            val feed = feed(api)
            feed.poll()
            assertEquals("c1", feed.cursor)
            assertEquals("page with an out-of-contract cursor is rejected", emptyList<String>(), feed.poll().map { it.envelope.id })
            assertEquals("c1", feed.cursor)
            feed.poll()
            assertEquals("/v1/alerts?cursor=c1", paths(api, 3)[2])
        }
    }

    @Test fun queueKeepsAtMostTwentyNewestAlerts() = runBlocking {
        val first = (1..15).map { alertJson("a$it") }.toTypedArray()
        val second = (16..25).map { alertJson("a$it") }.toTypedArray()
        LocalApi(listOf(page("c1", *first), page("c2", *second))).use { api ->
            val feed = feed(api)
            assertEquals(15, feed.poll().size)
            assertEquals("each new alert delivered", (16..25).map { "a$it" }, feed.poll().map { it.envelope.id })
            assertEquals("alert_queue_max", 20, feed.queue.size)
            assertEquals("oldest evicted first", (6..25).map { "a$it" }.toSet(), feed.queue.map { it.envelope.id }.toSet())
        }
    }

    @Test fun burstUpdatesCoalesceToOneLatestRevisionPerAlert() = runBlocking {
        LocalApi(listOf(
            page("c1", alertJson("a1", 1), alertJson("a1", 2), alertJson("a2", 1)),
            page("c2", alertJson("a1", 2), alertJson("a2", 3)),
            page("c3", alertJson("a2", 1)),
        )).use { api ->
            val feed = feed(api)
            assertEquals("burst coalesced", mapOf("a1" to 2L, "a2" to 1L), feed.poll().associate { it.envelope.id to it.envelope.revision })
            assertEquals("only the changed alert is delivered", mapOf("a2" to 3L), feed.poll().associate { it.envelope.id to it.envelope.revision })
            assertEquals("older revision rejected", emptyList<String>(), feed.poll().map { it.envelope.id })
            assertEquals("one entry per alert at its newest revision", mapOf("a1" to 2L, "a2" to 3L),
                feed.queue.associate { it.envelope.id to it.envelope.revision })
            assertEquals(2, feed.queue.size)
        }
    }

    @Test fun dismissAcknowledgesLocallyWithoutABackendCall() = runBlocking {
        LocalApi(listOf(page("c1", alertJson("a1")))).use { api ->
            val feed = feed(api)
            feed.poll()
            assertTrue("held alert acknowledged", feed.dismiss("a1"))
            assertFalse("unknown alert is not acknowledged", feed.dismiss("a-unknown"))
            assertEquals("dismiss sends nothing", listOf("/v1/alerts"), paths(api, 1))
        }
    }
}

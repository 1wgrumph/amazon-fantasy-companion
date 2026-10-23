package com.afc.companion.panel

import kotlin.math.ceil
import kotlin.math.floor
import kotlin.math.min
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

// Resource group: none shared. Owner examples supply labels/numbers; time is monotonic and injected, never slept.
class AlertCardContractTest {
    private fun notice(id: String = "nba-1", player: String = "Edwards", value: Double = 20.0, sport: String = "NBA"): Any {
        val type = overlayType("AlertCardNotice")
        val constructor = type.constructors.singleOrNull {
            it.parameterTypes.toList() == listOf(String::class.java, String::class.java, Double::class.javaObjectType, String::class.java, String::class.java)
        } ?: throw AssertionError("Missing overlay API: AlertCardNotice(alertId: String, player: String, value: Double, sport: String, watchEventId: String)")
        return constructor.newInstance(id, player, value, sport, "event-$id")
    }

    private fun queue(): Any = overlayType("AlertCardQueue").getConstructor().newInstance()
    private fun current(queue: Any): Any? = overlayCall(queue, "getCurrent")
    private fun offer(queue: Any, card: Any, now: Long) { overlayCall(queue, "offer", card, now) }
    private fun advance(queue: Any, now: Long) { overlayCall(queue, "advance", now) }
    private fun id(queue: Any): Any? = current(queue)?.let { overlayCall(it, "getAlertId") }
    private fun cardBox(width: Int, height: Int): Box {
        val geometry = checkNotNull(overlayType("AlertCardGeometry").getField("INSTANCE").get(null))
        return overlayCall(geometry, "layout", width, height) as Box
    }

    @Test fun cardIsAnExactCompactSquareAtTheSafeTopRightCorner() {
        for ((width, height) in listOf(1920 to 1080, 1280 to 720, 3840 to 2160, 1919 to 1079)) {
            val card = cardBox(width, height)
            val side = min(width, height) / 6
            assertEquals("one-sixth of short side; 180 px at 1080p", side, card.width)
            assertEquals(side, card.height)
            assertEquals("top-right anchor", floor(width * 0.95).toInt(), card.right)
            assertEquals("safe top inset", ceil(height * 0.05).toInt(), card.top)
            assertTrue(card.left >= ceil(width * 0.05).toInt())
            assertTrue(card.bottom <= floor(height * 0.95).toInt())
            assertTrue("small footprint, under 2% of screen", card.width.toLong() * card.height * 100 <= width.toLong() * height * 2)
        }
    }

    @Test fun rightSidePanelMovesBelowTheCardWithAGapAndStaysInsideItsSafeZone() {
        for ((width, height) in listOf(1920 to 1080, 1280 to 720, 3840 to 2160, 1919 to 1079)) {
            val card = cardBox(width, height)
            val geometry = checkNotNull(overlayType("OverlayGeometry").getField("INSTANCE").get(null))
            val panel = overlayCall(geometry, "layoutWithAlertCard", width, height, card) as Box
            assertEquals("panel remains right anchored", floor(width * 0.95).toInt(), panel.right)
            assertTrue(panel.width > 0 && panel.width <= floor(width * 0.30).toInt())
            assertTrue(panel.height > 0)
            assertTrue(panel.left >= ceil(width * 0.05).toInt())
            assertTrue(panel.bottom <= floor(height * 0.95).toInt())
            assertTrue("one-percent vertical gap", panel.top >= card.bottom + ceil(height * 0.01).toInt())
            assertTrue("rectangles cannot intersect", panel.left >= card.right || panel.right <= card.left || panel.top >= card.bottom || panel.bottom <= card.top)
        }
    }

    @Test fun labelContainsOnlyThePlayerAndCompactNumber() {
        val text = checkNotNull(overlayType("AlertCardText").getField("INSTANCE").get(null))
        assertEquals("Edwards · 20 PTS", overlayCall(text, "label", "Edwards", 20.0))
        assertEquals("Edwards · 6.5 PTS", overlayCall(text, "label", "Edwards", 6.5))
        assertEquals("Edwards · -1.5 PTS", overlayCall(text, "label", "Edwards", -1.5))
        assertEquals("Edwards · 0 PTS", overlayCall(text, "label", "Edwards", 0.0))
    }

    @Test fun unsafeTextAndUnknownNumbersCannotBecomeAnAuthoritativeCardLabel() {
        val text = checkNotNull(overlayType("AlertCardText").getField("INSTANCE").get(null))
        for (player in listOf("Edwards will score", "Edwards on the field", "")) {
            assertNull("reuse the existing claim boundary", overlayCall(text, "label", player, 20.0))
        }
        for (number in listOf(Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY)) {
            assertEquals("no fabricated number", "Edwards · SCORE", overlayCall(text, "label", "Edwards", number))
        }
    }

    @Test fun firstAlertAppearsImmediatelyAndRetainsItsSmallSportMarkAndWatchReference() {
        val q = queue()
        offer(q, notice(), 0)
        val card = checkNotNull(current(q))
        assertEquals("nba-1", overlayCall(card, "getAlertId"))
        assertEquals("NBA", overlayCall(card, "getSport"))
        assertEquals("event-nba-1", overlayCall(card, "getWatchEventId"))
    }

    @Test fun cardAutoDismissesAtTenSecondsWithoutInput() {
        val q = queue()
        offer(q, notice(), 10_000)
        advance(q, 19_999)
        assertEquals("nba-1", id(q))
        advance(q, 20_000)
        assertNull(current(q))
    }

    @Test fun severalNbaAndNflAlertsQueueInArrivalOrderOneAtATime() {
        val q = queue()
        offer(q, notice("nba-1"), 0)
        offer(q, notice("nfl-2", "Receiver", 6.5, "NFL"), 1_000)
        offer(q, notice("nba-3"), 2_000)
        assertEquals("nba-1", id(q))
        advance(q, 9_999)
        assertEquals("nba-1", id(q))
        advance(q, 10_000)
        assertEquals("nfl-2", id(q))
        assertEquals("NFL", overlayCall(checkNotNull(current(q)), "getSport"))
        advance(q, 19_999)
        assertEquals("nfl-2", id(q))
        advance(q, 20_000)
        assertEquals("nba-3", id(q))
        advance(q, 30_000)
        assertNull(current(q))
    }

    @Test fun duplicateCurrentIdDoesNotRestartTheTimeoutOrDisplayAgain() {
        val q = queue()
        offer(q, notice(), 0)
        offer(q, notice(value = 21.0), 4_000)
        advance(q, 10_000)
        assertNull(current(q))
        offer(q, notice(value = 22.0), 11_000)
        assertNull("same ID stays deduplicated after dismissal", current(q))
    }

    @Test fun duplicateQueuedIdDoesNotProduceASecondCard() {
        val q = queue()
        offer(q, notice("first"), 0)
        offer(q, notice("second"), 1_000)
        offer(q, notice("second"), 2_000)
        advance(q, 10_000)
        assertEquals("second", id(q))
        advance(q, 20_000)
        assertNull(current(q))
    }

    @Test fun delayedTimerStillGivesTheNextQueuedCardTenSeconds() {
        val q = queue()
        offer(q, notice("first"), 0)
        offer(q, notice("second"), 1_000)
        advance(q, 100_000)
        assertEquals("second", id(q))
        advance(q, 109_999)
        assertEquals("second", id(q))
        advance(q, 110_000)
        assertNull(current(q))
    }

    @Test fun clearingTheSessionRemovesCurrentAndQueuedCardsAndResetsDeduplication() {
        val q = queue()
        offer(q, notice("first"), 0)
        offer(q, notice("second"), 1_000)
        overlayCall(q, "clear")
        assertNull(current(q))
        advance(q, 5_000)
        assertNull(current(q))
        offer(q, notice("first"), 6_000)
        assertEquals("first", id(q))
    }
}

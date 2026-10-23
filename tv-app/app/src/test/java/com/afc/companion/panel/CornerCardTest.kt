package com.afc.companion.panel

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.compositeOver
import com.afc.companion.profile.Sport
import com.afc.companion.ui.theme.TvPalette
import com.afc.companion.ui.theme.contrast
import kotlin.math.ceil
import kotlin.math.floor
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** The default over-the-game surface: a small semi-transparent top-right card that shares the corner with alerts. */
class CornerCardTest {
    private val screens = listOf(1920 to 1080, 1280 to 720, 3840 to 2160, 1919 to 1079)

    private fun assertInSafeZone(label: String, box: Box, width: Int, height: Int) {
        assertTrue("$label positive", box.width > 0 && box.height > 0)
        assertTrue("$label left", box.left >= ceil(width * 0.05).toInt())
        assertTrue("$label top", box.top >= ceil(height * 0.05).toInt())
        assertTrue("$label right", box.right <= floor(width * 0.95).toInt())
        assertTrue("$label bottom", box.bottom <= floor(height * 0.95).toInt())
    }

    private fun disjoint(a: Box, b: Box) = a.left >= b.right || a.right <= b.left || a.top >= b.bottom || a.bottom <= b.top

    @Test fun cardIsSmallAtTheSafeTopRightCorner() {
        for ((width, height) in screens) {
            val card = OverlayGeometry.cornerCard(width, height, null)
            assertInSafeZone("card", card, width, height)
            assertEquals("right anchored", floor(width * 0.95).toInt(), card.right)
            assertEquals("top anchored", ceil(height * 0.05).toInt(), card.top)
            assertTrue("under 2.5% of the picture", card.width.toLong() * card.height * 1000 <= width.toLong() * height * 25)
        }
        val hd = OverlayGeometry.cornerCard(1920, 1080, null)
        assertEquals(Box(1517, 54, 307, 129), hd)
    }

    @Test fun anAlertTakesTheCornerAndTheCardStacksJustBelowWithoutOverlap() {
        for ((width, height) in screens) {
            val alert = AlertCardGeometry.layout(width, height)
            val card = OverlayGeometry.cornerCard(width, height, alert)
            assertInSafeZone("stacked card", card, width, height)
            assertTrue("never overlaps the alert", disjoint(card, alert))
            assertEquals("just below, with the 1% gap", alert.bottom + ceil(height * 0.01).toInt(), card.top)
            assertEquals("same right edge", alert.right, card.right)
        }
    }

    @Test fun menuStacksBelowTheCardInBothCornerStatesWithoutOverlap() {
        for ((width, height) in screens) {
            val alert = AlertCardGeometry.layout(width, height)
            for (shownAlert in listOf(null, alert)) {
                val card = OverlayGeometry.cornerCard(width, height, shownAlert)
                val menu = OverlayGeometry.menu(width, height, card)
                assertInSafeZone("menu", menu, width, height)
                assertTrue("menu below card", disjoint(menu, card) && menu.top >= card.bottom)
                // With no alert the corner is free; an arriving alert first moves the card and menu (onCard) below it.
                if (shownAlert != null) assertTrue("menu clear of the alert", disjoint(menu, shownAlert))
                assertEquals(card.right, menu.right)
            }
        }
    }

    @Test fun backgroundOpacityIsBetweenSixtyAndSeventyFivePercent() {
        assertTrue(CornerCardStyle.BACKGROUND_ALPHA in 0.60f..0.75f)
        assertTrue("the focused menu is at least as opaque as the card", CornerCardStyle.MENU_ALPHA >= CornerCardStyle.BACKGROUND_ALPHA)
    }

    @Test fun cardTextStaysLegibleOverBrightAndDarkVideo() {
        val surface = Color(TvPalette.surfaceArgb)
        val text = Color(CornerCardStyle.TEXT_ARGB)
        for (video in listOf(Color.White, Color(0xFFFFF4C0), Color(0xFF7FD8FF), Color(0xFF2FE39A), Color.Black)) {
            for (windowAlpha in listOf(1f, 0.8f)) {
                val behind = surface.copy(alpha = CornerCardStyle.backgroundAlpha(windowAlpha) * windowAlpha).compositeOver(video)
                val ink = text.copy(alpha = windowAlpha).compositeOver(video)
                val ratio = contrast(ink, behind)
                assertTrue("composited text over $video at window alpha $windowAlpha: $ratio", ratio >= 4.5f)
            }
            val menu = surface.copy(alpha = CornerCardStyle.MENU_ALPHA).compositeOver(video)
            assertTrue(contrast(text, menu) >= 4.5f)
        }
        for (sport in Sport.entries) {
            val ratio = contrast(Color(TvPalette.onSportAccentArgb(sport)), Color(TvPalette.sportAccentArgb(sport)))
            assertTrue("opaque sport mark is legible on any video: $ratio", ratio >= 4.5f)
        }
    }

    @Test fun cardTextIsSportMatchupClockTotalAndLeaders() {
        val fresh = snap(teamLeague = "demo-nba/cle-phi-tonight", total = 121.75).copy(
            sport = "NBA",
            rows = listOf(
                PanelRow("1", "Donovan Mitchell", PanelValue(32.5, null, "live", AS_OF_MS), "Q3 4:12"),
                PanelRow("2", "Tyrese Maxey", PanelValue(28.0, null, "live", AS_OF_MS), "Q3 4:12"),
                PanelRow("3", "Joel Embiid", PanelValue(0.0, null, null, AS_OF_MS), "Q3 4:12"),
            ),
        )
        assertEquals("NBA · CLE @ PHI  Q3 4:12", CornerCardText.label(fresh, fresh.teamLeague))
        assertEquals("121.8 pts", CornerCardText.total(fresh))
        assertEquals("Mitchell 32.5   Maxey 28.0", CornerCardText.leaders(fresh))
        assertEquals("NBA", CornerCardText.sport(fresh))
        for (basis in listOf(ScoringBasis.YahooLeague, ScoringBasis.Ppr, ScoringBasis.HalfPpr)) {
            assertEquals("current NFL wire omits sport", "NFL", CornerCardText.sport(fresh.copy(sport = null, basis = basis)))
        }
        assertEquals("NBA", CornerCardText.sport(fresh.copy(sport = null, basis = ScoringBasis.NbaPoints)))
        assertNull(CornerCardText.sport(null))
    }

    @Test fun currentNflAndNbaWireShapesSupplyTheSport() {
        for (basis in listOf("yahooLeague", "ppr", "halfPpr")) {
            val decoded = requireNotNull(decodePanel(state(panelData(basis = basis)), nbaEnabled = true))
            assertNull("NFL backend omits the optional sport field", decoded.sport)
            assertEquals("NFL", CornerCardText.sport(decoded))
        }
        val nba = requireNotNull(decodePanel(state(panelData(basis = "nbaPoints").put("sport", "nba")), nbaEnabled = true))
        assertEquals("NBA", CornerCardText.sport(nba))
    }

    @Test fun switchedPairLabelStaysVisibleAfterItsSnapshotLoads() {
        val pairs = listOf("league-a/team-7", "league-b/team-8")
        val panel = PanelController(pairs, pairs.first(), true)
        for (pair in pairs) {
            assertNull("the new pair starts loading", panel.snapshot)
            assertEquals(pair.substringAfter('/'), CornerCardText.label(panel.snapshot, panel.teamLeague))
            panel.onFetched(snap(teamLeague = pair, total = 42.0), 0)
            assertTrue("the label survives loading", CornerCardText.label(panel.snapshot, panel.teamLeague).contains(pair.substringAfter('/')))
            assertEquals("the total is still shown separately", "42.0 pts", CornerCardText.total(panel.snapshot))
            panel.perform(PanelAction.NextTeamLeague, 0)
        }
        assertEquals("No team selected", CornerCardText.label(null, null))
    }

    @Test fun unknownTotalsShowADashNeverUnavailable() {
        assertEquals("– pts", CornerCardText.total(snap(total = null)))
        assertEquals("–", CornerCardText.total(null))
        assertEquals("", CornerCardText.leaders(null))
    }

    @Test fun serviceOffShowsAOneLineHintAndServiceOnShowsNone() {
        val hint = CornerCardText.hint(serviceEnabled = false)
        assertEquals("Hold ≡ needs Accessibility", hint)
        assertTrue("one short line", hint!!.length <= 28 && '\n' !in hint)
        assertNull(CornerCardText.hint(serviceEnabled = true))
    }
}

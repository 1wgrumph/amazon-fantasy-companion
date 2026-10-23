package com.afc.companion.panel

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** AFC-PR-039/-040/-045: values, basis, stale and unavailable labels, and the text-size floor. */
class PanelTextTest {
    private val stale = Regex("stale", RegexOption.IGNORE_CASE)
    private val unavailable = Regex("unavailable", RegexOption.IGNORE_CASE)
    private val zero = Regex("(^|[^0-9.])-?0(\\.0+)?([^0-9.]|$)")

    private fun v(x: Double?, asOf: Long? = AS_OF_MS, reason: String? = null) = PanelValue(x, reason ?: if (x == null) "feed withheld" else null, "live", asOf)

    @Test fun freshValueShowsTheNumberWithoutLabels() {
        val text = PanelText.value(v(12.3), AS_OF_MS + 59_999)
        assertEquals("12.3", text)
        assertFalse("under 60 s is not stale: '$text'", stale.containsMatchIn(text))
        assertFalse(unavailable.containsMatchIn(text))
    }

    @Test fun valueAtSixtySecondsIsLabeledStaleWithItsAge() {
        val atLimit = PanelText.value(v(12.3), AS_OF_MS + 60_000)
        assertTrue("stale_after is 60 s: '$atLimit'", stale.containsMatchIn(atLimit))
        val older = PanelText.value(v(12.3), AS_OF_MS + 75_000)
        assertTrue("stale label: '$older'", stale.containsMatchIn(older))
        assertTrue("stale value shows its age: '$older'", older.contains("75"))
        assertTrue("stale value still shows its points: '$older'", older.contains("12.3"))
    }

    @Test fun unknownValueIsLabeledUnavailableAndNeverZero() {
        val text = PanelText.value(v(null), AS_OF_MS)
        assertTrue("null with reason is labeled: '$text'", unavailable.containsMatchIn(text))
        assertFalse("null with reason is never rendered as zero: '$text'", zero.containsMatchIn(text))
    }

    @Test fun realZeroIsShownAsZero() {
        val text = PanelText.value(v(0.0), AS_OF_MS)
        assertTrue("a real zero is a value: '$text'", zero.containsMatchIn(text))
        assertFalse(unavailable.containsMatchIn(text))
    }

    @Test fun valueWithoutTimestampIsNeverShownAsFresh() {
        val text = PanelText.value(v(12.3, asOf = null), AS_OF_MS)
        assertTrue("an undated value is labeled: '$text'", stale.containsMatchIn(text) || unavailable.containsMatchIn(text))
    }

    @Test fun unknownGameStatusIsLabeledUnavailable() {
        assertEquals("Q2 08:14", PanelText.gameStatus("Q2 08:14"))
        assertTrue(unavailable.containsMatchIn(PanelText.gameStatus(null)))
    }

    @Test fun eachScoringBasisHasItsLabel() {
        assertEquals("Yahoo league scoring", PanelText.basis(ScoringBasis.YahooLeague))
        assertEquals("PPR", PanelText.basis(ScoringBasis.Ppr))
        assertEquals("Half-PPR", PanelText.basis(ScoringBasis.HalfPpr))
    }

    // 1 sp >= 1 px at any 1080p density >= mdpi; the on-stick screencap measurement is P2-A05's CMD-TEXT-SIZE-MEASURE.
    @Test fun tvTextShowsMatchupPointsAndNoInternalLabels() {
        assertEquals("CLE @ PHI", PanelText.matchup("demo-nba/cle-phi-tonight"))
        assertEquals("a lineup key shows only its sport, never the raw key", "NFL", PanelText.matchup("demo-nfl/my-lineup"))
        assertEquals("NBA", PanelText.matchup("demo-nba/my-lineup"))
        assertEquals("NBA", PanelText.matchup("nba-league/team-9"))
        assertEquals("a snapshot's sport names a key that has none", "NFL", PanelText.matchup("league-a/team-7", "NFL"))
        assertEquals("Lineup", PanelText.matchup("league-a/team-7"))
        assertEquals("NFL", PanelText.title(snap(teamLeague = "demo-nfl/my-lineup")))
        assertEquals("NBA · CLE @ PHI", PanelText.title(snap(teamLeague = "demo-nba/cle-phi-tonight").copy(sport = "NBA")))
        assertEquals("121.8", PanelText.points(v(121.75)))
        assertEquals("0.0", PanelText.points(v(0.0)))
        assertEquals("–", PanelText.points(v(null)))
    }

    @Test fun weekdayStartsAndByesDoNotHideTheLiveClock() {
        val live = PanelRow("live", "Live Player", v(3.0), "Q2 08:14")
        for (status in listOf("Sun 12:00 PM", "Mon 7:15 PM", "BYE")) {
            val snapshot = snap(teamLeague = "demo-nfl/my-lineup").copy(rows = listOf(
                PanelRow("waiting", "Waiting Player", v(0.0), status), live,
            ))
            assertEquals("Q2 08:14", PanelText.clock(snapshot))
            assertEquals("NFL  Q2 08:14", CornerCardText.label(snapshot, snapshot.teamLeague))
        }
    }

    @Test fun shortNameIsFirstInitialAndLastName() {
        assertEquals("D. Mitchell", PanelText.shortName("Donovan Mitchell"))
        assertEquals("S. Gilgeous-Alexander", PanelText.shortName("Shai Gilgeous-Alexander"))
        assertEquals("K. Williams Jr.", PanelText.shortName("Kenrich Williams Jr."))
        assertEquals("Nene", PanelText.shortName(" Nene "))
    }

    @Test fun rowsSortByPointsHighestFirst() {
        fun row(id: String, points: Double?) = PanelRow(id, id, v(points), null)
        val sorted = PanelText.byPoints(listOf(row("a", 3.0), row("b", null), row("c", 12.5), row("d", 0.0)))
        assertEquals(listOf("c", "a", "d", "b"), sorted.map { it.playerId })
    }

    @Test fun textSizesMeetTheCouchFloor() {
        assertTrue("body text >= 24 px at 1080p: ${PanelTextSizes.bodySp} sp", PanelTextSizes.bodySp >= 24f)
        assertTrue("scores >= 32 px at 1080p: ${PanelTextSizes.scoreSp} sp", PanelTextSizes.scoreSp >= 32f)
    }
}

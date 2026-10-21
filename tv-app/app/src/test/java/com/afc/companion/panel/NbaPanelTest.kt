package com.afc.companion.panel

import com.afc.companion.BuildConfig
import java.io.File
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

// M16 NBA stretch (#137), TV side. Seam: decodePanel(state, nbaEnabled = BuildConfig.AFC_ENABLE_NBA), so both flag
// states are exercised without a rebuild. The optional `sport` field travels in the panel `data` object beside
// `scoringBasis`; the shared CONTRACT-AFC-P2-ENVELOPE is unchanged.

/** NBA panel rows behind AFC_ENABLE_NBA: flag off keeps every NFL decode and render as today. */
class NbaPanelTest {
    private fun nbaData(rows: List<JSONObject>? = null, basis: String = "nbaPoints", sport: Any? = null): JSONObject {
        val data = if (rows == null) panelData(basis = basis) else panelData(rows = rows, basis = basis)
        return if (sport == null) data else data.put("sport", sport)
    }

    private fun nba(data: JSONObject = nbaData()): PanelSnapshot {
        val snapshot = decodePanel(state(data), nbaEnabled = true)
        assertNotNull("Missing behavior: with AFC_ENABLE_NBA on, an NBA panel decodes", snapshot)
        return snapshot!!
    }

    // Item 1: the shipped default is on. -PafcEnableNba=false is the kill switch, and the
    // default decode follows the flag this build compiled.

    @Test fun flagDefaultsOnAndTheDefaultDecodeFollowsTheBuildFlag() {
        val gradle = File(System.getProperty("afc.repoRoot"), "tv-app/app/build.gradle.kts").readText()
        assertTrue(
            "AFC_ENABLE_NBA defaults on unless -PafcEnableNba=false",
            gradle.contains("providers.gradleProperty(\"afcEnableNba\").getOrElse(\"true\")"),
        )
        val nba = decodePanel(state(nbaData()))
        if (BuildConfig.AFC_ENABLE_NBA) {
            assertNotNull("the default decode follows the build flag", nba)
        } else {
            assertNull("the kill switch makes the default decode reject NBA", nba)
        }
        assertNotNull("NFL still decodes with the default flag", decodePanel(state()))
    }

    // Item 2: flag on.

    @Test fun nbaPointsBasisDecodesWithTheNbaLabel() {
        val s = nba()
        assertEquals(ScoringBasis.NbaPoints, s.basis)
        assertEquals("NBA", s.sport)
    }

    @Test fun sportFieldSetsTheLabelForAYahooNbaLeague() {
        val s = nba(nbaData(basis = "yahooLeague", sport = "nba"))
        assertEquals(ScoringBasis.YahooLeague, s.basis)
        assertEquals("NBA", s.sport)
        assertEquals("NBA", nba(nbaData(sport = "nba")).sport)
        assertEquals("NFL", nba(nbaData(basis = "ppr", sport = "nfl")).sport)
    }

    @Test fun unknownOrMalformedSportRejectsTheWholeState() {
        assertNull("an unknown sport is not guessed", decodePanel(state(nbaData(sport = "mlb")), nbaEnabled = true))
        assertNull("sport is case-exact on the wire", decodePanel(state(nbaData(sport = "NBA")), nbaEnabled = true))
        assertNull("a non-string sport is malformed", decodePanel(state(nbaData(sport = 5)), nbaEnabled = true))
        assertNull("NBA points under an NFL label contradict each other",
            decodePanel(state(nbaData(sport = "nfl")), nbaEnabled = true))
    }

    @Test fun nbaHeaderIsDistinctFromEveryNflHeader() {
        assertEquals("NBA · Points · Live", PanelText.header(nba()))
        assertEquals("NBA · Yahoo league scoring · Live", PanelText.header(nba(nbaData(basis = "yahooLeague", sport = "nba"))))
        val nflBasis = listOf(ScoringBasis.YahooLeague, ScoringBasis.Ppr, ScoringBasis.HalfPpr).map(PanelText::basis)
        val nbaBasis = PanelText.basis(ScoringBasis.NbaPoints)
        assertTrue("NBA points basis has text", nbaBasis.isNotBlank())
        assertFalse("NBA points basis text '$nbaBasis' differs from NFL $nflBasis", nbaBasis in nflBasis)
    }

    // Item 3: flag off is today's behavior, and flag on does not change an NFL panel without a sport field.

    @Test fun flagOffRejectsNbaAndIgnoresSport() {
        assertNull("nbaPoints is unknown with the flag off", decodePanel(state(nbaData()), nbaEnabled = false))
        assertNull(decodePanel(state(nbaData(sport = "nba")), nbaEnabled = false))
        val plain = decodePanel(state(), nbaEnabled = false)
        assertNotNull(plain)
        for (sport in listOf("nba", "nfl", "mlb", 5)) {
            val tagged = decodePanel(state(panelData().put("sport", sport)), nbaEnabled = false)
            assertEquals("sport=$sport is ignored with the flag off", plain, tagged)
        }
        assertNull("no sport label with the flag off", plain!!.sport)
        assertEquals("Half-PPR · Live", PanelText.header(plain))
    }

    @Test fun nflDecodeAndRenderMatchAcrossFlagStates() {
        for (basis in listOf("yahooLeague", "ppr", "halfPpr")) {
            val off = decodePanel(state(panelData(basis = basis)), nbaEnabled = false)
            val on = decodePanel(state(panelData(basis = basis)), nbaEnabled = true)
            assertNotNull(basis, off)
            assertEquals("$basis decodes the same with the flag on", off, on)
            assertNull("$basis without a sport field has no sport label", on!!.sport)
            assertEquals(PanelText.header(off!!), PanelText.header(on))
        }
        assertEquals("Yahoo league scoring · Live", PanelText.header(decodePanel(state(panelData(basis = "yahooLeague")), nbaEnabled = true)!!))
        assertEquals("PPR · Live", PanelText.header(decodePanel(state(panelData(basis = "ppr")), nbaEnabled = true)!!))
    }

    // Item 4: rows, total, progress, unknown values and the row bound are unchanged for NBA.

    @Test fun nbaRowsTotalAndProgressDecodeLikeNfl() {
        val s = nba()
        assertEquals(TL, s.teamLeague)
        assertEquals(listOf("p-11", "p-23", "p-31"), s.rows.map { it.playerId })
        assertEquals(12.3, s.rows[0].points.value!!, 1e-9)
        assertEquals(10.8, s.teamTotal.value!!, 1e-9)
        assertEquals(0.5, s.progress.value!!, 1e-9)
    }

    @Test fun nbaNullValueKeepsItsReasonAndIsNeverZero() {
        val unknown = nba().rows[2]
        assertNull("unknown NBA points stay null, never 0.0", unknown.points.value)
        assertEquals("feed withheld", unknown.points.reason)
        assertEquals("Unavailable", PanelText.value(unknown.points, AS_OF_MS))
        val malformed = nba(nbaData(rows = listOf(row("p-11", "Player Eleven", value("12")))))
        assertNull("a non-numeric NBA value is unknown, never coerced", malformed.rows[0].points.value)
        assertFalse(malformed.rows[0].points.reason.isNullOrBlank())
    }

    @Test fun nbaRowCountIsBoundedByTheDeclaredLimit() {
        val atLimit = nbaData(rows = (1..PANEL_ROWS_MAX).map { row("p-$it", "Player $it", value(1.0)) })
        assertEquals(PANEL_ROWS_MAX, decodePanel(state(atLimit), nbaEnabled = true)?.rows?.size)
        val over = nbaData(rows = (0..PANEL_ROWS_MAX).map { row("p-$it", "Player $it", value(1.0)) })
        assertNull("more than PANEL_ROWS_MAX NBA rows rejects the state", decodePanel(state(over), nbaEnabled = true))
    }
}

package com.afc.companion.panel

import com.afc.companion.net.ApiClient
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** AFC-PR-039/-040/-044/-062: GET /v1/panel data is untrusted; rows, total, progress and basis decode or nothing does. */
class PanelDecodeTest {
    private fun decoded(data: JSONObject = panelData()): PanelSnapshot {
        val snapshot = decodePanel(state(data))
        assertNotNull("Missing behavior: PanelState data decodes", snapshot)
        return snapshot!!
    }

    @Test fun rowsTotalProgressAndBasisDecode() {
        val s = decoded()
        assertEquals(TL, s.teamLeague)
        assertEquals(7L, s.revision)
        assertEquals(ScoringBasis.HalfPpr, s.basis)
        assertEquals(listOf("p-11", "p-23", "p-31"), s.rows.map { it.playerId })
        assertEquals("Player Eleven", s.rows[0].name)
        assertEquals(12.3, s.rows[0].points.value!!, 1e-9)
        assertEquals("negative fantasy points are real values", -1.5, s.rows[1].points.value!!, 1e-9)
        assertEquals("Q2 08:14", s.rows[0].gameStatus)
        assertEquals("live", s.rows[0].points.source)
        assertEquals(AS_OF_MS, s.rows[0].points.asOfMs)
        assertEquals(10.8, s.teamTotal.value!!, 1e-9)
        assertEquals(0.5, s.progress.value!!, 1e-9)
    }

    @Test fun eachScoringBasisDecodes() {
        val expected = mapOf("yahooLeague" to ScoringBasis.YahooLeague, "ppr" to ScoringBasis.Ppr, "halfPpr" to ScoringBasis.HalfPpr)
        for ((wire, basis) in expected) assertEquals(wire, basis, decodePanel(state(panelData(basis = wire)))?.basis)
    }

    @Test fun nullPointsKeepTheirReasonAndAreNotZero() {
        val unknown = decoded().rows[2]
        assertNull("unknown points stay null, never 0.0", unknown.points.value)
        assertEquals("feed withheld", unknown.points.reason)
        assertNull("unknown game status stays null", unknown.gameStatus)
    }

    @Test fun malformedValueBecomesUnavailableNotZero() {
        val data = panelData(rows = listOf(
            row("p-11", "Player Eleven", value("12")),
            row("p-23", "Player Twenty-Three", JSONObject()),
        ), progress = value(1.7))
        val s = decoded(data)
        for (r in s.rows) {
            assertNull("${r.playerId}: a non-numeric or absent value is unknown, never coerced", r.points.value)
            assertTrue("${r.playerId}: an unknown value carries a reason", !r.points.reason.isNullOrBlank())
        }
        assertNull("progress outside 0..1 is not shown", s.progress.value)
        assertTrue("rejected progress carries a reason", !s.progress.reason.isNullOrBlank())
    }

    @Test fun missingOrUnknownBasisRejectsTheWholeState() {
        assertNull("no value is shown without its scoring basis", decodePanel(state(panelData(basis = null))))
        assertNull("an unknown basis is not guessed", decodePanel(state(panelData(basis = "standard"))))
        assertNotNull("Missing behavior: a known basis decodes", decodePanel(state(panelData(basis = "ppr"))))
    }

    @Test fun malformedRowsRejectTheState() {
        assertNotNull("Missing behavior: a well-formed state decodes", decodePanel(state()))
        val noId = panelData(rows = listOf(JSONObject().put("name", "No Id").put("points", value(1.0))))
        assertNull("a row without a player ID is malformed", decodePanel(state(noId)))
        val duplicate = panelData(rows = listOf(row("p-11", "A", value(1.0)), row("p-11", "B", value(2.0))))
        assertNull("duplicate player IDs are malformed", decodePanel(state(duplicate)))
        assertNull("rows must be an array", decodePanel(state(panelData().put("rows", "p-11"))))
    }

    @Test fun rowCountIsBoundedByTheDeclaredLimit() {
        assertTrue("PANEL_ROWS_MAX declares room for a full lineup and stays small: $PANEL_ROWS_MAX", PANEL_ROWS_MAX in 20..64)
        val atLimit = panelData(rows = (1..PANEL_ROWS_MAX).map { row("p-$it", "Player $it", value(1.0)) })
        assertEquals(PANEL_ROWS_MAX, decodePanel(state(atLimit))?.rows?.size)
        val over = panelData(rows = (1..PANEL_ROWS_MAX + 1).map { row("p-$it", "Player $it", value(1.0)) })
        assertNull("a state above the row bound is rejected, not retained", decodePanel(state(over)))
    }

    @Test fun panelFeedDecodesOverTheApiClientForTheSelectedTeamLeague() = runBlocking {
        PanelServer(envelope(panelData())).use { server ->
            val result = ApiClient(server.baseUrl, { "session-fixture" }).getPanel(TL)
            assertEquals(200, result.status)
            assertEquals("teamLeague=league-a%2Fteam-7", server.queries.single())
            val s = decodePanel(result.value!!)
            assertNotNull("Missing behavior: the fetched PanelState decodes", s)
            assertEquals(3, s!!.rows.size)
        }
    }
}

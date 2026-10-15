package com.afc.companion.panel

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * P2-A05 repair regressions (A05-R02, A05-R04). The frozen A05T tests stay
 * byte-identical; host-testable repair behavior lives here. A05-R01/R03 are
 * Compose wiring (PanelContent parameters and the 1 s invalidation tick in
 * LineupPanel) and are verified by compiled-source inspection in the P2-A05
 * repair evidence; no host Compose renderer exists in this suite.
 */
class PanelRepairTest {
    private val stale = Regex("stale|unavailable", RegexOption.IGNORE_CASE)

    // A05-R04: an RFC3339 offset outside 00-23:00-59 is invalid; the value is
    // undated, so PanelText can never render it as fresh.
    @Test fun invalidTimezoneOffsetIsUndatedAndNeverFresh() {
        for (bad in listOf("2026-10-15T20:00:00-99:99", "2026-10-15T20:00:00+24:00", "2026-10-15T20:00:00-00:60")) {
            val decoded = decodePanel(state(panelData(total = value(12.3, asOf = bad))))
            assertNotNull("envelope still decodes: $bad", decoded)
            assertNull("invalid offset must not yield a timestamp: $bad", decoded!!.teamTotal.asOfMs)
            val text = PanelText.value(decoded.teamTotal, AS_OF_MS)
            assertTrue("invalid asOf is never fresh: $bad -> '$text'", stale.containsMatchIn(text))
        }
    }

    @Test fun validTimezoneOffsetsStillParse() {
        val decoded = decodePanel(state(panelData(total = value(12.3, asOf = "2026-10-15T15:00:00-05:00"))))
        assertEquals(AS_OF_MS, decoded!!.teamTotal.asOfMs)
        val text = PanelText.value(decoded.teamTotal, AS_OF_MS)
        assertFalse("a valid fresh value carries no label: '$text'", stale.containsMatchIn(text))
    }

    // A05-R02: the profile holds exactly one team/league pair, so the switch
    // list has one entry; pressing switch must keep the held rows and must
    // not refetch the team it already shows.
    @Test fun switchingWithOneTeamLeagueKeepsRowsAndDoesNotRefetch() {
        val c = PanelController(listOf(TL), TL, true)
        c.onFetched(snap(), 0)
        c.perform(PanelAction.NextTeamLeague, 1_000)
        assertEquals(TL, c.teamLeague)
        assertNotNull("a one-choice switch must not clear the rows", c.snapshot)
        assertFalse("a one-choice switch must not refetch the same team", c.shouldFetch(1_000))
    }
}

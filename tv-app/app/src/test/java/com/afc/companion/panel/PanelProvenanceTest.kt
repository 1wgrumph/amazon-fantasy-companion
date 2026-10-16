package com.afc.companion.panel

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** G3 M5 regression: lineup source and live/replay value provenance are rendered. */
class PanelProvenanceTest {
    @Test fun liveAndReplayValuesAreDistinct() {
        val live = PanelText.value(PanelValue(1.0, null, "live", AS_OF_MS), AS_OF_MS + 5_000)
        val replay = PanelText.value(PanelValue(1.0, null, "replay", AS_OF_MS), AS_OF_MS + 5_000)
        assertTrue("live labeled: $live", live.contains("live", ignoreCase = true))
        assertTrue("replay labeled: $replay", replay.contains("replay", ignoreCase = true))
        assertNotEquals(live, replay)
    }

    @Test fun manualAndYahooLineupSourcesAreDistinct() {
        assertNotEquals(PanelText.lineupSource("manual"), PanelText.lineupSource("yahoo"))
        assertTrue(PanelText.lineupSource("manual").contains("manual", ignoreCase = true))
        assertTrue(PanelText.lineupSource("yahoo").contains("yahoo", ignoreCase = true))
    }

    @Test fun decodedSnapshotCarriesEnvelopeSource() {
        val manualEnv = envelope(panelData()).put("source", "manual")
        val snapshot = decodePanel(requireNotNull(com.afc.companion.net.PanelState.from(manualEnv)))
        assertNotNull(snapshot)
        assertEquals("manual", snapshot!!.source)
        val yahooEnv = envelope(panelData()).put("source", "yahoo")
        assertEquals("yahoo", decodePanel(requireNotNull(com.afc.companion.net.PanelState.from(yahooEnv)))!!.source)
    }

    @Test fun replayPayloadFromG3RendersReplayOnRowTotalAndProgress() {
        val data = panelData(
            rows = listOf(row("9000001", "Sample 1", value(1.0, source = "replay"))),
            total = value(1.0, source = "replay"), progress = value(0.5, source = "replay"),
        )
        val snapshot = decodePanel(state(data))!!
        for (v in listOf(snapshot.rows[0].points, snapshot.teamTotal, snapshot.progress)) {
            assertTrue("replay labeled", PanelText.value(v, AS_OF_MS + 5_000).contains("replay", ignoreCase = true))
        }
    }
}

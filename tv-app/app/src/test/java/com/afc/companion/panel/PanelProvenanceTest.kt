package com.afc.companion.panel

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** G3 M5 regression: lineup source and live/replay value provenance are rendered. */
class PanelProvenanceTest {
    // F3: only the non-default provenance is labeled; a fresh live value is the bare number.
    @Test fun liveAndReplayValuesAreDistinct() {
        val live = PanelText.value(PanelValue(1.0, null, "live", AS_OF_MS), AS_OF_MS + 5_000)
        val replay = PanelText.value(PanelValue(1.0, null, "replay", AS_OF_MS), AS_OF_MS + 5_000)
        assertEquals("1.0", live)
        assertEquals("1.0 (replay)", replay)
        assertNotEquals(live, replay)
    }

    // F3: a stale live value never reads "live, stale".
    @Test fun staleLiveValueCarriesOnlyTheStaleLabel() {
        val staleLive = PanelText.value(PanelValue(1.0, null, "live", AS_OF_MS), AS_OF_MS + 75_000)
        assertEquals("1.0 (stale 75s)", staleLive)
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

    // F5: every lineup-source input has its label, including live/replay envelopes and unknown values.
    @Test fun lineupSourceLabelsCoverLiveReplayAndUnknown() {
        assertEquals("Manual lineup", PanelText.lineupSource("manual"))
        assertEquals("Yahoo lineup", PanelText.lineupSource("yahoo"))
        assertEquals("Live", PanelText.lineupSource("live"))
        assertEquals("Replay", PanelText.lineupSource("replay"))
        assertEquals("Source unavailable", PanelText.lineupSource("something-else"))
    }

    // F5: the LineupPanel header line is basis beside lineup source.
    @Test fun headerShowsBasisBesideLineupSource() {
        val snapshot = decodePanel(state(panelData()))!!.copy(source = "manual")
        assertEquals("Half-PPR · Manual lineup", PanelText.header(snapshot))
        assertEquals("Half-PPR · Live", PanelText.header(snapshot.copy(source = "live")))
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

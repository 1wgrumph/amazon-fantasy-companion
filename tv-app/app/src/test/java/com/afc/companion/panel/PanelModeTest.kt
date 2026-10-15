package com.afc.companion.panel

import kotlin.math.abs
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** AFC-PR-041/-047: the P2-X04 verdict fixes the mode; modeB leaves the video unobscured at its aspect ratio. */
class PanelModeTest {
    @Test fun onlyAModeBVerdictSelectsModeB() {
        assertEquals(PanelMode.ModeB, panelModeFor("modeB"))
        for (other in listOf(null, "", "fullScreen", "partial", "timebox", "MODEB", "modeB "))
            assertEquals("verdict '$other'", PanelMode.FullScreen, panelModeFor(other))
    }

    @Test fun fullScreenHostsThePanelAloneWithNoStandInVideo() {
        val layout = panelLayout(PanelMode.FullScreen, 1920, 1080)
        assertNull("no stand-in video in fullScreen", layout.video)
        assertEquals(Box(0, 0, 1920, 1080), layout.panel)
    }

    @Test fun modeBPutsThePanelRightAndFitsTheVideoLeftAtItsAspect() {
        val layout = panelLayout(PanelMode.ModeB, 1920, 1080)
        val panel = layout.panel
        val video = layout.video
        assertNotNull("Missing behavior: modeB reserves a video area", video)
        video!!
        assertEquals("panel on the right edge", 1920, panel.right)
        assertEquals(0, panel.top)
        assertEquals(1080, panel.height)
        assertTrue("panel has width and leaves room for video: $panel", panel.width in 1 until 1920)
        assertTrue("video left of the panel, no overlap: $video vs $panel", video.left >= 0 && video.right <= panel.left)
        assertTrue("video inside the screen height: $video", video.top >= 0 && video.bottom <= 1080)
        assertTrue("16:9 preserved: $video", abs(video.width.toDouble() / video.height - 16.0 / 9.0) <= 0.01)
        assertTrue("video fills the remaining area's width or height: $video", video.width >= panel.left - 1 || video.height >= 1079)
    }
}

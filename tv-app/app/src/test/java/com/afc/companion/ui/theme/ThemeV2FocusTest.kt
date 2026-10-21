package com.afc.companion.ui.theme

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.compositeOver
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ThemeV2FocusTest {
    @Test fun focusOutlineIsAtLeastFourDp() {
        assertTrue("Focused outline ${TvFocusStyle.borderWidthDp} dp < 4 dp", TvFocusStyle.borderWidthDp >= 4f)
    }

    @Test fun focusedAndUnfocusedOutlinesDifferByThreeToOne() {
        val background = captureTheme().colors.background
        val focused = Color(TvFocusStyle.focusedBorderArgb).compositeOver(background)
        val unfocused = Color(TvFocusStyle.unfocusedBorderArgb).compositeOver(background)
        assertTrue("Focused/unfocused outline must differ by 3:1", contrast(focused, unfocused) >= 3f)
        assertTrue("Focused outline must be visible on the background", contrast(focused, background) >= 3f)
    }

    @Test fun spaciousCardsScaleToOnePointOne() {
        assertEquals(1.1f, TvFocusStyle.scale, 0f)
    }

    /** Intended API: TvFocusStyle.denseScale: Float, used by dense rows. */
    @Test fun denseRowsDoNotEnlarge() {
        assertEquals(1f, designProperty(TvFocusStyle, "denseScale") as Float, 0f)
    }
}

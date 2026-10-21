package com.afc.companion.ui.theme

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.luminance
import androidx.compose.ui.graphics.toArgb
import kotlin.math.abs
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ThemePaletteTest {
    @Test fun primaryAccentIsVivid() {
        val saturation = referenceHsl(captureTheme().colors.primary)[1]
        assertTrue("Primary saturation $saturation < 0.6", saturation >= 0.6f)
    }

    @Test fun backgroundHasDarkRelativeLuminance() {
        val actual = captureTheme().colors.background.luminance()
        assertTrue("Background luminance $actual > 0.06", actual <= 0.06f)
    }

    @Test fun backgroundGradientHasTwoDistinctDarkStops() {
        val stops = backgroundGradient()
        assertEquals("Two gradient stops", 2, stops.size)
        assertTrue("Gradient stops must differ", stops[0] != stops[1])
        stops.forEachIndexed { index, color ->
            assertEquals("Gradient stop $index must be opaque", 1f, color.alpha, 0f)
            assertTrue("Gradient stop $index luminance ${color.luminance()} > 0.06", color.luminance() <= 0.06f)
        }
    }

    @Test fun sportAccentsAreVividAndAtLeastSixtyDegreesApart() {
        val hues = com.afc.companion.profile.Sport.entries.map { sport ->
            val color = sportColor("sportAccentArgb", sport)
            val hsl = referenceHsl(color)
            assertEquals("$sport accent must be opaque", 1f, color.alpha, 0f)
            assertTrue("$sport saturation ${hsl[1]} < 0.6", hsl[1] >= 0.6f)
            hsl[0]
        }
        val difference = abs(hues[0] - hues[1])
        val separation = minOf(difference, 360f - difference)
        assertTrue("Sport hue separation $separation < 60 degrees", separation >= 60f)
    }

    @Test fun semanticErrorRolesKeepTheirExistingMeaning() {
        val actual = captureTheme().colors
        val defaults = androidx.tv.material3.darkColorScheme()
        assertEquals(defaults.error, actual.error)
        assertEquals(defaults.onError, actual.onError)
        assertEquals(defaults.errorContainer, actual.errorContainer)
        assertEquals(defaults.onErrorContainer, actual.onErrorContainer)
    }

    /** Intended API: object TvColorMath { fun hsl(argb: Int): FloatArray }, H degrees, S/L fractions. */
    @Test fun sharedPureKotlinColorHelperMeasuresTheActualPalette() {
        val helper = designObject("TvColorMath")
        val hsl = helper.javaClass.getMethod("hsl", Int::class.javaPrimitiveType)
        val samples = palette().values + listOf(Color.Black, Color.White, Color.Gray, Color.Cyan, Color.Blue, Color.Magenta)
        samples.forEach { color ->
            val actual = hsl.invoke(helper, color.toArgb()) as FloatArray
            assertArrayEquals("HSL for $color", referenceHsl(color), actual, 0.001f)
        }
    }

    private fun palette(): Map<String, Color> = captureTheme().colors.let {
        mapOf(
            "background" to it.background, "surface" to it.surface, "surfaceVariant" to it.surfaceVariant,
            "primary" to it.primary, "secondary" to it.secondary, "tertiary" to it.tertiary,
            "primaryContainer" to it.primaryContainer, "secondaryContainer" to it.secondaryContainer,
            "tertiaryContainer" to it.tertiaryContainer,
        )
    }

    private fun referenceHsl(color: Color): FloatArray {
        val r = color.red
        val g = color.green
        val b = color.blue
        val high = maxOf(r, g, b)
        val low = minOf(r, g, b)
        val delta = high - low
        val lightness = (high + low) / 2f
        if (delta == 0f) return floatArrayOf(0f, 0f, lightness)
        val hue = when (high) {
            r -> ((g - b) / delta + 6f) % 6f
            g -> (b - r) / delta + 2f
            else -> (r - g) / delta + 4f
        } * 60f
        return floatArrayOf(hue, delta / (1f - abs(2f * lightness - 1f)), lightness)
    }
}

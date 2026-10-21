package com.afc.companion.ui.theme

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.luminance
import androidx.compose.ui.graphics.toArgb
import kotlin.math.abs
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ThemePaletteTest {
    @Test fun primarySecondaryAndAccentAreCoolAndDesaturated() {
        val failures = palette().mapNotNull { (role, color) ->
            val hsl = referenceHsl(color)
            println("$role: hue=${hsl[0]}, saturation=${hsl[1]}")
            if (hsl[0] !in 180f..300f || hsl[1] > 0.65f) "$role: H=${hsl[0]}, S=${hsl[1]}" else null
        }
        assertTrue("Require H in [180, 300] and S <= 0.65: ${failures.joinToString()}", failures.isEmpty())
    }

    @Test fun backgroundHasDarkRelativeLuminance() {
        val actual = captureTheme().colors.background.luminance()
        assertTrue("Background luminance $actual > 0.05", actual <= 0.05f)
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
        palette().forEach { (role, color) ->
            val actual = hsl.invoke(helper, color.toArgb()) as FloatArray
            assertTrue("$role must be cool and desaturated", actual[0] in 180f..300f && actual[1] <= 0.65f)
        }
    }

    private fun palette(): Map<String, Color> = captureTheme().colors.let {
        mapOf("primary" to it.primary, "secondary" to it.secondary, "accent (tertiary)" to it.tertiary)
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

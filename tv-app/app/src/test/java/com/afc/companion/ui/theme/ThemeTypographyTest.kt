package com.afc.companion.ui.theme

import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.TextUnitType
import androidx.compose.ui.unit.sp
import java.io.File
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ThemeTypographyTest {
    @Test fun noFontsAreBundled() {
        val main = File(System.getProperty("afc.repoRoot"), "tv-app/app/src/main")
        val fonts = main.walkTopDown().filter { file ->
            file.isFile && (file.extension.lowercase() in setOf("ttf", "otf", "woff", "woff2") ||
                file.relativeTo(main).invariantSeparatorsPath.startsWith("res/font/"))
        }.map { it.relativeTo(main).invariantSeparatorsPath }.toList()
        assertTrue("Use platform fonts; bundled fonts: $fonts", fonts.isEmpty())
    }

    @Test fun namedStylesMatchTheV2Ramp() {
        val t = captureTheme().typography
        val ramp = listOf(
            Triple("displayMedium", t.displayMedium, Triple(32, 40, FontWeight.Medium)),
            Triple("headlineMedium", t.headlineMedium, Triple(28, 36, FontWeight.Medium)),
            Triple("titleLarge", t.titleLarge, Triple(22, 30, FontWeight.Medium)),
            Triple("bodyLarge", t.bodyLarge, Triple(16, 24, FontWeight.Normal)),
            Triple("bodyMedium", t.bodyMedium, Triple(14, 22, FontWeight.Normal)),
            Triple("bodySmall", t.bodySmall, Triple(14, 20, FontWeight.Normal)),
            Triple("labelLarge", t.labelLarge, Triple(14, 20, FontWeight.Medium)),
        )
        val failures = ramp.flatMap { (name, actual, expected) ->
            listOfNotNull(
                if (actual.fontSize != expected.first.sp) "$name size: ${actual.fontSize} != ${expected.first}sp" else null,
                if (actual.lineHeight != expected.second.sp) "$name line: ${actual.lineHeight} != ${expected.second}sp" else null,
                if (actual.fontWeight != expected.third) "$name weight: ${actual.fontWeight} != ${expected.third}" else null,
                if (actual.fontFamily != FontFamily.Default) "$name must use the platform default family" else null,
            )
        }
        assertTrue(failures.joinToString("; "), failures.isEmpty())
    }

    @Test fun entireTypeScaleUsesNormalOrHeavierWeight() {
        val t = captureTheme().typography
        val styles = mapOf(
            "displayLarge" to t.displayLarge, "displayMedium" to t.displayMedium, "displaySmall" to t.displaySmall,
            "headlineLarge" to t.headlineLarge, "headlineMedium" to t.headlineMedium, "headlineSmall" to t.headlineSmall,
            "titleLarge" to t.titleLarge, "titleMedium" to t.titleMedium, "titleSmall" to t.titleSmall,
            "bodyLarge" to t.bodyLarge, "bodyMedium" to t.bodyMedium, "bodySmall" to t.bodySmall,
            "labelLarge" to t.labelLarge, "labelMedium" to t.labelMedium, "labelSmall" to t.labelSmall,
        )
        val failures = styles.mapNotNull { (name, style) ->
            val weight = style.fontWeight ?: FontWeight.Normal
            println("$name: weight=${weight.weight}")
            if (weight < FontWeight.Normal) "$name: ${weight.weight} < 400" else null
        }
        assertTrue(failures.joinToString(), failures.isEmpty())
    }

    @Test fun bodyTextResolvesToAtLeast24PixelsAt1080p() {
        // 1920x1080 output at 960x540 dp: density 2, default user font scale.
        val density = Density(density = 2f, fontScale = 1f)
        val t = captureTheme().typography
        for ((name, style) in mapOf("bodyLarge" to t.bodyLarge, "bodyMedium" to t.bodyMedium, "bodySmall" to t.bodySmall)) {
            assertEquals("$name must use scalable text units", TextUnitType.Sp, style.fontSize.type)
            val pixels = with(density) { style.fontSize.toPx() }
            println("$name: $pixels px at 1080p")
            assertTrue("$name resolves to $pixels px < 24 px (AFC-PR-045)", pixels >= 24f)
        }
    }
}

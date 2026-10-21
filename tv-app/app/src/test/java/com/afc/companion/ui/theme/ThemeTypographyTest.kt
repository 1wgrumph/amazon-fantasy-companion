package com.afc.companion.ui.theme

import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.TextUnitType
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ThemeTypographyTest {
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
        // Amazon's 1920x1080 output is 960x540 dp: density 2, default user font scale.
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

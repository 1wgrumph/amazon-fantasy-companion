package com.afc.companion.ui.theme

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.compositeOver
import org.junit.Assert.assertTrue
import org.junit.Test

/** Enabled text must meet WCAG 1.4.3, including inherited content and TV button states. */
class ThemeContrastTest {
    @Test fun inheritedTextOnAppBackgroundMeetsBodyContrast() {
        val theme = captureTheme()
        val scheme = theme.colors
        val background = scheme.background
        // TV Material 1.0.0 ButtonDefaults: normal uses 80% surfaceVariant/onSurface; focused/pressed invert.
        assertPairs(4.5f, mapOf(
            "Inherited text (NotConfigured, Link, Settings, panel headings)" to (theme.contentColor to background),
            "Settings input" to (scheme.onSurface to background),
            "Panel values and alert body" to (Color.White to background),
            "Button" to (scheme.onSurface.copy(alpha = 0.8f) to scheme.surfaceVariant.copy(alpha = 0.8f).compositeOver(background)),
            "Focused button" to (scheme.inverseOnSurface to scheme.onSurface),
            "Pressed button" to (scheme.inverseOnSurface to scheme.onSurface),
        ))
    }

    @Test fun allThemeTextRolesMeetBodyContrast() {
        val c = captureTheme().colors
        assertPairs(4.5f, mapOf(
            "onPrimary / primary" to (c.onPrimary to c.primary),
            "onPrimaryContainer / primaryContainer" to (c.onPrimaryContainer to c.primaryContainer),
            "onSecondary / secondary" to (c.onSecondary to c.secondary),
            "onSecondaryContainer / secondaryContainer" to (c.onSecondaryContainer to c.secondaryContainer),
            "onTertiary / tertiary (accent)" to (c.onTertiary to c.tertiary),
            "onTertiaryContainer / tertiaryContainer" to (c.onTertiaryContainer to c.tertiaryContainer),
            "onBackground / background" to (c.onBackground to c.background),
            "onSurface / surface" to (c.onSurface to c.surface),
            "onSurfaceVariant / surfaceVariant" to (c.onSurfaceVariant to c.surfaceVariant),
            "inverseOnSurface / inverseSurface" to (c.inverseOnSurface to c.inverseSurface),
            "onError / error" to (c.onError to c.error),
            "onErrorContainer / errorContainer" to (c.onErrorContainer to c.errorContainer),
        ))
    }

    @Test fun largeLinkCodeAndScreenHeadingsMeetLargeTextContrast() {
        val theme = captureTheme()
        assertPairs(3f, mapOf(
            "Link code and screen headings" to (theme.contentColor to theme.colors.background),
            "Panel scores and alert headline" to (Color.White to theme.colors.background),
        ))
    }

    private fun assertPairs(minimum: Float, pairs: Map<String, Pair<Color, Color>>) {
        val failures = pairs.mapNotNull { (name, pair) ->
            val (text, background) = pair
            val actual = contrast(text.compositeOver(background), background)
            println("$name = $actual:1 (minimum $minimum:1)")
            if (actual < minimum) "$name: $actual:1 < $minimum:1" else null
        }
        assertTrue(failures.joinToString("; "), failures.isEmpty())
    }
}

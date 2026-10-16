package com.afc.companion.ui.theme

import androidx.compose.runtime.AbstractApplier
import androidx.compose.runtime.Composition
import androidx.compose.runtime.Recomposer
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.luminance
import androidx.compose.ui.graphics.compositeOver
import androidx.tv.material3.LocalContentColor
import androidx.tv.material3.MaterialTheme
import kotlin.coroutines.EmptyCoroutineContext
import org.junit.Assert.assertTrue
import org.junit.Test

/** Couch UI: inherited text, including NotConfigured, must meet WCAG 1.4.3. */
class ThemeContrastTest {
    @Test fun inheritedTextOnAppBackgroundMeetsBodyContrast() {
        val recomposer = Recomposer(EmptyCoroutineContext)
        val composition = Composition(object : AbstractApplier<Unit>(Unit) {
            override fun insertTopDown(index: Int, instance: Unit) = Unit
            override fun insertBottomUp(index: Int, instance: Unit) = Unit
            override fun remove(index: Int, count: Int) = Unit
            override fun move(from: Int, to: Int, count: Int) = Unit
            override fun onClear() = Unit
        }, recomposer)
        try {
            composition.setContent {
                AfcTheme {
                    val foreground = LocalContentColor.current
                    val background = MaterialTheme.colorScheme.background
                    val scheme = MaterialTheme.colorScheme
                    // TV Material 1.0.0 ButtonDefaults: normal uses 80% surfaceVariant/onSurface; focused/pressed invert.
                    val pairs = mapOf(
                        "Inherited text (NotConfigured, Link, Settings, panel headings)" to (foreground to background),
                        "Settings input" to (MaterialTheme.colorScheme.onSurface to background),
                        "Panel values" to (Color.White to background),
                        "Button" to (scheme.onSurface.copy(alpha = 0.8f) to scheme.surfaceVariant.copy(alpha = 0.8f).compositeOver(background)),
                        "Focused button" to (scheme.inverseOnSurface to scheme.onSurface),
                        "Pressed button" to (scheme.inverseOnSurface to scheme.onSurface),
                    )
                    val failures = pairs.mapNotNull { (name, pair) ->
                        val (text, container) = pair
                        val actual = contrast(text.compositeOver(container), container)
                        println("$name: $text on $container = $actual:1")
                        if (actual < 4.5f) "$name: $actual:1 < 4.5:1" else null
                    }
                    assertTrue(failures.joinToString("; "), failures.isEmpty())
                }
            }
        } finally {
            composition.dispose()
            recomposer.cancel()
        }
    }

    private fun contrast(foreground: Color, background: Color): Float {
        val a = foreground.luminance()
        val b = background.luminance()
        return (maxOf(a, b) + 0.05f) / (minOf(a, b) + 0.05f)
    }
}

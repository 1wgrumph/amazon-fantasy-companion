package com.afc.companion.ui.theme

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.compositeOver
import java.io.File
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ThemeLayoutAndFocusTest {
    /** Intended API: object TvSafeZone { val fraction: Float; fun insets(widthDp: Float, heightDp: Float): Pair<Float, Float> }. */
    @Test fun sharedSafeZoneIsFivePercentOfEachDimension() {
        val safeZone = designObject("TvSafeZone")
        assertEquals(0.05f, designProperty(safeZone, "fraction") as Float, 0.000001f)
        val insets = safeZone.javaClass.getMethod("insets", Float::class.javaPrimitiveType, Float::class.javaPrimitiveType)
        for ((width, height) in listOf(960f to 540f, 1920f to 1080f)) {
            val actual = insets.invoke(safeZone, width, height) as Pair<*, *>
            assertEquals("Horizontal safe inset for $width dp", width * 0.05f, actual.first as Float, 0.001f)
            assertEquals("Vertical safe inset for $height dp", height * 0.05f, actual.second as Float, 0.001f)
        }
    }

    @Test fun everyTopLevelScreenReferencesSharedSafeZone() {
        // JVM source wiring check; geometry and focused-item clipping still need device visual review.
        val screens = listOf(
            Triple("link", "link/LinkScreen.kt", "fun LinkView("),
            Triple("profile settings", "profile/ProfileSettingsScreen.kt", "fun ProfileSettingsScreen("),
            Triple("panel and its alert cards", "panel/LineupPanel.kt", "fun LineupPanel("),
            Triple("panel loading", "panel/LineupPanel.kt", "fun PanelMessage("),
            Triple("watch confirmation", "watch/WatchActivity.kt", "fun confirmSwitch("),
            Triple("unconfigured", "MainActivity.kt", "fun NotConfigured("),
            Triple("shell navigation", "MainActivity.kt", "fun AppShell("),
        )
        val failures = screens.mapNotNull { (name, path, function) ->
            val source = File(System.getProperty("afc.repoRoot"), "tv-app/app/src/main/java/com/afc/companion/$path").readText()
                .replace(Regex("/\\*.*?\\*/", RegexOption.DOT_MATCHES_ALL), "")
                .replace(Regex("//[^\\n]*"), "")
            val start = source.indexOf(function)
            assertTrue("$name entry point $function exists", start >= 0)
            // Slice the actual function body, so a helper import or a reference in another screen cannot pass.
            val bodyStart = source.indexOf('{', start)
            var depth = 1
            var end = bodyStart + 1
            while (end < source.length && depth > 0) {
                when (source[end]) {
                    '{' -> depth++
                    '}' -> depth--
                }
                end++
            }
            val body = source.substring(bodyStart, end)
            if (!Regex("\\b(?:tvSafeZonePadding\\s*\\(|TvSafeZone\\s*\\.\\s*insets\\s*\\()").containsMatchIn(body)) {
                "$name must apply tvSafeZonePadding() or TvSafeZone.insets(...)"
            } else null
        }
        assertTrue(failures.joinToString("; "), failures.isEmpty())
    }

    /** Intended API: object TvFocusStyle { val borderWidthDp: Float; val focusedBorderArgb: Int; val unfocusedBorderArgb: Int }. */
    @Test fun sharedFocusOutlineIsAtLeastTwoDpAndChangesContrastByThreeToOne() {
        val style = designObject("TvFocusStyle")
        val width = designProperty(style, "borderWidthDp") as Float
        assertTrue("Focused border $width dp < 2 dp", width >= 2f)
        val background = captureTheme().colors.background
        val focused = Color(designProperty(style, "focusedBorderArgb") as Int).compositeOver(background)
        val unfocused = Color(designProperty(style, "unfocusedBorderArgb") as Int).compositeOver(background)
        val actual = contrast(focused, unfocused)
        assertTrue("Focused/unfocused outline contrast $actual:1 < 3:1", actual >= 3f)
        assertTrue("Focused outline must also be visible on the app background", contrast(focused, background) >= 3f)
    }
}

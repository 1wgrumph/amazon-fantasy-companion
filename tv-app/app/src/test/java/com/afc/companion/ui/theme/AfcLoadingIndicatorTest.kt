package com.afc.companion.ui.theme

import java.io.File
import org.junit.Assert.assertTrue
import org.junit.Test

/** Source contracts: this module has no JVM Compose rule or Robolectric dependency. */
class AfcLoadingIndicatorTest {
    @Test fun sharedComposableFillsAndCentresItsContainer() {
        val body = indicatorBody()
        val box = Regex("\\bBox\\s*\\(([\\s\\S]*?)\\)\\s*\\{").find(body)
        assertTrue("Loading indicator must have a Box container", box != null)
        val parameters = box!!.groupValues[1]
        assertTrue("Container must fill the available screen", Regex("\\.fillMaxSize\\s*\\(").containsMatchIn(parameters))
        assertTrue("Loading loop and label must be centred", Regex("contentAlignment\\s*=\\s*Alignment\\.Center\\b").containsMatchIn(parameters))
    }

    @Test fun loadingLoopUsesAnInfiniteAnimationInTheRenderedIndicator() {
        val body = indicatorBody()
        assertTrue("Use a remembered infinite transition", Regex("\\brememberInfiniteTransition\\s*\\(").containsMatchIn(body))
        assertTrue("Animation must repeat indefinitely", Regex("\\binfiniteRepeatable\\s*\\(").containsMatchIn(body))
        val animated = Regex("\\bval\\s+(\\w+)\\s+by\\s+\\w+\\.animateFloat\\s*\\(").find(body)
        assertTrue("Infinite transition must animate a float", animated != null)
        val value = animated!!.groupValues[1]
        assertTrue(
            "Animated value must rotate the rendered loop",
            Regex("(?:\\.rotate\\s*\\(\\s*$value\\b|\\brotationZ\\s*=\\s*$value\\b)").containsMatchIn(body),
        )
        assertTrue("Draw the loading loop", Regex("\\bdrawArc\\s*\\(").containsMatchIn(body))
    }

    @Test fun loadingLabelRemainsAccessible() {
        val body = indicatorBody()
        assertTrue(
            "Expose label as visible text or a content description",
            Regex("(?:\\bText\\s*\\(\\s*(?:text\\s*=\\s*)?label\\b|\\bcontentDescription\\s*=\\s*label\\b)").containsMatchIn(body),
        )
    }

    private fun indicatorBody(): String {
        // Intended API: @Composable fun AfcLoadingIndicator(label: String, modifier: Modifier = Modifier).
        val path = "ui/theme/AfcLoadingIndicator.kt"
        val file = File(System.getProperty("afc.repoRoot"), "tv-app/app/src/main/java/com/afc/companion/$path")
        assertTrue("Missing shared composable: ui.theme.AfcLoadingIndicator(label: String, modifier: Modifier)", file.isFile)
        val source = productSource(path)
        val signature = Regex("@Composable\\s+fun\\s+AfcLoadingIndicator\\s*\\(\\s*label\\s*:\\s*String\\b")
        assertTrue("Loading indicator must be composable and accept its label", signature.containsMatchIn(source))
        return sourceBlock(source, signature)
    }
}

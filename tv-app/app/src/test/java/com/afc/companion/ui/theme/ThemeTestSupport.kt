package com.afc.companion.ui.theme

import androidx.compose.runtime.AbstractApplier
import androidx.compose.runtime.Composition
import androidx.compose.runtime.Recomposer
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.luminance
import androidx.tv.material3.ColorScheme
import androidx.tv.material3.LocalContentColor
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Typography
import com.afc.companion.profile.Sport
import java.io.File
import kotlin.coroutines.EmptyCoroutineContext

internal data class ThemeSnapshot(val colors: ColorScheme, val typography: Typography, val contentColor: Color)

internal fun captureTheme(): ThemeSnapshot {
    val recomposer = Recomposer(EmptyCoroutineContext)
    val composition = Composition(object : AbstractApplier<Unit>(Unit) {
        override fun insertTopDown(index: Int, instance: Unit) = Unit
        override fun insertBottomUp(index: Int, instance: Unit) = Unit
        override fun remove(index: Int, count: Int) = Unit
        override fun move(from: Int, to: Int, count: Int) = Unit
        override fun onClear() = Unit
    }, recomposer)
    var snapshot: ThemeSnapshot? = null
    try {
        composition.setContent {
            AfcTheme {
                snapshot = ThemeSnapshot(MaterialTheme.colorScheme, MaterialTheme.typography, LocalContentColor.current)
            }
        }
        return checkNotNull(snapshot)
    } finally {
        composition.dispose()
        recomposer.cancel()
    }
}

internal fun contrast(foreground: Color, background: Color): Float {
    val a = foreground.luminance()
    val b = background.luminance()
    return (maxOf(a, b) + 0.05f) / (minOf(a, b) + 0.05f)
}

// Reflection keeps the red suite executable before the shared product definitions exist.
internal fun designObject(name: String): Any {
    val type = try {
        Class.forName("com.afc.companion.ui.theme.$name")
    } catch (_: ClassNotFoundException) {
        throw AssertionError("Missing shared design API: object $name in ui.theme")
    }
    return type.getField("INSTANCE").get(null) ?: throw AssertionError("$name.INSTANCE is null")
}

internal fun designProperty(instance: Any, name: String): Any = try {
    instance.javaClass.getMethod("get${name.replaceFirstChar { it.uppercase() }}").invoke(instance)
        ?: throw AssertionError("${instance.javaClass.simpleName}.$name is null")
} catch (missing: NoSuchMethodException) {
    throw AssertionError("Missing shared design API: ${instance.javaClass.simpleName}.$name", missing)
}

/** Intended API: TvPalette.backgroundGradientArgb: List<Int> (two ordered stops). */
internal fun backgroundGradient(): List<Color> =
    (designProperty(designObject("TvPalette"), "backgroundGradientArgb") as List<*>).map { Color(it as Int) }

/** Intended APIs: TvPalette.sportAccentArgb(Sport): Int and onSportAccentArgb(Sport): Int. */
internal fun sportColor(name: String, sport: Sport): Color {
    val palette = designObject("TvPalette")
    val method = try {
        palette.javaClass.getMethod(name, Sport::class.java)
    } catch (missing: NoSuchMethodException) {
        throw AssertionError("Missing shared design API: TvPalette.$name(Sport): Int", missing)
    }
    return Color(method.invoke(palette, sport) as Int)
}

internal fun productSource(path: String): String = File(
    System.getProperty("afc.repoRoot"), "tv-app/app/src/main/java/com/afc/companion/$path",
).readText().replace(Regex("/\\*.*?\\*/", RegexOption.DOT_MATCHES_ALL), "")
    .replace(Regex("//[^\\n]*"), "")

// Matches the safe-zone tests' source-reference approach; runtime geometry needs visual verification.
internal fun sourceBlock(source: String, declaration: Regex): String {
    val match = declaration.find(source) ?: throw AssertionError("Missing source declaration: ${declaration.pattern}")
    val start = source.indexOf('{', match.range.last + 1)
    check(start >= 0) { "Missing body for ${declaration.pattern}" }
    var depth = 1
    var end = start + 1
    while (end < source.length && depth > 0) {
        when (source[end]) {
            '{' -> depth++
            '}' -> depth--
        }
        end++
    }
    check(depth == 0) { "Unbalanced body for ${declaration.pattern}" }
    return source.substring(start + 1, end - 1)
}

internal fun assertLoadingCall(source: String, label: String) {
    org.junit.Assert.assertTrue(
        "Loading state must call AfcLoadingIndicator with accessible label '$label'",
        Regex("\\bAfcLoadingIndicator\\s*\\(\\s*(?:label\\s*=\\s*)?\"${Regex.escape(label)}\"").containsMatchIn(source),
    )
}

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

internal fun designProperty(instance: Any, name: String): Any =
    instance.javaClass.getMethod("get${name.replaceFirstChar { it.uppercase() }}").invoke(instance)
        ?: throw AssertionError("${instance.javaClass.simpleName}.$name is null")

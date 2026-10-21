// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
// Adapted from AmazonAppDev/hello-world-fire-tv (see THIRD_PARTY_NOTICES.md): package renamed, TV dark scheme only.

package com.afc.companion.ui.theme

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Border
import androidx.tv.material3.Button
import androidx.tv.material3.ButtonDefaults
import androidx.tv.material3.LocalContentColor
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Typography
import androidx.tv.material3.darkColorScheme
import kotlin.math.abs

object TvColorMath {
    fun hsl(argb: Int): FloatArray {
        val r = (argb ushr 16 and 255) / 255f
        val g = (argb ushr 8 and 255) / 255f
        val b = (argb and 255) / 255f
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

object TvSafeZone {
    val fraction = 0.05f
    fun insets(widthDp: Float, heightDp: Float): Pair<Float, Float> =
        widthDp * fraction to heightDp * fraction
}

// Shell children already sit inside the display's safe zone; standalone screens still apply it.
internal val LocalTvSafeZoneApplied = staticCompositionLocalOf { false }

@Composable
fun Modifier.tvSafeZonePadding(): Modifier {
    if (LocalTvSafeZoneApplied.current) return this
    val screen = LocalConfiguration.current
    val (horizontal, vertical) = TvSafeZone.insets(screen.screenWidthDp.toFloat(), screen.screenHeightDp.toFloat())
    return padding(horizontal = horizontal.dp, vertical = vertical.dp)
}

object TvFocusStyle {
    val borderWidthDp = 2f
    val focusedBorderArgb = 0xFF8AB4D6.toInt()
    val unfocusedBorderArgb = 0xFF303945.toInt()
    val scale = 1.02f
}

@Composable
fun Modifier.tvFocusStyle(focused: Boolean): Modifier =
    graphicsLayer {
        scaleX = if (focused) TvFocusStyle.scale else 1f
        scaleY = if (focused) TvFocusStyle.scale else 1f
    }.background(MaterialTheme.colorScheme.surface, RoundedCornerShape(8.dp))
        .border(TvFocusStyle.borderWidthDp.dp,
            Color(if (focused) TvFocusStyle.focusedBorderArgb else TvFocusStyle.unfocusedBorderArgb),
            RoundedCornerShape(8.dp))

@Composable
fun TvButton(onClick: () -> Unit, modifier: Modifier = Modifier, content: @Composable RowScope.() -> Unit) {
    Button(
        onClick = onClick,
        modifier = modifier,
        shape = ButtonDefaults.shape(shape = RoundedCornerShape(8.dp)),
        colors = ButtonDefaults.colors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant,
            contentColor = MaterialTheme.colorScheme.onSurface,
            focusedContainerColor = MaterialTheme.colorScheme.primary,
            focusedContentColor = MaterialTheme.colorScheme.onPrimary,
            pressedContainerColor = MaterialTheme.colorScheme.primary,
            pressedContentColor = MaterialTheme.colorScheme.onPrimary,
        ),
        border = ButtonDefaults.border(focusedBorder = Border(
            BorderStroke(TvFocusStyle.borderWidthDp.dp, Color(TvFocusStyle.focusedBorderArgb)),
            shape = RoundedCornerShape(8.dp),
        )),
        scale = ButtonDefaults.scale(focusedScale = TvFocusStyle.scale),
        content = content,
    )
}

private val AfcColors = darkColorScheme(
    primary = Color(TvFocusStyle.focusedBorderArgb), onPrimary = Color(0xFF101820),
    primaryContainer = Color(0xFF273F53), onPrimaryContainer = Color(0xFFD5E6F4),
    secondary = Color(0xFFA6B7C8), onSecondary = Color(0xFF101820),
    secondaryContainer = Color(0xFF303E4B), onSecondaryContainer = Color(0xFFDDE5ED),
    tertiary = Color(0xFF9DBBC5), onTertiary = Color(0xFF101820),
    tertiaryContainer = Color(0xFF293F47), onTertiaryContainer = Color(0xFFD9E8ED),
    background = Color(0xFF101418), onBackground = Color(0xFFE5E9ED),
    surface = Color(0xFF1A2027), onSurface = Color(0xFFE5E9ED),
    surfaceVariant = Color(0xFF29323C), onSurfaceVariant = Color(0xFFB8C2CC),
    inverseSurface = Color(0xFFE5E9ED), inverseOnSurface = Color(0xFF1A2027),
)

// Couch UI: body text stays at or above 28 px at 1080p with regular or medium weight.
private fun tvText(size: Int, lineHeight: Int, weight: FontWeight = FontWeight.Normal) = TextStyle(
    fontFamily = FontFamily.Default, fontWeight = weight, fontSize = size.sp, lineHeight = lineHeight.sp,
)

private val AfcTypography = Typography(
    displayMedium = tvText(44, 52, FontWeight.Medium),
    headlineMedium = tvText(28, 36, FontWeight.Medium),
    titleLarge = tvText(22, 30, FontWeight.Medium),
    bodyLarge = tvText(16, 24),
    bodyMedium = tvText(14, 22),
    bodySmall = tvText(14, 20),
    labelLarge = tvText(14, 20, FontWeight.Medium),
)

@Composable
fun AfcTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = AfcColors,
        typography = AfcTypography,
        content = {
            CompositionLocalProvider(LocalContentColor provides MaterialTheme.colorScheme.onBackground, content = content)
        },
    )
}

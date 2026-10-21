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
import androidx.compose.ui.graphics.Brush
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
import com.afc.companion.profile.Sport
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

/** Stadium at night: an indigo-to-plum sky, a floodlight-gold accent and one vivid colour per sport. */
object TvPalette {
    val backgroundGradientArgb = listOf(0xFF0E1030.toInt(), 0xFF2A0E3F.toInt())
    val surfaceArgb = 0xFF1B1E4B.toInt()
    val onSurfaceArgb = 0xFFF4F2FF.toInt()
    val primaryArgb = 0xFFFFD23F.toInt()
    val primaryContainerArgb = 0xFF4A3A12.toInt()
    val alertArgb = 0xFFFF6FB5.toInt()

    fun sportAccentArgb(sport: Sport): Int = when (sport) {
        Sport.Nfl -> 0xFF2FE39A.toInt()
        Sport.Nba -> 0xFFFF6A3D.toInt()
    }

    fun onSportAccentArgb(sport: Sport): Int = when (sport) {
        Sport.Nfl -> 0xFF00281A.toInt()
        Sport.Nba -> 0xFF2A0A00.toInt()
    }
}

/** The app backdrop: the palette's two gradient stops, corner to corner. */
fun Modifier.afcBackground(): Modifier = background(Brush.linearGradient(TvPalette.backgroundGradientArgb.map(::Color)))

object TvFocusStyle {
    val borderWidthDp = 4f
    val focusedBorderArgb = TvPalette.primaryArgb
    val unfocusedBorderArgb = 0xFF3A3E78.toInt()
    val scale = 1.1f
    // Dense rows (panel rows, alert cards, text fields) mark focus by outline and fill only.
    val denseScale = 1f
}

@Composable
fun Modifier.tvFocusStyle(focused: Boolean): Modifier =
    graphicsLayer {
        scaleX = if (focused) TvFocusStyle.denseScale else 1f
        scaleY = if (focused) TvFocusStyle.denseScale else 1f
    }.background(
        if (focused) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surface,
        RoundedCornerShape(8.dp),
    )
        .border(TvFocusStyle.borderWidthDp.dp,
            Color(if (focused) TvFocusStyle.focusedBorderArgb else TvFocusStyle.unfocusedBorderArgb),
            RoundedCornerShape(8.dp))

@Composable
fun TvButton(onClick: () -> Unit, modifier: Modifier = Modifier, content: @Composable RowScope.() -> Unit) {
    Button(
        onClick = onClick,
        modifier = modifier,
        shape = ButtonDefaults.shape(shape = RoundedCornerShape(50)),
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
            shape = RoundedCornerShape(50),
        )),
        scale = ButtonDefaults.scale(focusedScale = TvFocusStyle.scale),
        content = content,
    )
}

private val AfcColors = darkColorScheme(
    primary = Color(TvPalette.primaryArgb), onPrimary = Color(0xFF1E1400),
    primaryContainer = Color(TvPalette.primaryContainerArgb), onPrimaryContainer = Color(0xFFFFE9A8),
    secondary = Color(0xFF7CE8FF), onSecondary = Color(0xFF00202A),
    secondaryContainer = Color(0xFF0F3A4A), onSecondaryContainer = Color(0xFFC4F3FF),
    tertiary = Color(TvPalette.alertArgb), onTertiary = Color(0xFF2A0018),
    tertiaryContainer = Color(0xFF5A1A40), onTertiaryContainer = Color(0xFFFFD6EA),
    background = Color(TvPalette.backgroundGradientArgb[0]), onBackground = Color(TvPalette.onSurfaceArgb),
    surface = Color(TvPalette.surfaceArgb), onSurface = Color(TvPalette.onSurfaceArgb),
    surfaceVariant = Color(0xFF2B2E66), onSurfaceVariant = Color(0xFFC9C6EC),
    inverseSurface = Color(TvPalette.onSurfaceArgb), inverseOnSurface = Color(TvPalette.surfaceArgb),
)

// Couch UI: body text stays at or above 28 px at 1080p with regular or medium weight.
private fun tvText(size: Int, lineHeight: Int, weight: FontWeight = FontWeight.Normal) = TextStyle(
    fontFamily = FontFamily.Default, fontWeight = weight, fontSize = size.sp, lineHeight = lineHeight.sp,
)

private val AfcTypography = Typography(
    displayMedium = tvText(32, 40, FontWeight.Medium),
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

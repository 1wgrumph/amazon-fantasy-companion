package com.afc.companion.panel

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import com.afc.companion.profile.Sport
import com.afc.companion.ui.theme.TvFocusStyle
import com.afc.companion.ui.theme.TvPalette

private val onSurface = Color(CornerCardStyle.TEXT_ARGB)

/**
 * The default over-the-game surface: the team total, its freshness and an opaque sport mark on a
 * translucent theme surface, with a sport-colour edge. Without [holdEnabled] it adds the one-line accessibility-switch hint.
 */
@Composable
fun CornerCardContent(snapshot: PanelSnapshot?, teamLeague: String?, nowMs: Long, holdEnabled: Boolean) {
    val sport = Sport.entries.find { it.label == CornerCardText.sport(snapshot) }
    val accent = sport?.let { Color(TvPalette.sportAccentArgb(it)) } ?: Color(TvPalette.primaryArgb)
    val hint = CornerCardText.hint(holdEnabled)
    Row(
        Modifier.fillMaxSize().clip(RoundedCornerShape(12.dp))
            .background(Color(TvPalette.surfaceArgb).copy(alpha = CornerCardStyle.BACKGROUND_ALPHA)),
    ) {
        Box(Modifier.width(4.dp).fillMaxHeight().background(accent))
        Column(
            Modifier.weight(1f).fillMaxHeight().padding(horizontal = 10.dp, vertical = 5.dp),
            verticalArrangement = Arrangement.Center,
        ) {
            Line(CornerCardText.total(snapshot), 22.sp, FontWeight.Bold)
            Row(verticalAlignment = Alignment.CenterVertically) {
                if (sport != null) {
                    Text(
                        sport.label,
                        Modifier.clip(RoundedCornerShape(4.dp)).background(accent).padding(horizontal = 4.dp),
                        style = TextStyle(fontSize = 11.sp, lineHeight = 14.sp, fontWeight = FontWeight.Bold, color = Color(TvPalette.onSportAccentArgb(sport))),
                    )
                    Box(Modifier.width(6.dp))
                }
                Line(CornerCardText.status(snapshot, teamLeague, nowMs), 12.sp)
            }
            if (hint != null) Line(hint, 10.sp)
        }
    }
}

/** The held-≡ menu below the card: three rows, the focused one in the theme's gold focus style. */
@Composable
fun OverlayMenuContent(focus: OverlayMenuItem, teamLeague: String?) {
    Column(
        Modifier.fillMaxSize().clip(RoundedCornerShape(12.dp))
            .background(Color(TvPalette.surfaceArgb).copy(alpha = CornerCardStyle.MENU_ALPHA)).padding(6.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        OverlayMenuItem.entries.forEach { item ->
            val focused = item == focus
            val label = when (item) {
                OverlayMenuItem.Expand -> "Expand"
                OverlayMenuItem.League -> "League: ${teamLeague?.substringBefore('/') ?: "none"}"
                OverlayMenuItem.Hide -> "Hide"
            }
            Box(
                Modifier.fillMaxWidth().weight(1f).clip(RoundedCornerShape(8.dp))
                    .background(if (focused) Color(TvPalette.primaryContainerArgb) else Color.Transparent)
                    .border(2.dp, if (focused) Color(TvFocusStyle.focusedBorderArgb) else Color.Transparent, RoundedCornerShape(8.dp))
                    .padding(horizontal = 10.dp),
                contentAlignment = Alignment.CenterStart,
            ) {
                Line(label, 15.sp, if (focused) FontWeight.Bold else FontWeight.Normal)
            }
        }
    }
}

@Composable
private fun Line(text: String, size: TextUnit, weight: FontWeight = FontWeight.Normal) {
    Text(
        text,
        maxLines = 1,
        softWrap = false,
        overflow = TextOverflow.Ellipsis,
        style = TextStyle(fontSize = size, lineHeight = size * 1.2f, fontWeight = weight, color = onSurface),
    )
}

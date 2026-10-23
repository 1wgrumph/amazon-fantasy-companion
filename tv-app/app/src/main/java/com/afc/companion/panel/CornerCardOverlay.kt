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
import androidx.compose.runtime.remember
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
 * The default over-the-game surface, read from the couch: matchup and clock small; the team total
 * large in the brand gold; the two top scorers, a ▲ on one whose points rose since the last refresh.
 * Translucent theme surface with a sport-colour edge. Without [holdEnabled] the accessibility-switch hint replaces the scorers.
 */
@Composable
fun CornerCardContent(snapshot: PanelSnapshot?, teamLeague: String?, nowMs: Long, holdEnabled: Boolean, windowAlpha: Float = 1f) {
    val sport = Sport.entries.find { it.label == CornerCardText.sport(snapshot) }
    val accent = sport?.let { Color(TvPalette.sportAccentArgb(it)) } ?: Color(TvPalette.primaryArgb)
    // The window outlives each refresh, so the snapshot it showed last is the one to compare against.
    val seen = remember { arrayOfNulls<PanelSnapshot>(1) }
    val prior = remember(snapshot) { seen[0].also { seen[0] = snapshot } }
    Row(
        Modifier.fillMaxSize().clip(RoundedCornerShape(12.dp))
            .background(Color(TvPalette.surfaceArgb).copy(alpha = CornerCardStyle.backgroundAlpha(windowAlpha))),
    ) {
        Box(Modifier.width(5.dp).fillMaxHeight().background(accent))
        Column(
            Modifier.weight(1f).fillMaxHeight().padding(horizontal = 10.dp, vertical = 2.dp),
            verticalArrangement = Arrangement.Center,
        ) {
            Line(CornerCardText.label(snapshot, teamLeague), 11.sp, FontWeight.SemiBold, onSurface.copy(alpha = 0.8f))
            Text(
                CornerCardText.total(snapshot),
                maxLines = 1,
                softWrap = false,
                style = TextStyle(fontSize = 22.sp, lineHeight = 24.sp, fontWeight = FontWeight.Black, color = Color(TvPalette.primaryArgb), fontFeatureSettings = "tnum"),
            )
            val hint = CornerCardText.hint(holdEnabled)
            if (hint != null) Line(hint, 11.sp) else CornerCardText.leaders(snapshot, prior).forEach { LeaderLine(it) }
        }
    }
}

/** The held-≡ menu below the card: available rows, the focused one in the theme's gold focus style. */
@Composable
fun OverlayMenuContent(focus: OverlayMenuItem, teamLeague: String?, items: List<OverlayMenuItem>) {
    Column(
        Modifier.fillMaxSize().clip(RoundedCornerShape(12.dp))
            .background(Color(TvPalette.surfaceArgb).copy(alpha = CornerCardStyle.MENU_ALPHA)).padding(6.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        items.forEach { item ->
            val focused = item == focus
            val label = when (item) {
                OverlayMenuItem.Expand -> "Expand"
                OverlayMenuItem.League -> CornerCardText.label(null, teamLeague)
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

/** "D. Mitchell ▲      34.1": name left, points right in tabular figures. */
@Composable
private fun LeaderLine(leader: CornerCardText.Leader) {
    val style = TextStyle(fontSize = 11.sp, lineHeight = 12.sp, fontWeight = FontWeight.SemiBold, color = onSurface)
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Row(Modifier.weight(1f)) {
            Text(leader.name, Modifier.weight(1f, fill = false), maxLines = 1, softWrap = false, overflow = TextOverflow.Ellipsis, style = style)
            if (leader.rose) Text(" ▲", maxLines = 1, style = style.copy(color = Color(TvPalette.primaryArgb)))
        }
        Text(leader.points, Modifier.padding(start = 6.dp), maxLines = 1, softWrap = false, style = style.copy(fontWeight = FontWeight.Bold, fontFeatureSettings = "tnum"))
    }
}

@Composable
private fun Line(text: String, size: TextUnit, weight: FontWeight = FontWeight.Normal, color: Color = onSurface) {
    Text(
        text,
        maxLines = 1,
        softWrap = false,
        overflow = TextOverflow.Ellipsis,
        style = TextStyle(fontSize = size, lineHeight = size * 1.2f, fontWeight = weight, color = color),
    )
}

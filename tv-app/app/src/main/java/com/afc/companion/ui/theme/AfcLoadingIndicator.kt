package com.afc.companion.ui.theme

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.dp
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text

/** Shared loading state: a spinning gold-to-flare loop with its label, centred in the available space. */
@Composable
fun AfcLoadingIndicator(label: String, modifier: Modifier = Modifier) {
    val transition = rememberInfiniteTransition(label = "loading")
    val angle by transition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(tween(durationMillis = 1_100, easing = LinearEasing)),
        label = "loading angle",
    )
    val track = MaterialTheme.colorScheme.surfaceVariant
    // Transparent tail to gold head at the arc's 300-degree end, so the loop reads as a comet.
    val comet = Brush.sweepGradient(
        0f to Color.Transparent,
        0.45f to MaterialTheme.colorScheme.tertiary,
        0.83f to MaterialTheme.colorScheme.primary,
        1f to Color.Transparent,
    )
    Box(modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(24.dp)) {
            Canvas(Modifier.size(80.dp).rotate(angle)) {
                val stroke = Stroke(width = 8.dp.toPx(), cap = StrokeCap.Round)
                drawArc(color = track, startAngle = 0f, sweepAngle = 360f, useCenter = false, style = stroke)
                drawArc(brush = comet, startAngle = 0f, sweepAngle = 300f, useCenter = false, style = stroke)
            }
            Text(label, style = MaterialTheme.typography.titleLarge)
        }
    }
}

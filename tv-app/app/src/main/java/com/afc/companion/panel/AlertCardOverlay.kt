package com.afc.companion.panel

import android.content.Context
import android.graphics.PixelFormat
import android.os.SystemClock
import android.provider.Settings
import android.util.DisplayMetrics
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.ComposeView
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.LifecycleRegistry
import androidx.lifecycle.setViewTreeLifecycleOwner
import androidx.savedstate.SavedStateRegistry
import androidx.savedstate.SavedStateRegistryController
import androidx.savedstate.SavedStateRegistryOwner
import androidx.savedstate.setViewTreeSavedStateRegistryOwner
import androidx.tv.material3.Text
import com.afc.companion.net.Alert
import com.afc.companion.profile.Sport
import com.afc.companion.ui.theme.AfcTheme
import com.afc.companion.ui.theme.TvPalette

/**
 * The top-right alert card window (phone-notification style): one small square per new inbox alert,
 * five seconds each, queued, never focusable. Timeout never dismisses the inbox alert, so Watch stays
 * reachable in Companion's Panel. Without the overlay permission nothing is shown and nothing is asked:
 * a background alert must not pull the viewer out of the game.
 */
class AlertCardOverlay(
    private val context: Context,
    private val windows: WindowManager,
    private val panel: () -> PanelSnapshot?,
    private val onCard: (Box?) -> Unit,
) {
    private val queue = AlertCardQueue()
    private var started = false
    private var retained: Set<String>? = null
    private var shownId: String? = null
    private var view: OverlayView? = null

    val active: Boolean get() = started && Settings.canDrawOverlays(context)

    fun start() {
        started = true
    }

    /** Alerts already retained when the host first sees the inbox are old news: only later arrivals pop up. */
    fun onAlerts(alerts: List<Alert>) {
        val old = retained ?: alerts.map { it.envelope.id }.toSet().also { retained = it }
        if (!started) return
        val now = SystemClock.elapsedRealtime()
        alerts.filter { it.envelope.id !in old }.mapNotNull { alertCardNotice(it, panel()) }.forEach { queue.offer(it, now) }
        render()
    }

    fun tick() {
        queue.advance(SystemClock.elapsedRealtime())
        if (queue.current == null) hideCard() else render()
    }

    fun stop() {
        started = false
        queue.clear()
        hideCard()
    }

    private fun render() {
        val notice = queue.current ?: return
        if (notice.alertId != shownId) showCard(notice)
    }

    private fun showCard(notice: AlertCardNotice) {
        hideCard()
        shownId = notice.alertId
        if (!Settings.canDrawOverlays(context)) return
        val (width, height) = screenSize(windows)
        val box = AlertCardGeometry.layout(width, height)
        val params = WindowManager.LayoutParams(
            box.width, box.height, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            // Never focusable or touchable: remote input stays with the game.
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
            PixelFormat.TRANSLUCENT,
        ).apply {
            gravity = Gravity.TOP or Gravity.LEFT
            x = box.left
            y = box.top
        }
        val card = OverlayView(context) { AlertCardContent(notice) }
        // A revoked permission or a gone display shows nothing rather than crashing the host.
        if (runCatching { windows.addView(card.view, params) }.isSuccess) {
            view = card
            onCard(box)
        }
    }

    private fun hideCard() {
        shownId = null
        val card = view ?: return
        view = null
        runCatching { windows.removeView(card.view) }
        card.destroy()
        onCard(null)
    }
}

/** Two text nodes: the "Edwards 20" label and a 14 sp sport mark, on a sport-accent band. */
@Composable
fun AlertCardContent(notice: AlertCardNotice) {
    val sport = Sport.entries.find { it.label == notice.sport }
    val accent = sport?.let { Color(TvPalette.sportAccentArgb(it)) } ?: Color(TvPalette.alertArgb)
    Column(
        Modifier.fillMaxSize().clip(RoundedCornerShape(14.dp)).background(Color(TvPalette.surfaceArgb).copy(alpha = 0.94f)),
    ) {
        Box(Modifier.fillMaxWidth().height(6.dp).background(accent))
        Column(
            Modifier.fillMaxSize().padding(horizontal = 10.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.SpaceBetween,
        ) {
            // An unknown number shows the name alone; the presenter already cleared the name as safe.
            val label = AlertCardText.label(notice.player, notice.value) ?: notice.player
            BoxWithConstraints {
                // Shrink so the longest word fits one line: wrapping happens between name and number, never inside a name.
                val longest = label.split(' ').maxOf { it.length }.coerceAtLeast(1)
                val size = minOf(22f, maxWidth.value / (longest * 0.56f))
                Text(
                    label,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    style = TextStyle(fontSize = size.sp, lineHeight = (size * 1.15f).sp, fontWeight = FontWeight.Bold, color = Color(TvPalette.onSurfaceArgb)),
                )
            }
            Text(notice.sport, modifier = Modifier.align(Alignment.End), style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold, color = accent))
        }
    }
}

/** Full display size in pixels, the space overlay windows are placed in. */
internal fun screenSize(windows: WindowManager): Pair<Int, Int> {
    val metrics = DisplayMetrics()
    @Suppress("DEPRECATION") windows.defaultDisplay.getRealMetrics(metrics)
    return metrics.widthPixels to metrics.heightPixels
}

/** A ComposeView for a service-owned window, which has no activity to supply its lifecycle and saved state. */
internal class OverlayView(context: Context, content: @Composable () -> Unit) : LifecycleOwner, SavedStateRegistryOwner {
    private val registry = LifecycleRegistry(this)
    private val saved = SavedStateRegistryController.create(this)
    override val lifecycle: Lifecycle get() = registry
    override val savedStateRegistry: SavedStateRegistry get() = saved.savedStateRegistry

    val view: View = ComposeView(context).apply {
        setViewTreeLifecycleOwner(this@OverlayView)
        setViewTreeSavedStateRegistryOwner(this@OverlayView)
        setContent { AfcTheme(content) }
    }

    init {
        saved.performRestore(null)
        registry.currentState = Lifecycle.State.RESUMED
    }

    fun destroy() {
        registry.currentState = Lifecycle.State.DESTROYED
    }
}

package com.afc.companion.panel

import com.afc.companion.alerts.AlertNotifier
import com.afc.companion.alerts.AlertPresenter
import com.afc.companion.net.Alert
import kotlin.math.ceil
import kotlin.math.floor
import kotlin.math.min
import org.json.JSONObject

// JVM-pure overlay logic: the side panel over the game and the top-right alert card. Android windows live in
// OverlayService and AlertCardOverlay; everything they place or decide comes from here.

enum class OverlayOutcome { Shown, Hidden, PermissionNeeded }

/** One overlay window over the existing [panel] state; [hasPermission] is rechecked on every show. */
class OverlayController(
    val panel: PanelController,
    private val hasPermission: () -> Boolean,
    private val requestPermission: () -> Unit,
    private val addWindow: () -> Unit,
    private val removeWindow: () -> Unit,
) {
    private var shown = false

    fun show(): OverlayOutcome {
        if (shown) return OverlayOutcome.Shown
        if (!hasPermission()) {
            requestPermission()
            return OverlayOutcome.PermissionNeeded
        }
        // ToggleVisibility on a hidden panel also marks it for an immediate fetch.
        if (!panel.visible) panel.perform(PanelAction.ToggleVisibility, 0)
        addWindow()
        shown = true
        return OverlayOutcome.Shown
    }

    fun hide(): OverlayOutcome {
        if (panel.visible) panel.perform(PanelAction.ToggleVisibility, 0)
        if (shown) {
            shown = false
            removeWindow()
        }
        return OverlayOutcome.Hidden
    }

    fun toggle(): OverlayOutcome = if (shown) hide() else show()
}

private fun safeLeft(width: Int) = ceil(width * 0.05).toInt()
private fun safeTop(height: Int) = ceil(height * 0.05).toInt()
private fun safeRight(width: Int) = floor(width * 0.95).toInt()
private fun safeBottom(height: Int) = floor(height * 0.95).toInt()

/** Side panel in screen pixels: a quarter of the width, on the safe right edge, full safe height. */
object OverlayGeometry {
    fun layout(screenWidth: Int, screenHeight: Int): Box {
        val width = screenWidth / 4
        val top = safeTop(screenHeight)
        return Box(safeRight(screenWidth) - width, top, width, safeBottom(screenHeight) - top)
    }

    /** The same panel moved below a showing [card], with a 1% gap, so the two never overlap. */
    fun layoutWithAlertCard(screenWidth: Int, screenHeight: Int, card: Box): Box {
        val panel = layout(screenWidth, screenHeight)
        val top = maxOf(panel.top, card.bottom + ceil(screenHeight * 0.01).toInt())
        return panel.copy(top = top, height = safeBottom(screenHeight) - top)
    }
}

/** Alert card: a square of one-sixth of the short side at the safe top-right corner (180 px at 1080p). */
object AlertCardGeometry {
    fun layout(screenWidth: Int, screenHeight: Int): Box {
        val side = min(screenWidth, screenHeight) / 6
        return Box(safeRight(screenWidth) - side, safeTop(screenHeight), side, side)
    }
}

/** One card with an authoritative finite value and known sport. */
data class AlertCardNotice(
    val alertId: String,
    val player: String,
    val value: Double,
    val sport: String,
    val watchEventId: String,
)

object AlertCardText {
    /** "Edwards 20": the player and a compact number; null for a non-finite number or an unsafe claim. */
    fun label(player: String, value: Double): String? {
        if (player.isBlank() || !value.isFinite() || AlertPresenter.isUnsafe(player)) return null
        val number = if (value == floor(value)) value.toLong().toString() else value.toString()
        return "$player $number"
    }
}

/** Card notices shown one at a time in arrival order, each for [SHOW_MS] once current; IDs show once per session. */
class AlertCardQueue {
    private val pending = ArrayDeque<AlertCardNotice>()
    private val seen = HashSet<String>()
    private var shownAtMs = 0L

    var current: AlertCardNotice? = null
        private set

    fun offer(notice: AlertCardNotice, nowMs: Long) {
        if (!seen.add(notice.alertId)) return
        pending.addLast(notice)
        if (current == null) promote(nowMs)
    }

    fun advance(nowMs: Long) {
        if (current != null && nowMs - shownAtMs >= SHOW_MS) {
            current = null
            promote(nowMs)
        }
    }

    fun clear() {
        pending.clear()
        seen.clear()
        current = null
    }

    private fun promote(nowMs: Long) {
        current = pending.removeFirstOrNull()
        shownAtMs = nowMs
    }

    companion object { const val SHOW_MS = 5_000L }
}

/**
 * Card notice from one inbox alert, or null when the alert has no safe first starter.
 * Optional backend fields win when present: `triggerContext.sport` ("nba"/"nfl"),
 * `starters[0].shortName` and `starters[0].points` (fantasy points on the profile's basis).
 * Without them the player is the starter's last name, and the number and sport come only from the
 * fresh matching row of the selected profile's [panel] snapshot; otherwise no card is emitted.
 */
fun alertCardNotice(alert: Alert, panel: PanelSnapshot?): AlertCardNotice? {
    if (AlertPresenter.text(alert) == null) return null // the panel's safety gate: unsafe names never reach a card
    val trigger = alert.envelope.data.opt("triggerContext") as? JSONObject ?: return null
    val starter = trigger.optJSONArray("starters")?.opt(0) as? JSONObject ?: return null
    val player = ((starter.opt("shortName") as? String)?.trim()?.takeIf { it.isNotEmpty() }
        ?: (starter.opt("name") as? String)?.trim()?.substringAfterLast(' '))
        ?.take(MAX_CARD_NAME)?.takeIf { AlertCardText.label(it, 0.0) != null } ?: return null
    val declaredSport = when (trigger.opt("sport")) { "nba" -> "NBA"; "nfl" -> "NFL"; else -> null }
    val row = panel?.rows?.firstOrNull {
        it.playerId == starter.opt("athlete_id") && (declaredSport == null || declaredSport == panel.sport)
    }
    val freshPoints = row?.points?.takeIf { points ->
        points.asOfMs?.let { System.currentTimeMillis() - it in 0..60_000 } == true
    }?.value?.takeIf { it.isFinite() }
    val value = (starter.opt("points") as? Number)?.toDouble()?.takeIf { it.isFinite() } ?: freshPoints ?: return null
    val sport = declaredSport ?: panel?.sport?.takeIf { row != null && it in listOf("NBA", "NFL") } ?: return null
    return AlertCardNotice(alert.envelope.id, player, value, sport, AlertNotifier.watchEventId(alert).orEmpty())
}

private const val MAX_CARD_NAME = 14

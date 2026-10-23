package com.afc.companion.panel

import com.afc.companion.alerts.AlertNotifier
import com.afc.companion.alerts.AlertPresenter
import android.view.KeyEvent
import android.view.WindowManager
import com.afc.companion.net.Alert
import com.afc.companion.profile.ProfileState
import com.afc.companion.ui.theme.TvPalette
import kotlin.math.ceil
import kotlin.math.floor
import kotlin.math.min
import org.json.JSONObject

// JVM-pure overlay logic: the corner card, its held-≡ menu, the side panel and the top-right alert card. Android
// windows live in OverlayService, CornerCardOverlay and AlertCardOverlay; everything they place or decide comes from here.

enum class OverlayOutcome { Shown, Hidden, PermissionNeeded }

/** Off; the corner card; the card with its small menu; the expanded side panel. */
enum class OverlayMode { Off, Card, Menu, Expanded }

/** Menu rows in D-pad order; League is offered only for known real pairs. */
enum class OverlayMenuItem { Expand, League, Hide }

/**
 * One overlay surface over the existing [panel] state; [hasPermission] is rechecked on every show.
 * [addWindow] and [removeWindow] run when the surface turns on and off; the host re-reads [mode] after each call.
 */
class OverlayController(
    val panel: PanelController,
    private val hasPermission: () -> Boolean,
    private val requestPermission: () -> Unit,
    private val addWindow: () -> Unit,
    private val removeWindow: () -> Unit,
    private val nowMs: () -> Long = { System.nanoTime() / 1_000_000 },
) {
    private var idleDeadlineMs: Long? = null
    var mode = OverlayMode.Off
        private set(value) {
            field = value
            idleDeadlineMs = if (focusable) nowMs() + IDLE_MS else null
        }
    var menuFocus = OverlayMenuItem.entries.first()
        private set

    val menuItems: List<OverlayMenuItem> get() = if (panel.canSwitchTeamLeague) OverlayMenuItem.entries
        else listOf(OverlayMenuItem.Expand, OverlayMenuItem.Hide)

    /** Only the menu and the expanded panel take the remote; the plain card leaves it with the game. */
    val focusable: Boolean get() = mode == OverlayMode.Menu || mode == OverlayMode.Expanded

    fun show(): OverlayOutcome {
        if (mode != OverlayMode.Off) return OverlayOutcome.Shown
        if (!hasPermission()) {
            requestPermission()
            return OverlayOutcome.PermissionNeeded
        }
        // ToggleVisibility on a hidden panel also marks it for an immediate fetch.
        if (!panel.visible) panel.perform(PanelAction.ToggleVisibility, 0)
        mode = OverlayMode.Card
        addWindow()
        return OverlayOutcome.Shown
    }

    fun hide(): OverlayOutcome {
        if (panel.visible) panel.perform(PanelAction.ToggleVisibility, 0)
        if (mode != OverlayMode.Off) {
            mode = OverlayMode.Off
            removeWindow()
        }
        return OverlayOutcome.Hidden
    }

    fun toggle(): OverlayOutcome = if (mode != OverlayMode.Off) hide() else show()

    /** Held ≡: show the card, open its menu, or close the menu or panel back to the card. */
    fun hold(): OverlayOutcome = when (mode) {
        OverlayMode.Off -> show()
        OverlayMode.Card -> openMenu()
        OverlayMode.Menu, OverlayMode.Expanded -> { mode = OverlayMode.Card; OverlayOutcome.Shown }
    }

    /** Double-tapped ≡ switches the pair in whichever view is open: card, menu or expanded panel. */
    fun doubleTap() {
        if (mode != OverlayMode.Off) panel.perform(PanelAction.NextTeamLeague, 0)
    }

    fun select(item: OverlayMenuItem) {
        when (item) {
            OverlayMenuItem.Hide -> hide()
            OverlayMenuItem.Expand -> mode = OverlayMode.Expanded
            OverlayMenuItem.League -> if (panel.canSwitchTeamLeague) panel.perform(PanelAction.NextTeamLeague, 0)
        }
    }

    /** A key delivered to a focused menu or panel window (key down only); false leaves it unhandled. */
    fun onFocusedKey(keyCode: Int): Boolean {
        if (focusable) idleDeadlineMs = nowMs() + IDLE_MS
        val items = menuItems
        return when (mode) {
            OverlayMode.Menu -> when (keyCode) {
                KeyEvent.KEYCODE_DPAD_UP -> { menuFocus = items[(items.indexOf(menuFocus) - 1).coerceAtLeast(0)]; true }
                KeyEvent.KEYCODE_DPAD_DOWN -> { menuFocus = items[(items.indexOf(menuFocus) + 1).coerceAtMost(items.lastIndex)]; true }
                in OK_KEYS -> { select(menuFocus); true }
                KeyEvent.KEYCODE_BACK -> { mode = OverlayMode.Card; true }
                else -> false
            }
            OverlayMode.Expanded -> when (keyCode) {
                in OK_KEYS -> { openMenu(); true }
                KeyEvent.KEYCODE_BACK -> { mode = OverlayMode.Card; true }
                else -> false
            }
            OverlayMode.Off, OverlayMode.Card -> false
        }
    }

    /** Called by the host's existing tick; expiry uses the same Card transition as Back. */
    fun tick(): Boolean {
        val deadline = idleDeadlineMs ?: return false
        if (nowMs() < deadline) return false
        mode = OverlayMode.Card
        return true
    }

    private fun openMenu(): OverlayOutcome {
        menuFocus = OverlayMenuItem.entries.first()
        mode = OverlayMode.Menu
        return OverlayOutcome.Shown
    }

    private companion object {
        const val IDLE_MS = 90_000L
        val OK_KEYS = setOf(KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_ENTER, KeyEvent.KEYCODE_NUMPAD_ENTER, KeyEvent.KEYCODE_BUTTON_A)
    }
}

/** Unpaired league/team selection sets do not establish associations; only the selected pair is known. */
fun overlayTeamLeagues(profile: ProfileState?): List<String> = listOfNotNull(panelTeamLeague(profile))

/** Window flags: the card never takes focus or touch; the menu and panel take focus and pass outside touches on. */
fun overlayWindowFlags(focusable: Boolean): Int =
    if (focusable) WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL
    else WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE

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

    /** Corner card: 16% wide, 12% tall, at the safe top-right; a showing [alert] keeps the corner and the card sits below it. */
    fun cornerCard(screenWidth: Int, screenHeight: Int, alert: Box?): Box {
        val width = floor(screenWidth * 0.16).toInt()
        val top = alert?.let { it.bottom + gap(screenHeight) } ?: safeTop(screenHeight)
        return Box(safeRight(screenWidth) - width, top, width, floor(screenHeight * 0.12).toInt())
    }

    /** The small menu: right-aligned just below the [card], wherever the card currently sits. */
    fun menu(screenWidth: Int, screenHeight: Int, card: Box): Box {
        val width = floor(screenWidth * 0.20).toInt()
        return Box(safeRight(screenWidth) - width, card.bottom + gap(screenHeight), width, floor(screenHeight * 0.24).toInt())
    }

    private fun gap(height: Int) = ceil(height * 0.01).toInt()
}

/** Corner card and menu look: the theme surface, translucent so the game shows through, with full-strength text. */
object CornerCardStyle {
    /** Effective surface opacity, after WindowManager's untrusted-overlay alpha. */
    const val BACKGROUND_ALPHA = 0.72f
    fun backgroundAlpha(windowAlpha: Float): Float = (BACKGROUND_ALPHA / windowAlpha).coerceAtMost(1f)
    const val MENU_ALPHA = 0.90f
    val TEXT_ARGB = TvPalette.onSurfaceArgb
}

/** The card's few words: matchup and clock; the total; the top two players. */
object CornerCardText {
    fun label(snapshot: PanelSnapshot?, teamLeague: String?): String {
        if (teamLeague == null) return "No team selected"
        if (snapshot == null) return PanelText.matchup(teamLeague)
        return listOfNotNull(PanelText.matchup(snapshot.teamLeague), PanelText.clock(snapshot)).joinToString("  ")
    }

    fun total(snapshot: PanelSnapshot?): String = snapshot?.let { PanelText.points(it.teamTotal) } ?: "–"

    /** One top-two line: short name, points, and whether the points rose since the [prior] refresh of the same pair. */
    data class Leader(val name: String, val points: String, val rose: Boolean, val slot: String? = null)

    fun leaders(snapshot: PanelSnapshot?, prior: PanelSnapshot? = null): List<Leader> {
        val snap = snapshot ?: return emptyList()
        val before = prior?.takeIf { it.teamLeague == snap.teamLeague }?.rows?.associate { it.playerId to it.points.value }.orEmpty()
        return PanelText.byPoints(snap.rows).filter { it.points.value != null }.take(2).map { row ->
            val was = before[row.playerId]
            Leader(PanelText.shortName(row.name), PanelText.points(row.points), was != null && row.points.value!! > was, row.slot)
        }
    }

    fun sport(snapshot: PanelSnapshot?): String? = snapshot?.let {
        it.sport ?: when (it.basis) {
            ScoringBasis.NbaPoints -> "NBA"
            ScoringBasis.YahooLeague, ScoringBasis.Ppr, ScoringBasis.HalfPpr -> "NFL"
        }
    }

    fun hint(serviceEnabled: Boolean): String? = if (serviceEnabled) null else "Hold ≡ needs Accessibility"
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
    val value: Double?,
    val sport: String,
    val watchEventId: String,
)

object AlertCardText {
    /** "D. Mitchell · 30 PTS", or "D. Mitchell · SCORE" when no fresh number is known; null for an unsafe claim. */
    fun label(player: String, value: Double?): String? {
        if (player.isBlank() || AlertPresenter.isUnsafe(player)) return null
        if (value == null || !value.isFinite()) return "$player · SCORE"
        val number = if (value == floor(value)) value.toLong().toString() else value.toString()
        return "$player · $number PTS"
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

    companion object { const val SHOW_MS = 10_000L } // owner 2026-10-23: alert cards stay up 10 s
}

/**
 * Card notice from one inbox alert, or null when the alert has no safe first starter.
 * Optional backend fields win when present: `triggerContext.sport` ("nba"/"nfl"),
 * `starters[0].shortName` and `starters[0].points` (fantasy points on the profile's basis).
 * Without them the player is the starter's short name ("D. Mitchell"), and the number and sport come only from the
 * fresh matching row of the selected [panel] snapshot; with no fresh number the card reads "SCORE" (never dropped).
 */
fun alertCardNotice(alert: Alert, panel: PanelSnapshot?): AlertCardNotice? {
    if (AlertPresenter.text(alert) == null) return null // the panel's safety gate: unsafe names never reach a card
    val trigger = alert.envelope.data.opt("triggerContext") as? JSONObject ?: return null
    val starter = trigger.optJSONArray("starters")?.opt(0) as? JSONObject ?: return null
    val player = ((starter.opt("shortName") as? String)?.trim()?.takeIf { it.isNotEmpty() }
        ?: (starter.opt("name") as? String)?.let(PanelText::shortName))
        ?.takeIf { AlertCardText.label(it, 0.0) != null } ?: return null
    val declaredSport = when (trigger.opt("sport")) { "nba" -> "NBA"; "nfl" -> "NFL"; else -> null }
    val row = panel?.rows?.firstOrNull {
        it.playerId == starter.opt("athlete_id") && (declaredSport == null || declaredSport == CornerCardText.sport(panel))
    }
    val freshPoints = row?.points?.takeIf { points ->
        points.asOfMs?.let { System.currentTimeMillis() - it in 0..60_000 } == true
    }?.value?.takeIf { it.isFinite() }
    // Owner 2026-10-23: an alert always shows, even for a player outside the pair on screen (cross-sport);
    // without a fresh number it reads "SCORE". An unknown sport ("") gets the neutral alert colour.
    val value = (starter.opt("points") as? Number)?.toDouble()?.takeIf { it.isFinite() } ?: freshPoints
    val sport = declaredSport ?: CornerCardText.sport(panel)?.takeIf { row != null && it in listOf("NBA", "NFL") } ?: ""
    return AlertCardNotice(alert.envelope.id, player, value, sport, AlertNotifier.watchEventId(alert).orEmpty())
}

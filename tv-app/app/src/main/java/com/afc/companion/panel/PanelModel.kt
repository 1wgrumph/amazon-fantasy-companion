package com.afc.companion.panel

import android.view.KeyEvent
import com.afc.companion.alerts.AlertNotifier
import com.afc.companion.alerts.AlertPresenter
import com.afc.companion.alerts.AlertText
import com.afc.companion.net.Alert
import com.afc.companion.net.PanelState
import com.afc.companion.net.RoutingOutcome
import java.util.Calendar
import java.util.TimeZone
import org.json.JSONArray
import org.json.JSONObject

// DES-AFC-P2-PANEL host logic (P2-A05). Panel state from the API is untrusted:
// identity/basis/bounds violations reject the whole state, while a malformed
// individual value becomes unavailable (null with a reason), never zero.

/** Scoring context shown with every value (AFC-PR-039: no value without its basis). */
enum class ScoringBasis { YahooLeague, Ppr, HalfPpr }

/** One displayed number from the untrusted PanelState: unknown is a null value with a reason, never zero. */
data class PanelValue(val value: Double?, val reason: String?, val source: String?, val asOfMs: Long?)

data class PanelRow(val playerId: String, val name: String, val points: PanelValue, val gameStatus: String?)

data class PanelSnapshot(
    val teamLeague: String,
    val revision: Long,
    val basis: ScoringBasis,
    val rows: List<PanelRow>,
    val teamTotal: PanelValue,
    val progress: PanelValue,
    /** Envelope lineup source (manual/yahoo), kept separate from per-value live/replay source. */
    val source: String = "live",
)

/** Declared bound on rows accepted from one PanelState (AFC-PR-062). */
val PANEL_ROWS_MAX: Int = 32

/** Stale boundary (AFC-PR-040): age >= 60 s is labeled stale. */
private const val STALE_AFTER_MS = 60_000L

/** Refresh cadence while visible (panel_refresh, AFC-PR-061). */
private const val REFRESH_MS = 30_000L

/** Decodes GET /v1/panel data; null when malformed, oversized or missing its scoring basis. */
fun decodePanel(state: PanelState): PanelSnapshot? {
    val data = state.envelope.data
    val teamLeague = (data.opt("teamLeague") as? String)?.takeIf { it.isNotBlank() } ?: return null
    val basis = when (data.opt("scoringBasis") as? String) {
        "yahooLeague" -> ScoringBasis.YahooLeague
        "ppr" -> ScoringBasis.Ppr
        "halfPpr" -> ScoringBasis.HalfPpr
        else -> return null
    }
    val rawRows = data.opt("rows") as? JSONArray ?: return null
    if (rawRows.length() > PANEL_ROWS_MAX) return null
    val seen = HashSet<String>()
    val rows = ArrayList<PanelRow>(rawRows.length())
    for (i in 0 until rawRows.length()) {
        val row = rawRows.opt(i) as? JSONObject ?: return null
        val playerId = (row.opt("playerId") as? String)?.takeIf { it.isNotBlank() } ?: return null
        if (!seen.add(playerId)) return null
        val name = row.opt("name") as? String ?: return null
        val status = row.opt("gameStatus").let { if (it == JSONObject.NULL) null else it as? String }
        rows += PanelRow(playerId, name, panelValue(row.opt("points") as? JSONObject), status)
    }
    var progress = panelValue(data.opt("progress") as? JSONObject)
    val progressValue = progress.value
    if (progressValue != null && (progressValue < 0.0 || progressValue > 1.0)) {
        progress = progress.copy(value = null, reason = progress.reason ?: "progress out of range")
    }
    return PanelSnapshot(
        teamLeague = teamLeague,
        revision = state.envelope.revision,
        basis = basis,
        rows = rows,
        teamTotal = panelValue(data.opt("teamTotal") as? JSONObject),
        progress = progress,
        source = state.envelope.source,
    )
}

/** A malformed or absent numeric value is unknown with a reason; only a JSON number is a value. */
private fun panelValue(obj: JSONObject?): PanelValue {
    if (obj == null) return PanelValue(null, "unavailable", null, null)
    val raw = obj.opt("value")
    val number = (raw as? Number)?.toDouble()?.takeIf { it.isFinite() }
    val reason = (obj.opt("reason") as? String)?.takeIf { it.isNotBlank() }
    val source = obj.opt("source") as? String
    val asOfMs = parseInstantMs(obj.opt("asOf") as? String)
    return if (number != null) {
        PanelValue(number, reason, source, asOfMs)
    } else {
        PanelValue(null, reason ?: "unavailable", source, asOfMs)
    }
}

private val INSTANT = Regex(
    """^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,9}))?(Z|[+-]\d{2}:\d{2})$""",
)

private fun parseInstantMs(text: String?): Long? {
    val m = text?.let { INSTANT.matchEntire(it) } ?: return null
    return runCatching {
        val g = m.groupValues
        val calendar = Calendar.getInstance(TimeZone.getTimeZone("UTC")).apply {
            isLenient = false
            set(g[1].toInt(), g[2].toInt() - 1, g[3].toInt(), g[4].toInt(), g[5].toInt(), g[6].toInt())
            set(Calendar.MILLISECOND, (g[7] + "000").take(3).toInt())
        }
        val offsetMs = if (g[8] == "Z") 0L else {
            val sign = if (g[8].startsWith("-")) -1L else 1L
            val parts = g[8].substring(1).split(":")
            // RFC3339 time-numoffset is time-hour ":" time-minute (00-23:00-59); an
            // out-of-range offset is invalid, so the value stays undated, never fresh.
            if (parts[0].toInt() !in 0..23 || parts[1].toInt() !in 0..59) return@runCatching null
            sign * (parts[0].toLong() * 3_600_000L + parts[1].toLong() * 60_000L)
        }
        calendar.timeInMillis - offsetMs
    }.getOrNull()
}

/** Text for one value, its basis and a game status; stale and unavailable are labeled (AFC-PR-040). */
object PanelText {
    fun value(value: PanelValue, nowMs: Long): String {
        val number = value.value ?: return "Unavailable"
        val text = number.toString()
        // Only the non-default provenance is labeled: a fresh live value is the bare number.
        val provenance = if (value.source == "replay") "replay" else null
        val stale = when {
            value.asOfMs == null -> "stale"
            nowMs - value.asOfMs >= STALE_AFTER_MS -> "stale ${(nowMs - value.asOfMs) / 1_000}s"
            else -> null
        }
        val labels = listOfNotNull(provenance, stale)
        return if (labels.isEmpty()) text else "$text (${labels.joinToString(", ")})"
    }

    fun lineupSource(source: String): String = when (source) {
        "manual" -> "Manual lineup"
        "yahoo" -> "Yahoo lineup"
        "live" -> "Live"
        "replay" -> "Replay"
        else -> "Source unavailable"
    }

    fun basis(basis: ScoringBasis): String = when (basis) {
        ScoringBasis.YahooLeague -> "Yahoo league scoring"
        ScoringBasis.Ppr -> "PPR"
        ScoringBasis.HalfPpr -> "Half-PPR"
    }

    fun gameStatus(status: String?): String = status?.takeIf { it.isNotBlank() } ?: "Unavailable"

    /** The panel header: scoring basis beside lineup source (AFC-PR-039). */
    fun header(snapshot: PanelSnapshot): String = "${basis(snapshot.basis)} · ${lineupSource(snapshot.source)}"

    /** The reported outcome of the last Watch attempt, shown to the customer (AFC-PR-031). */
    fun watchOutcome(outcome: RoutingOutcome): String = when (outcome) {
        RoutingOutcome.GameOpened -> "Watch: game opened."
        RoutingOutcome.SearchOpened -> "Watch: provider search opened."
        RoutingOutcome.AppHomeOpened -> "Watch: provider app opened."
        RoutingOutcome.AppAbsent -> "Watch: the provider app is not installed."
        RoutingOutcome.AccessUnknown -> "Watch: could not confirm the game is playing."
        RoutingOutcome.PlaybackDenied -> "Watch: the provider app refused the launch."
    }
}

/** Font sizes in sp; at 1080p 1 sp renders as at least 1 px (AFC-PR-045). */
object PanelTextSizes {
    val bodySp: Float = 24f
    val scoreSp: Float = 32f
}

/** The P2-X04 verdict selects the mode; anything but a modeB verdict is fullScreen (AFC-PR-041, -047). */
fun panelModeFor(verdict: String?): PanelMode = if (verdict == "modeB") PanelMode.ModeB else PanelMode.FullScreen

data class Box(val left: Int, val top: Int, val width: Int, val height: Int) {
    val right: Int get() = left + width
    val bottom: Int get() = top + height
}

/** video is null in fullScreen: no stand-in video. */
data class PanelLayout(val video: Box?, val panel: Box)

fun panelLayout(mode: PanelMode, screenWidth: Int, screenHeight: Int, videoAspect: Double = 16.0 / 9.0): PanelLayout {
    if (mode == PanelMode.FullScreen) return PanelLayout(null, Box(0, 0, screenWidth, screenHeight))
    val panelWidth = (screenWidth / 4).coerceIn(1, (screenWidth - 1).coerceAtLeast(1))
    val panel = Box(screenWidth - panelWidth, 0, panelWidth, screenHeight)
    val availableWidth = panel.left
    val video = if (availableWidth / videoAspect <= screenHeight) {
        val height = (availableWidth / videoAspect).toInt()
        Box(0, (screenHeight - height) / 2, availableWidth, height)
    } else {
        Box(0, 0, (screenHeight * videoAspect).toInt(), screenHeight)
    }
    return PanelLayout(video, panel)
}

enum class PanelAction { ToggleVisibility, NextTeamLeague, FocusNext, FocusPrevious, Select }

sealed interface FocusTarget {
    data class AlertWatch(val alertId: String) : FocusTarget
    data class AlertDismiss(val alertId: String) : FocusTarget
    data object TeamLeagueSwitch : FocusTarget
    data class Row(val playerId: String) : FocusTarget
    data object Total : FocusTarget
}

/** One panel-only alert (P2-X02 FAILS); Watch only when the alert names an event an outcome can be reported for. */
data class PanelAlert(val id: String, val text: AlertText, val watchable: Boolean)

/** Alerts shown above the lineup at once; older retained ones appear as newer ones are dismissed. */
const val PANEL_ALERTS_MAX: Int = 3

/** Retained alerts newest first; an alert without safe text is not shown, as the notifier posts nothing for it. */
fun panelAlerts(alerts: List<Alert>): List<PanelAlert> = alerts.asReversed().mapNotNull { alert ->
    AlertPresenter.text(alert)?.let { PanelAlert(alert.envelope.id, it, AlertNotifier.watchEventId(alert) != null) }
}.take(PANEL_ALERTS_MAX)

sealed interface AlertCommand {
    data class Watch(val alertId: String) : AlertCommand
    data class Dismiss(val alertId: String) : AlertCommand
}

/** Rows and totals that one applied update changed; the UI recomposes only these (AFC-PR-061). */
data class PanelDelta(val changedRows: Set<String>, val removedRows: Set<String>, val totalsChanged: Boolean) {
    companion object { val NONE = PanelDelta(emptySet(), emptySet(), false) }
}

/** The device setting "Show panel on new alert" applies to the fullScreen panel only. */
fun revealsOnNewAlert(setting: Boolean, mode: PanelMode): Boolean = setting && mode == PanelMode.FullScreen

/**
 * Remote-driven panel state: one snapshot, visibility, team/league, focus and refresh timing.
 * With [revealOnNewAlert], an alert that arrives after the first [onAlerts] re-shows a hidden panel.
 */
class PanelController(
    teamLeagues: List<String>,
    selected: String?,
    visible: Boolean,
    private val revealOnNewAlert: Boolean = false,
) {
    private val teamLeagues = teamLeagues.toList()
    private var shown = visible
    private var currentTeamLeague: String? = selected ?: this.teamLeagues.firstOrNull()
    private var held: PanelSnapshot? = null
    private var alerts: List<PanelAlert> = emptyList()
    private var alertsSeen = false
    private var armed: String? = null
    private var focus: FocusTarget? = FocusTarget.TeamLeagueSwitch
    private var lastFetchMs: Long? = null
    private var needsFetch = true

    val visible: Boolean get() = shown
    val teamLeague: String? get() = currentTeamLeague
    val snapshot: PanelSnapshot? get() = held
    val focused: FocusTarget? get() = focus
    val panelAlerts: List<PanelAlert> get() = alerts
    /** Alert whose Watch awaits the confirming second press (switching confirmation, AFC-PR-035). */
    val armedWatch: String? get() = armed

    fun focusTargets(): List<FocusTarget> {
        val alertTargets = alerts.flatMap { alert ->
            listOfNotNull(FocusTarget.AlertWatch(alert.id).takeIf { alert.watchable }, FocusTarget.AlertDismiss(alert.id))
        }
        val snap = held ?: return alertTargets + FocusTarget.TeamLeagueSwitch
        return alertTargets + FocusTarget.TeamLeagueSwitch + snap.rows.map { FocusTarget.Row(it.playerId) } + FocusTarget.Total
    }

    fun onAlerts(next: List<PanelAlert>) = keepFocus {
        val arrived = alertsSeen && next.any { alert -> alerts.none { it.id == alert.id } }
        alertsSeen = true
        alerts = next
        if (next.none { it.id == armed }) armed = null
        if (arrived && revealOnNewAlert && !shown) {
            shown = true
            needsFetch = true
        }
    }

    /** OK on a focused alert action; with [confirmSwitch] the first OK on Watch only arms it. */
    fun select(confirmSwitch: Boolean): AlertCommand? {
        if (!shown) return null
        return when (val target = focus) {
            is FocusTarget.AlertDismiss -> AlertCommand.Dismiss(target.alertId)
            is FocusTarget.AlertWatch -> if (confirmSwitch && armed != target.alertId) {
                armed = target.alertId
                null
            } else {
                armed = null
                AlertCommand.Watch(target.alertId)
            }
            else -> null
        }
    }

    fun bindings(): Map<Int, PanelAction> = mapOf(
        KeyEvent.KEYCODE_MENU to PanelAction.ToggleVisibility,
        KeyEvent.KEYCODE_MEDIA_FAST_FORWARD to PanelAction.NextTeamLeague,
        KeyEvent.KEYCODE_DPAD_DOWN to PanelAction.FocusNext,
        KeyEvent.KEYCODE_DPAD_UP to PanelAction.FocusPrevious,
        KeyEvent.KEYCODE_DPAD_CENTER to PanelAction.Select,
        // Keyboards, the Fire TV app remote and game controllers send these for OK.
        KeyEvent.KEYCODE_ENTER to PanelAction.Select,
        KeyEvent.KEYCODE_NUMPAD_ENTER to PanelAction.Select,
        KeyEvent.KEYCODE_BUTTON_A to PanelAction.Select,
    )

    fun onKey(keyCode: Int, nowMs: Long): Boolean {
        val action = bindings()[keyCode] ?: return false
        if (!shown && action != PanelAction.ToggleVisibility) return false
        perform(action, nowMs)
        return true
    }

    fun perform(action: PanelAction, nowMs: Long) {
        when (action) {
            PanelAction.ToggleVisibility -> {
                shown = !shown
                if (shown) needsFetch = true
            }
            PanelAction.NextTeamLeague -> {
                if (teamLeagues.isEmpty()) return
                val index = teamLeagues.indexOf(currentTeamLeague)
                val next = teamLeagues[(index + 1).mod(teamLeagues.size)]
                // One choice (the profile's single pair): keep the held rows, no refetch.
                if (next == currentTeamLeague) return
                currentTeamLeague = next
                held = null
                focus = FocusTarget.TeamLeagueSwitch
                needsFetch = true
            }
            PanelAction.FocusNext -> moveFocus(1)
            PanelAction.FocusPrevious -> moveFocus(-1)
            PanelAction.Select -> Unit // the host runs select(), which needs the profile's switching confirmation
        }
    }

    private fun moveFocus(delta: Int) {
        armed = null
        val targets = focusTargets()
        if (targets.isEmpty()) return
        val index = targets.indexOf(focus)
        focus = when {
            index < 0 -> targets.first()
            else -> targets[(index + delta).coerceIn(0, targets.lastIndex)]
        }
    }

    fun shouldFetch(nowMs: Long): Boolean {
        if (!shown) return false
        if (needsFetch) return true
        val last = lastFetchMs ?: return true
        return nowMs - last >= REFRESH_MS
    }

    fun onFetched(snapshot: PanelSnapshot, nowMs: Long): PanelDelta {
        if (!shown) return PanelDelta.NONE
        if (snapshot.teamLeague != currentTeamLeague) return PanelDelta.NONE
        lastFetchMs = nowMs
        needsFetch = false
        val previous = held
        if (previous != null && snapshot.revision <= previous.revision) return PanelDelta.NONE
        val delta = if (previous == null) {
            PanelDelta(snapshot.rows.map { it.playerId }.toSet(), emptySet(), true)
        } else {
            val previousById = previous.rows.associateBy { it.playerId }
            val changed = snapshot.rows.filter { previousById[it.playerId] != it }.map { it.playerId }.toSet()
            val removed = previousById.keys - snapshot.rows.map { it.playerId }.toSet()
            val totalsChanged = previous.teamTotal != snapshot.teamTotal ||
                previous.progress != snapshot.progress || previous.basis != snapshot.basis || previous.source != snapshot.source
            PanelDelta(changed, removed, totalsChanged)
        }
        keepFocus { held = snapshot }
        return delta
    }

    /** Applies [change]; focus on a vanished element moves to the element now at its position. */
    private fun keepFocus(change: () -> Unit) {
        val oldIndex = focusTargets().indexOf(focus)
        change()
        val newTargets = focusTargets()
        if (focus !in newTargets) {
            focus = if (newTargets.isEmpty()) null else newTargets[oldIndex.coerceIn(0, newTargets.lastIndex)]
        }
    }
}

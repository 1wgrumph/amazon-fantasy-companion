package com.afc.companion.panel

import android.view.KeyEvent
import com.afc.companion.net.PanelState
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
        val asOf = value.asOfMs ?: return "$text (stale)"
        val ageMs = nowMs - asOf
        return if (ageMs >= STALE_AFTER_MS) "$text (stale ${ageMs / 1_000}s)" else text
    }

    fun basis(basis: ScoringBasis): String = when (basis) {
        ScoringBasis.YahooLeague -> "Yahoo league scoring"
        ScoringBasis.Ppr -> "PPR"
        ScoringBasis.HalfPpr -> "Half-PPR"
    }

    fun gameStatus(status: String?): String = status?.takeIf { it.isNotBlank() } ?: "Unavailable"
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

enum class PanelAction { ToggleVisibility, NextTeamLeague, FocusNext, FocusPrevious }

sealed interface FocusTarget {
    data object TeamLeagueSwitch : FocusTarget
    data class Row(val playerId: String) : FocusTarget
    data object Total : FocusTarget
}

/** Rows and totals that one applied update changed; the UI recomposes only these (AFC-PR-061). */
data class PanelDelta(val changedRows: Set<String>, val removedRows: Set<String>, val totalsChanged: Boolean) {
    companion object { val NONE = PanelDelta(emptySet(), emptySet(), false) }
}

/** Remote-driven panel state: one snapshot, visibility, team/league, focus and refresh timing. */
class PanelController(teamLeagues: List<String>, selected: String?, visible: Boolean) {
    private val teamLeagues = teamLeagues.toList()
    private var shown = visible
    private var currentTeamLeague: String? = selected ?: this.teamLeagues.firstOrNull()
    private var held: PanelSnapshot? = null
    private var focus: FocusTarget? = FocusTarget.TeamLeagueSwitch
    private var lastFetchMs: Long? = null
    private var needsFetch = true

    val visible: Boolean get() = shown
    val teamLeague: String? get() = currentTeamLeague
    val snapshot: PanelSnapshot? get() = held
    val focused: FocusTarget? get() = focus

    fun focusTargets(): List<FocusTarget> {
        val snap = held ?: return listOf(FocusTarget.TeamLeagueSwitch)
        return listOf(FocusTarget.TeamLeagueSwitch) + snap.rows.map { FocusTarget.Row(it.playerId) } + FocusTarget.Total
    }

    fun bindings(): Map<Int, PanelAction> = mapOf(
        KeyEvent.KEYCODE_MENU to PanelAction.ToggleVisibility,
        KeyEvent.KEYCODE_MEDIA_FAST_FORWARD to PanelAction.NextTeamLeague,
        KeyEvent.KEYCODE_DPAD_DOWN to PanelAction.FocusNext,
        KeyEvent.KEYCODE_DPAD_UP to PanelAction.FocusPrevious,
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
        }
    }

    private fun moveFocus(delta: Int) {
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
                previous.progress != snapshot.progress || previous.basis != snapshot.basis
            PanelDelta(changed, removed, totalsChanged)
        }
        val oldTargets = focusTargets()
        val oldIndex = oldTargets.indexOf(focus)
        held = snapshot
        val newTargets = focusTargets()
        if (focus !in newTargets) {
            focus = if (newTargets.isEmpty()) null else newTargets[oldIndex.coerceIn(0, newTargets.lastIndex)]
        }
        return delta
    }
}

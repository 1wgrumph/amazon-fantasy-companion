package com.afc.companion.panel

import com.afc.companion.net.PanelState

// AFC-STUB: P2-A05 implements every body in this file behind these final signatures (DES-AFC-P2-PANEL).

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
val PANEL_ROWS_MAX: Int = 0

/** Decodes GET /v1/panel data; null when malformed, oversized or missing its scoring basis. */
fun decodePanel(state: PanelState): PanelSnapshot? = null

/** Text for one value, its basis and a game status; stale and unavailable are labeled (AFC-PR-040). */
object PanelText {
    fun value(value: PanelValue, nowMs: Long): String = ""
    fun basis(basis: ScoringBasis): String = ""
    fun gameStatus(status: String?): String = ""
}

/** Font sizes in sp; at 1080p 1 sp renders as at least 1 px (AFC-PR-045). */
object PanelTextSizes {
    val bodySp: Float = 0f
    val scoreSp: Float = 0f
}

/** The P2-X04 verdict selects the mode; anything but a modeB verdict is fullScreen (AFC-PR-041, -047). */
fun panelModeFor(verdict: String?): PanelMode = PanelMode.FullScreen

data class Box(val left: Int, val top: Int, val width: Int, val height: Int) {
    val right: Int get() = left + width
    val bottom: Int get() = top + height
}

/** video is null in fullScreen: no stand-in video. */
data class PanelLayout(val video: Box?, val panel: Box)

fun panelLayout(mode: PanelMode, screenWidth: Int, screenHeight: Int, videoAspect: Double = 16.0 / 9.0): PanelLayout =
    PanelLayout(null, Box(0, 0, 0, 0))

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
    val visible: Boolean get() = false
    val teamLeague: String? get() = null
    val snapshot: PanelSnapshot? get() = null
    val focused: FocusTarget? get() = null
    fun focusTargets(): List<FocusTarget> = emptyList()
    fun bindings(): Map<Int, PanelAction> = emptyMap()
    fun onKey(keyCode: Int, nowMs: Long): Boolean = false
    fun perform(action: PanelAction, nowMs: Long) {}
    fun shouldFetch(nowMs: Long): Boolean = false
    fun onFetched(snapshot: PanelSnapshot, nowMs: Long): PanelDelta = PanelDelta.NONE
}

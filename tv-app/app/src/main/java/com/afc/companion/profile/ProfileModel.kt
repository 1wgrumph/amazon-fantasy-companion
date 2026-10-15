package com.afc.companion.profile

import com.afc.companion.net.ApiClient
import com.afc.companion.net.ScoringPreset
import com.afc.companion.net.Settings

// AFC-STUB: P2-A02 implements PROFILE (codec, store, override, control set) behind these final signatures.

enum class AlertType { RedZone, PlayerScore, CloseGame }
enum class Presentation { HeadsUp, PanelOnly }
enum class Excitement { Off, Mild, Hype }

/** Minutes of the local day, 0..1439; a window may wrap past midnight. */
data class TimeWindow(val startMinute: Int, val endMinute: Int)

data class FantasySelections(val leagues: Set<String>, val teams: Set<String>, val players: Set<String>, val favoriteTeams: Set<String>)
data class TeamLeague(val league: String, val team: String)
data class GameDayMode(val enabled: Boolean, val periods: List<TimeWindow>)

/** Provider order, explicit access confirmations, customer overrides of detected apps, retained local market. */
data class ProviderPreference(
    val order: List<String>,
    val confirmedAccess: Set<String>,
    val appOverrides: Map<String, Boolean>,
    val localMarket: String?,
)
data class PanelPrefs(val visible: Boolean)

data class ProfileState(
    val selections: FantasySelections,
    val teamLeague: TeamLeague?,
    val alertTypes: Set<AlertType>,
    val minGapSeconds: Int,
    val quietHours: List<TimeWindow>,
    val gameDay: GameDayMode,
    val spoilerDelaySeconds: Int,
    val presentation: Presentation,
    val voiceEnabled: Boolean,
    val excitement: Excitement,
    val providerPref: ProviderPreference,
    val switchingConfirm: Boolean,
    val panel: PanelPrefs,
    val detectionOptIn: Boolean,
    val scoringPreset: ScoringPreset,
)

object ProfileCodec {
    /** Persisted settings are untrusted: any invalid control yields null. */
    fun decode(settings: Settings): ProfileState? = null
    fun encode(state: ProfileState): Settings = Settings()
}

/** Installed apps after the customer's review: overrides win over detection. */
fun ProfileState.effectiveInstalled(detected: Set<String>): Set<String> = emptySet()

/** Voice speaks only while enabled and over a verified route (AFC-PR-022). */
fun ProfileState.voiceActive(routeVerified: Boolean): Boolean = false

enum class ProfileControl {
    Selections, TeamLeague, AlertTypes, Frequency, QuietHours, GameDay, SpoilerDelay, Presentation,
    Voice, Excitement, ProviderPreference, SwitchingConfirmation, DetectionOptIn, PanelVisibility, ScoringPreset,
}

/** Visible controls, and a stated limit for each control hidden because its platform route is unsupported. */
data class ControlSet(val visible: List<ProfileControl>, val limits: Map<ProfileControl, String>)

fun profileControls(detectionSupported: Boolean, voiceRouteVerified: Boolean): ControlSet = ControlSet(emptyList(), emptyMap())

/** GET/PUT /v1/profile; save writes against the revision held from load. Null when unavailable, invalid or stale. */
class ProfileStore(private val client: ApiClient) {
    suspend fun load(): ProfileState? = null
    suspend fun save(state: ProfileState): ProfileState? = null
}

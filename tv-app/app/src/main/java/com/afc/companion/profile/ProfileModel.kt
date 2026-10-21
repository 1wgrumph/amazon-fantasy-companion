package com.afc.companion.profile

import com.afc.companion.net.ApiClient
import com.afc.companion.net.ProfileUpdate
import com.afc.companion.net.ScoringPreset
import com.afc.companion.net.Settings
import org.json.JSONArray
import org.json.JSONObject

enum class AlertType { RedZone, PlayerScore, CloseGame }
enum class Presentation { HeadsUp, PanelOnly }
enum class Excitement { Off, Mild, Hype }
enum class Sport(val wire: String, val label: String) { Nfl("nfl", "NFL"), Nba("nba", "NBA") }

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
    val sports: Map<Sport, Boolean>? = null,
) {
    fun sportEnabled(sport: Sport): Boolean = sports?.get(sport) ?: true
}

/**
 * One control per frozen Settings field. Persisted settings are untrusted:
 * decode validates every present field's type, enum and range and returns
 * null whole on any violation; absent fields take the documented defaults.
 */
object ProfileCodec {
    fun decode(settings: Settings): ProfileState? {
        val c = settings.controls
        val selections = field(c, "fantasySelections", FantasySelections(emptySet(), emptySet(), emptySet(), emptySet())) { v ->
            val o = v as? JSONObject ?: return null
            if (o.keys().asSequence().any { it !in SELECTION_KEYS }) return null
            FantasySelections(
                stringSet(o, "leagues") ?: return null, stringSet(o, "teams") ?: return null,
                stringSet(o, "players") ?: return null, stringSet(o, "favoriteTeams") ?: return null,
            )
        } ?: return null
        val teamLeague: TeamLeague? = if (!c.has("teamLeague") || c.opt("teamLeague") == JSONObject.NULL) null else {
            val o = c.opt("teamLeague") as? JSONObject ?: return null
            TeamLeague(o.opt("league") as? String ?: return null, o.opt("team") as? String ?: return null)
        }
        val alertTypes = field(c, "alertTypes", emptySet()) { v ->
            strings(v)?.map { name -> enumValues<AlertType>().firstOrNull { it.name == name } ?: return null }?.toSet()
        } ?: return null
        val minGap = field(c, "frequency", 120) { intIn(it, 0..600) } ?: return null
        val quiet = field(c, "quietHours", emptyList()) { windows(it) } ?: return null
        val gameDay = field(c, "gameDayPeriods", GameDayMode(false, emptyList())) { v ->
            val o = v as? JSONObject ?: return null
            GameDayMode(o.opt("enabled") as? Boolean ?: return null, windows(o.opt("periods")) ?: return null)
        } ?: return null
        val spoiler = field(c, "spoilerDelay", 0) { intIn(it, 0..120) } ?: return null
        val presentation = field(c, "presentation", Presentation.HeadsUp) { v -> enumValues<Presentation>().firstOrNull { it.name == v } } ?: return null
        val voice = field(c, "voice", false) { it as? Boolean } ?: return null
        val excitement = field(c, "excitement", Excitement.Off) { v -> enumValues<Excitement>().firstOrNull { it.name == v } } ?: return null
        val providerPref = field(c, "providerPref", ProviderPreference(emptyList(), emptySet(), emptyMap(), null)) { v ->
            val o = v as? JSONObject ?: return null
            val overrides = o.opt("appOverrides") as? JSONObject ?: return null
            val map = overrides.keys().asSequence().associateWith { overrides.opt(it) as? Boolean ?: return null }
            val market = o.opt("localMarket").let { if (it == JSONObject.NULL) null else it as? String ?: return null }
            ProviderPreference(
                stringList(o, "order") ?: return null, stringSet(o, "confirmedAccess") ?: return null, map, market,
            )
        } ?: return null
        val switching = field(c, "switchingConfirm", true) { it as? Boolean } ?: return null
        val panel = field(c, "panelPrefs", PanelPrefs(true)) { v ->
            ((v as? JSONObject)?.opt("visible") as? Boolean)?.let(::PanelPrefs)
        } ?: return null
        val detection = field(c, "detectionOptIn", false) { it as? Boolean } ?: return null
        val sports = if (!c.has("sports")) null else {
            val o = c.opt("sports") as? JSONObject ?: return null
            if (o.keys().asSequence().any { key -> Sport.entries.none { it.wire == key } }) return null
            Sport.entries.associateWith { sport ->
                if (o.has(sport.wire)) o.opt(sport.wire) as? Boolean ?: return null else true
            }
        }
        return ProfileState(
            selections, teamLeague, alertTypes, minGap, quiet, gameDay, spoiler, presentation, voice,
            excitement, providerPref, switching, panel, detection, settings.scoringPreset, sports,
        )
    }

    fun encode(state: ProfileState): Settings {
        require(state.minGapSeconds in 0..600) { "alert_min_gap out of range" }
        require(state.spoilerDelaySeconds in 0..120) { "spoiler_delay out of range" }
        (state.quietHours + state.gameDay.periods).forEach {
            require(it.startMinute in 0..1439 && it.endMinute in 0..1439) { "minute of day out of range" }
        }
        val c = JSONObject()
            .put("fantasySelections", JSONObject()
                .put("leagues", JSONArray(state.selections.leagues.toList()))
                .put("teams", JSONArray(state.selections.teams.toList()))
                .put("players", JSONArray(state.selections.players.toList()))
                .put("favoriteTeams", JSONArray(state.selections.favoriteTeams.toList())))
            .put("teamLeague", state.teamLeague?.let { JSONObject().put("league", it.league).put("team", it.team) } ?: JSONObject.NULL)
            .put("alertTypes", JSONArray(state.alertTypes.map { it.name }))
            .put("frequency", state.minGapSeconds)
            .put("quietHours", windowsJson(state.quietHours))
            .put("gameDayPeriods", JSONObject().put("enabled", state.gameDay.enabled).put("periods", windowsJson(state.gameDay.periods)))
            .put("spoilerDelay", state.spoilerDelaySeconds)
            .put("presentation", state.presentation.name)
            .put("voice", state.voiceEnabled)
            .put("excitement", state.excitement.name)
            .put("providerPref", JSONObject()
                .put("order", JSONArray(state.providerPref.order))
                .put("confirmedAccess", JSONArray(state.providerPref.confirmedAccess.toList()))
                .put("appOverrides", JSONObject().apply { state.providerPref.appOverrides.forEach { (k, v) -> put(k, v) } })
                .put("localMarket", state.providerPref.localMarket ?: JSONObject.NULL))
            .put("switchingConfirm", state.switchingConfirm)
            .put("panelPrefs", JSONObject().put("visible", state.panel.visible))
            .put("detectionOptIn", state.detectionOptIn)
        if (state.sports != null) {
            c.put("sports", JSONObject().apply {
                Sport.entries.forEach { put(it.wire, state.sportEnabled(it)) }
            })
        }
        return Settings(state.scoringPreset, c, nbaEnabled = state.sports != null)
    }

    private val SELECTION_KEYS = setOf("leagues", "teams", "players", "favoriteTeams")

    /** Absent yields [default]; present must parse or the whole decode fails. */
    private inline fun <T> field(c: JSONObject, key: String, default: T, parse: (Any?) -> T?): T? =
        if (!c.has(key)) default else parse(c.opt(key))

    private fun intIn(v: Any?, range: IntRange): Int? = when (v) {
        is Int -> v.takeIf { it in range }
        is Long -> v.toInt().takeIf { it.toLong() == v && it in range }
        else -> null
    }

    private fun strings(v: Any?): List<String>? {
        val a = v as? JSONArray ?: return null
        return (0 until a.length()).map { a.opt(it) as? String ?: return null }
    }

    private fun stringList(o: JSONObject, key: String): List<String>? = strings(o.opt(key))
    private fun stringSet(o: JSONObject, key: String): Set<String>? = strings(o.opt(key))?.toSet()

    private fun windows(v: Any?): List<TimeWindow>? {
        val a = v as? JSONArray ?: return null
        return (0 until a.length()).map { i ->
            val o = a.opt(i) as? JSONObject ?: return null
            TimeWindow(intIn(o.opt("startMinute"), 0..1439) ?: return null, intIn(o.opt("endMinute"), 0..1439) ?: return null)
        }
    }

    private fun windowsJson(windows: List<TimeWindow>): JSONArray =
        JSONArray(windows.map { JSONObject().put("startMinute", it.startMinute).put("endMinute", it.endMinute) })
}

/** Installed apps after the customer's review: overrides win over detection. */
fun ProfileState.effectiveInstalled(detected: Set<String>): Set<String> =
    detected.filterTo(mutableSetOf()) { providerPref.appOverrides[it] != false } +
        providerPref.appOverrides.filterValues { it }.keys

/** Voice speaks only while enabled and over a verified route (AFC-PR-022). */
fun ProfileState.voiceActive(routeVerified: Boolean): Boolean = voiceEnabled && routeVerified

enum class ProfileControl {
    Selections, TeamLeague, AlertTypes, Frequency, QuietHours, GameDay, SpoilerDelay, Presentation,
    Voice, Excitement, ProviderPreference, SwitchingConfirmation, DetectionOptIn, PanelVisibility, ScoringPreset,
}

/** Visible controls, and a stated limit for each control hidden because its platform route is unsupported. */
data class ControlSet(val visible: List<ProfileControl>, val limits: Map<ProfileControl, String>)

fun profileControls(detectionSupported: Boolean, voiceRouteVerified: Boolean): ControlSet {
    val limits = buildMap {
        if (!detectionSupported) put(
            ProfileControl.DetectionOptIn,
            "Installed-app detection is not supported on this device, so detection cannot be enabled here.",
        )
        if (!voiceRouteVerified) put(
            ProfileControl.Voice,
            "No verified voice route is available on this device, so voice alerts cannot be enabled here.",
        )
    }
    return ControlSet(ProfileControl.entries.filter { it !in limits }, limits)
}

/** GET/PUT /v1/profile; save writes against the revision held from load. Null when unavailable, invalid or stale. */
class ProfileStore(private val client: ApiClient) {
    private var revision: Long? = null

    suspend fun load(): ProfileState? = runCatching {
        val profile = client.getProfile().value ?: return null
        val state = ProfileCodec.decode(profile.settings) ?: return null
        revision = profile.envelope.revision
        state
    }.getOrNull()

    suspend fun save(state: ProfileState): ProfileState? = runCatching {
        val held = revision ?: load()?.let { revision } ?: return null
        val profile = client.putProfile(ProfileUpdate(held, ProfileCodec.encode(state))).value ?: return null
        val stored = ProfileCodec.decode(profile.settings) ?: return null
        revision = profile.envelope.revision
        stored
    }.getOrNull()
}

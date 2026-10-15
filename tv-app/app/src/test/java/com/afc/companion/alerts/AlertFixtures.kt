package com.afc.companion.alerts

import com.afc.companion.net.Alert
import com.afc.companion.net.Envelope
import com.afc.companion.profile.Excitement
import com.afc.companion.profile.FantasySelections
import com.afc.companion.profile.GameDayMode
import com.afc.companion.profile.PanelPrefs
import com.afc.companion.profile.Presentation
import com.afc.companion.profile.ProfileState
import com.afc.companion.profile.ProviderPreference
import com.afc.companion.net.ScoringPreset
import org.json.JSONArray
import org.json.JSONObject

// Resource group: none shared. Pages are served by com.afc.companion.LocalApi on an OS-assigned loopback port.
// Alert data follows the store's Alert attributes (alertType, triggerContext, commentary) and Dto's data.route.

internal const val PLAYER = "Player Eleven"
internal const val MATCHUP = "KC at BUF"

internal fun route(basis: String, provider: String? = "provider-a"): JSONObject =
    JSONObject().put("accessBasis", basis).put("provider", provider ?: JSONObject.NULL)

internal fun alertData(
    type: String = "redZone",
    player: String? = PLAYER,
    matchup: String? = MATCHUP,
    commentary: String? = null,
    route: JSONObject? = route("unknown"),
): JSONObject = JSONObject()
    .put("alertType", type)
    .put("eventId", "evt-fixture")
    .put("triggerContext", JSONObject().apply { player?.let { put("player", it) }; matchup?.let { put("matchup", it) } })
    .put("commentary", commentary ?: JSONObject.NULL)
    .put("route", route ?: JSONObject.NULL)

internal fun alertJson(id: String, revision: Long = 1, data: JSONObject = alertData()): JSONObject = JSONObject()
    .put("schemaVersion", 1).put("id", id).put("revision", revision).put("source", "replay")
    .put("updatedAt", "2026-10-15T00:20:00Z").put("eventTime", "2026-10-15T00:19:30Z").put("data", data)

internal fun alert(data: JSONObject = alertData()): Alert =
    checkNotNull(Envelope.from(alertJson("alert-fixture", 1, data))?.let(Alert::from)) { "fixture must satisfy the A01 decoder" }

internal fun page(cursor: String, vararg alerts: JSONObject): Pair<Int, String> =
    200 to JSONObject().put("alerts", JSONArray(alerts.toList())).put("cursor", cursor).toString()

internal fun profile(presentation: Presentation = Presentation.HeadsUp, voice: Boolean = false): ProfileState = ProfileState(
    selections = FantasySelections(emptySet(), emptySet(), setOf("player-11"), emptySet()),
    teamLeague = null,
    alertTypes = emptySet(),
    minGapSeconds = 120,
    quietHours = emptyList(),
    gameDay = GameDayMode(false, emptyList()),
    spoilerDelaySeconds = 0,
    presentation = presentation,
    voiceEnabled = voice,
    excitement = Excitement.Off,
    providerPref = ProviderPreference(emptyList(), emptySet(), emptyMap(), null),
    switchingConfirm = true,
    panel = PanelPrefs(true),
    detectionOptIn = false,
    scoringPreset = ScoringPreset.HalfPpr,
)

/** Every line the customer can see. */
internal fun AlertText.all(): String = listOfNotNull(headline, context, access, commentary).joinToString("\n")

package com.afc.companion.net

import com.afc.companion.BuildConfig
import org.json.JSONArray
import org.json.JSONObject

/** Request and response types for every CONTRACT-AFC-P2-API operation. Decoders return null on contract violations. */
data class ApiResponse(val status: Int, val body: JSONObject?)

data class ApiResult<out T : Any>(val status: Int, val value: T?, val error: ApiError?)

data class ApiError(val code: String, val message: String) {
    companion object {
        fun from(body: JSONObject?): ApiError? {
            val error = body?.opt("error") as? JSONObject ?: return null
            val code = error.opt("code") as? String ?: return null
            val message = error.opt("message") as? String ?: return null
            return ApiError(code, message)
        }
    }
}

/** CONTRACT-AFC-P2-ENVELOPE. A revision older than the one held is rejected. */
data class Envelope(
    val schemaVersion: Int,
    val id: String,
    val revision: Long,
    val source: String,
    val updatedAt: String,
    val eventTime: String?,
    val data: JSONObject,
) {
    companion object {
        const val SCHEMA_VERSION = 1
        val SOURCES = setOf("live", "replay", "yahoo", "manual")

        fun from(json: JSONObject, heldRevision: Long? = null): Envelope? {
            val schemaVersion = integral(json.opt("schemaVersion"))?.takeIf { it == SCHEMA_VERSION.toLong() } ?: return null
            val id = (json.opt("id") as? String)?.takeIf { it.isNotEmpty() } ?: return null
            val revision = integral(json.opt("revision"))?.takeIf { it >= 0 } ?: return null
            if (heldRevision != null && revision < heldRevision) return null
            val source = (json.opt("source") as? String)?.takeIf { it in SOURCES } ?: return null
            val updatedAt = timestamp(json.opt("updatedAt")) ?: return null
            val eventTime = if (json.has("eventTime")) timestamp(json.opt("eventTime")) ?: return null else null
            val data = json.opt("data") as? JSONObject ?: return null
            return Envelope(schemaVersion.toInt(), id, revision, source, updatedAt, eventTime, data)
        }
    }
}

data class DeviceCode(val code: String, val expires: String, val handle: String) {
    companion object {
        private val CODE = Regex("^[ABCDEFGHJKLMNPQRSTUVWXYZ23456789]{8}$")
        fun from(json: JSONObject): DeviceCode? {
            val code = (json.opt("code") as? String)?.takeIf { CODE.matches(it) } ?: return null
            val expires = timestamp(json.opt("expires")) ?: return null
            val handle = (json.opt("handle") as? String)?.takeIf { it.isNotEmpty() } ?: return null
            return DeviceCode(code, expires, handle)
        }
    }
}

enum class LinkStatus(val wire: String) {
    Unlinked("unlinked"), CodePending("codePending"), Linked("linked"), Expired("expired");
    companion object { fun of(wire: Any?): LinkStatus? = entries.firstOrNull { it.wire == wire } }
}

/** The session token never appears in toString, logs or presentation. */
class LinkState(val state: LinkStatus, val sessionToken: String?) {
    override fun toString(): String = "LinkState(state=$state, sessionToken=${if (sessionToken == null) "absent" else "redacted"})"
    companion object {
        fun from(json: JSONObject): LinkState? {
            val state = LinkStatus.of(json.opt("state")) ?: return null
            val token = json.opt("sessionToken")?.let { it as? String ?: return null }
            return LinkState(state, token)
        }
    }
}

class LinkConfirm(val code: String, val passphrase: String, val profileId: String) {
    override fun toString(): String = "LinkConfirm(code=$code, profileId=$profileId)"
    fun toJson(): JSONObject = JSONObject().put("code", code).put("passphrase", passphrase).put("profileId", profileId)
}

enum class ScoringPreset(val wire: String) {
    Ppr("ppr"), HalfPpr("halfPpr");
    companion object { fun of(wire: Any?): ScoringPreset? = entries.firstOrNull { it.wire == wire } }
}

/** Settings: additionalProperties false; scoringPreset defaults to Half-PPR. Other controls stay opaque until P2-A02. */
class Settings(
    val scoringPreset: ScoringPreset = ScoringPreset.HalfPpr,
    controls: JSONObject = JSONObject(),
    nbaEnabled: Boolean = BuildConfig.AFC_ENABLE_NBA,
) {
    val controls: JSONObject = JSONObject(controls.toString())

    init { require(this.controls.keys().asSequence().all { it in CONTROLS || (nbaEnabled && it == "sports") }) { "Unknown settings field" } }

    fun toJson(): JSONObject = JSONObject(controls.toString()).put("scoringPreset", scoringPreset.wire)

    companion object {
        val CONTROLS = setOf(
            "fantasySelections", "teamLeague", "alertTypes", "frequency", "quietHours", "gameDayPeriods", "spoilerDelay",
            "presentation", "voice", "excitement", "providerPref", "switchingConfirm", "panelPrefs", "detectionOptIn",
        )

        fun from(json: JSONObject, nbaEnabled: Boolean = BuildConfig.AFC_ENABLE_NBA): Settings? {
            val preset = if (json.has("scoringPreset")) ScoringPreset.of(json.opt("scoringPreset")) ?: return null else ScoringPreset.HalfPpr
            val controls = JSONObject(json.toString()).apply { remove("scoringPreset") }
            if (!controls.keys().asSequence().all { it in CONTROLS || (nbaEnabled && it == "sports") }) return null
            return Settings(preset, controls, nbaEnabled)
        }
    }
}

class Profile(val envelope: Envelope, val settings: Settings) {
    companion object {
        fun from(json: JSONObject, heldRevision: Long? = null): Profile? {
            val envelope = Envelope.from(json, heldRevision) ?: return null
            return Settings.from(envelope.data)?.let { Profile(envelope, it) }
        }
    }
}

class ProfileUpdate(val revision: Long, val settings: Settings, val profileId: String? = null) {
    init { require(revision >= 0) { "revision must be non-negative" } }
    fun toJson(): JSONObject = JSONObject().put("revision", revision).put("data", settings.toJson())
        .apply { profileId?.let { put("profileId", it) } }
}

enum class AccessBasis(val wire: String) {
    Verified("verified"), CustomerConfirmed("customerConfirmed"), Unknown("unknown");
    companion object { fun of(wire: Any?): AccessBasis? = entries.firstOrNull { it.wire == wire } }
}

/** GET /v1/providers: resolved route and access basis; never inferred from installed apps. */
class ProviderRoute(val provider: String?, val channel: String?, val route: JSONObject?, val accessBasis: AccessBasis) {
    companion object {
        fun from(json: JSONObject): ProviderRoute? {
            val basis = AccessBasis.of(json.opt("accessBasis")) ?: return null
            val provider = optional<String>(json, "provider") ?: return null
            val channel = optional<String>(json, "channel") ?: return null
            val route = optional<JSONObject>(json, "route") ?: return null
            return ProviderRoute(provider.value, channel.value, route.value, basis)
        }
    }
}

/** An alert envelope; data.route (a ProviderRoute) is optional and absent access shows as unknown (AFC-PR-032). */
class Alert(val envelope: Envelope, val route: ProviderRoute?) {
    val accessBasis: AccessBasis get() = route?.accessBasis ?: AccessBasis.Unknown
    companion object {
        fun from(envelope: Envelope): Alert? {
            val route = optional<JSONObject>(envelope.data, "route") ?: return null
            return Alert(envelope, route.value?.let { ProviderRoute.from(it) ?: return null })
        }
    }
}

/** GET /v1/alerts: one invalid entry rejects the page, so nothing is partially applied. */
class AlertsPage(val alerts: List<Alert>, val cursor: String) {
    companion object {
        fun from(json: JSONObject): AlertsPage? {
            val items = json.opt("alerts") as? JSONArray ?: return null
            val cursor = json.opt("cursor") as? String ?: return null
            val alerts = (0 until items.length()).map { i ->
                (items.opt(i) as? JSONObject)?.let(Envelope::from)?.let(Alert::from) ?: return null
            }
            return AlertsPage(alerts, cursor)
        }
    }
}

/** GET /v1/panel: PanelState envelope; P2-A05 reads rows, totals and scoring basis from data. */
class PanelState(val envelope: Envelope) {
    companion object {
        fun from(json: JSONObject, heldRevision: Long? = null): PanelState? = Envelope.from(json, heldRevision)?.let(::PanelState)
    }
}

enum class RoutingOutcome(val wire: String) {
    GameOpened("gameOpened"), SearchOpened("searchOpened"), AppHomeOpened("appHomeOpened"),
    AppAbsent("appAbsent"), AccessUnknown("accessUnknown"), PlaybackDenied("playbackDenied"),
}

class RoutingOutcomeReport(val eventId: String, val outcome: RoutingOutcome, val profileId: String? = null) {
    init { require(eventId.length in 1..256) { "eventId length" } }
    fun toJson(): JSONObject = JSONObject().put("eventId", eventId).put("outcome", outcome.wire)
        .apply { profileId?.let { put("profileId", it) } }
}

class InstalledApps(val packages: List<String>, val profileId: String? = null) {
    init {
        require(packages.size <= MAX_PACKAGES) { "At most $MAX_PACKAGES packages" }
        require(packages.all { PACKAGE.matches(it) }) { "Invalid package name" }
    }
    fun toJson(): JSONObject = JSONObject().put("packages", JSONArray(packages))
        .apply { profileId?.let { put("profileId", it) } }
    companion object {
        const val MAX_PACKAGES = 500
        private val PACKAGE = Regex("^[A-Za-z0-9._]{1,255}$")
    }
}

private class Present<out T>(val value: T?)

/** Absent or JSON null yields Present(null); a value of the wrong type yields null. */
private inline fun <reified T> optional(json: JSONObject, key: String): Present<T>? {
    val value = json.opt(key)
    if (value == null || value == JSONObject.NULL) return Present(null)
    return (value as? T)?.let { Present(it) }
}

private fun integral(value: Any?): Long? = when (value) {
    is Int -> value.toLong()
    is Long -> value
    else -> null
}

private val RFC3339 = Regex(
    "^\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])T([01]\\d|2[0-3]):[0-5]\\d:([0-5]\\d|60)(\\.\\d{1,9})?(Z|[+-]([01]\\d|2[0-3]):[0-5]\\d)$",
)

private fun timestamp(value: Any?): String? = (value as? String)?.takeIf { RFC3339.matches(it) }

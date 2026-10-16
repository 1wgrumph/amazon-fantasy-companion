package com.afc.companion.alerts

import com.afc.companion.net.AccessBasis
import com.afc.companion.net.Alert
import com.afc.companion.profile.Presentation
import com.afc.companion.profile.ProfileState
import com.afc.companion.profile.voiceActive
import org.json.JSONArray
import org.json.JSONObject

enum class AlertAction { Watch, Dismiss }

/** Customer-visible alert text: headline, triggering player and matchup context, access label, optional commentary. */
data class AlertText(val headline: String, val context: String, val access: String, val commentary: String?)

/** What NOTIFIER renders for one alert. */
data class AlertView(val presentation: Presentation, val actions: List<AlertAction>, val text: AlertText, val speak: Boolean)

/**
 * NOTIFIER's presentation, alert text and voice gate. Alert payloads are untrusted: the headline is
 * ours, player/matchup/commentary are sanitized and bounded, and any displayed field carrying an
 * on-field, will-score or access claim is dropped whole rather than edited (AFC-PR-027, -028, -032).
 * Claims are matched on a normalized form (non-alphanumerics collapsed to one space) so whitespace
 * or punctuation variants such as "will  score" or "on-the-field" cannot slip through.
 */
object AlertPresenter {
    // Matched by isUnsafe against normalized text, where words are separated by single spaces.
    private val unsafeClaim = Regex(
        "(?i)\\b(on the field|on field|will score|going to score|about to score|is scoring|set to score|sure to score|guaranteed" +
            "|includ(ed|es)|subscribed)\\b|(?<!not )\\bverified\\b",
    )

    /** Null when the alert lacks safe triggering context. Server payloads carry structured starters, no matchup yet. */
    fun text(alert: Alert): AlertText? {
        val data = alert.envelope.data
        val trigger = data.opt("triggerContext") as? JSONObject ?: return null
        // A present matchup must be safe; an absent or null one is simply not shown (never fabricated).
        val matchup = if (trigger.has("matchup") && !trigger.isNull("matchup")) {
            clean(trigger.opt("matchup"))?.takeUnless(::isUnsafe) ?: return null
        } else {
            null
        }
        val player = if (trigger.has("starters")) {
            val starters = trigger.opt("starters") as? JSONArray ?: return null
            val names = (0 until starters.length()).map { i ->
                val starter = starters.opt(i) as? JSONObject ?: return null
                clean(starter.opt("name"))?.takeUnless(::isUnsafe) ?: return null
            }
            // Empty starters is a correction: present without claiming any player triggered it.
            if (names.isEmpty()) "Update for your lineup" else boundedNames(names)
        } else {
            // Legacy fixture shape: both player and matchup remain required, as before.
            if (matchup == null) return null
            clean(trigger.opt("player"))?.takeUnless(::isUnsafe) ?: return null
        }
        if (isUnsafe(listOfNotNull(player, matchup).joinToString(" "))) return null // a claim may span the boundary
        val commentary = clean(data.opt("commentary"), MAX_COMMENTARY_LENGTH)?.takeUnless(::isUnsafe)
        return AlertText(
            headline = when (data.opt("alertType")) {
                "RedZone", "redZone" -> "Red-zone alert"
                "PlayerScore", "playerScore" -> "Score update"
                "CloseGame", "closeGame" -> "Close game alert"
                else -> "Game alert"
            },
            context = if (matchup == null) player else "$player — $matchup",
            access = when (alert.accessBasis) {
                AccessBasis.Verified -> "Access: verified"
                AccessBasis.CustomerConfirmed -> "Access: confirmed by you"
                AccessBasis.Unknown -> "Access: unknown"
            },
            commentary = commentary,
        )
    }

    fun view(alert: Alert, profile: ProfileState, voiceRouteVerified: Boolean = false): AlertView? {
        val text = text(alert) ?: return null
        return AlertView(
            presentation = profile.presentation,
            actions = if (profile.presentation == Presentation.HeadsUp) {
                listOf(AlertAction.Watch, AlertAction.Dismiss)
            } else {
                emptyList()
            },
            text = text,
            speak = profile.voiceActive(voiceRouteVerified),
        )
    }

    /** Joined starter names bounded to one context field; the remainder is counted, not spelled out. */
    private fun boundedNames(names: List<String>): String {
        val joined = names.joinToString(", ")
        if (joined.length <= MAX_CONTEXT_LENGTH) return joined
        for (shown in names.size - 1 downTo 1) {
            val candidate = names.take(shown).joinToString(", ") + ", +${names.size - shown} more"
            if (candidate.length <= MAX_CONTEXT_LENGTH) return candidate
        }
        val suffix = ", +${names.size - 1} more"
        return names[0].take(MAX_CONTEXT_LENGTH - suffix.length) + suffix
    }

    private const val MAX_CONTEXT_LENGTH = 80
    private const val MAX_COMMENTARY_LENGTH = 240

    private fun isUnsafe(value: String): Boolean = unsafeClaim.containsMatchIn(
        value.replace(Regex("[^\\p{L}\\p{N}]+"), " ").trim(),
    )

    private fun clean(value: Any?, maxLength: Int = MAX_CONTEXT_LENGTH): String? =
        (value as? String)?.replace(Regex("[\\p{Cntrl}\\s]+"), " ")?.trim()?.take(maxLength)?.takeIf { it.isNotBlank() }
}

package com.afc.companion.alerts

import com.afc.companion.net.AccessBasis
import com.afc.companion.net.Alert
import com.afc.companion.profile.Presentation
import com.afc.companion.profile.ProfileState
import com.afc.companion.profile.voiceActive
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

    /** Null when the alert lacks safe triggering player and matchup context. */
    fun text(alert: Alert): AlertText? {
        val data = alert.envelope.data
        val trigger = data.opt("triggerContext") as? JSONObject ?: return null
        val player = clean(trigger.opt("player"))?.takeUnless(::isUnsafe) ?: return null
        val matchup = clean(trigger.opt("matchup"))?.takeUnless(::isUnsafe) ?: return null
        if (isUnsafe("$player $matchup")) return null // a claim may span the player/matchup boundary
        val commentary = clean(data.opt("commentary"), MAX_COMMENTARY_LENGTH)?.takeUnless(::isUnsafe)
        return AlertText(
            headline = when (data.opt("alertType")) {
                "redZone" -> "Red-zone alert"
                "playerScore" -> "Score update"
                "closeGame" -> "Close game alert"
                else -> "Game alert"
            },
            context = "$player — $matchup",
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

    private const val MAX_CONTEXT_LENGTH = 80
    private const val MAX_COMMENTARY_LENGTH = 240

    private fun isUnsafe(value: String): Boolean = unsafeClaim.containsMatchIn(
        value.replace(Regex("[^\\p{L}\\p{N}]+"), " ").trim(),
    )

    private fun clean(value: Any?, maxLength: Int = MAX_CONTEXT_LENGTH): String? =
        (value as? String)?.replace(Regex("[\\p{Cntrl}\\s]+"), " ")?.trim()?.take(maxLength)?.takeIf { it.isNotBlank() }
}

package com.afc.companion.alerts

import com.afc.companion.net.Alert
import com.afc.companion.profile.Presentation
import com.afc.companion.profile.ProfileState

enum class AlertAction { Watch, Dismiss }

/** Customer-visible alert text: headline, triggering player and matchup context, access label, optional commentary. */
data class AlertText(val headline: String, val context: String, val access: String, val commentary: String?)

/** What NOTIFIER renders for one alert. */
data class AlertView(val presentation: Presentation, val actions: List<AlertAction>, val text: AlertText, val speak: Boolean)

// AFC-STUB: P2-A03 implements NOTIFIER's presentation, alert text and voice gate behind these signatures.
object AlertPresenter {
    /** Null when the alert lacks its triggering player and matchup context. */
    fun text(alert: Alert): AlertText? = null

    fun view(alert: Alert, profile: ProfileState, voiceRouteVerified: Boolean = false): AlertView? = null
}

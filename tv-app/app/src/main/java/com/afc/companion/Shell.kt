package com.afc.companion

import com.afc.companion.net.ApiClient
import com.afc.companion.profile.ProfileState

/** SHELL: Link, Profile/Settings and Panel only; no social or messaging surfaces (AFC-PR-057). */
enum class Destination(val label: String) { Link("Connect"), ProfileSettings("My setup"), Panel("My lineup") }

/** Starts and stops the AlertService long poll. */
interface MonitorControl {
    fun start()
    fun stop()
}

class Shell {
    fun destinations(): Set<String> = Destination.entries.mapTo(LinkedHashSet()) { it.label }

    fun start(hasSession: Boolean): Destination = if (hasSession) Destination.ProfileSettings else Destination.Link

    /** Null means "Backend not configured": an empty or unusable AFC_API_BASE_URL. */
    fun client(baseUrl: String, sessionToken: () -> String?): ApiClient? =
        baseUrl.takeIf { it.isNotBlank() }?.let { runCatching { ApiClient(it, sessionToken) }.getOrNull() }

    /**
     * AFC-PR-009: monitoring runs only with a session and at least one enabled alert type; the backend
     * applies the schedule (game-day periods, quiet hours). An unread profile changes nothing.
     */
    fun syncMonitoring(hasSession: Boolean, profile: ProfileState?, control: MonitorControl) {
        when {
            !hasSession -> control.stop()
            profile == null -> Unit
            profile.alertTypes.isNotEmpty() -> control.start()
            else -> control.stop()
        }
    }
}

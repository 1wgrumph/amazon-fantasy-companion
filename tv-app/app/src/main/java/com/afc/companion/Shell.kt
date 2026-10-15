package com.afc.companion

import com.afc.companion.net.ApiClient

/** SHELL: Link, Profile/Settings and Panel only; no social or messaging surfaces (AFC-PR-057). */
enum class Destination(val label: String) { Link("Link"), ProfileSettings("Profile/Settings"), Panel("Panel") }

class Shell {
    fun destinations(): Set<String> = Destination.entries.mapTo(LinkedHashSet()) { it.label }

    fun start(hasSession: Boolean): Destination = if (hasSession) Destination.ProfileSettings else Destination.Link

    /** Null means "Backend not configured": an empty or unusable AFC_API_BASE_URL. */
    fun client(baseUrl: String, sessionToken: () -> String?): ApiClient? =
        baseUrl.takeIf { it.isNotBlank() }?.let { runCatching { ApiClient(it, sessionToken) }.getOrNull() }
}

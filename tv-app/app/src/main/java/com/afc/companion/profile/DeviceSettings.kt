package com.afc.companion.profile

import android.content.Context
import android.content.SharedPreferences
import androidx.core.content.edit

/** Settings kept on this TV only, in app-private storage; never sent to the server profile (owner, 2026-10-16). */
class DeviceSettings(private val prefs: SharedPreferences) {
    constructor(context: Context) : this(context.getSharedPreferences("afc_device", Context.MODE_PRIVATE))

    /** A new alert re-shows a hidden fullScreen panel; on unless the customer turns it off. */
    var showPanelOnNewAlert: Boolean
        get() = prefs.getBoolean(SHOW_PANEL_ON_NEW_ALERT, true)
        set(value) = prefs.edit { putBoolean(SHOW_PANEL_ON_NEW_ALERT, value) }

    companion object {
        private const val SHOW_PANEL_ON_NEW_ALERT = "showPanelOnNewAlert"

        /** Shown under the toggle: the setting stays on this TV and needs no Save. */
        const val SCOPE_NOTE = "Applies immediately on this TV."

        fun label(showPanelOnNewAlert: Boolean): String =
            "Open lineup on alerts: ${if (showPanelOnNewAlert) "On" else "Off"}"
    }
}

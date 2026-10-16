package com.afc.companion.net

import android.content.Context
import androidx.core.content.edit

/** The only credential the TV holds: its device session token, in app-private storage (AFC-PR-055). Never logged. */
class SessionStore(context: Context) {
    private val prefs = context.getSharedPreferences("afc_session", Context.MODE_PRIVATE)

    fun token(): String? = prefs.getString(KEY, null)

    fun save(token: String) = prefs.edit { putString(KEY, token) }

    fun clear() = prefs.edit { remove(KEY) }

    private companion object { const val KEY = "sessionToken" }
}

package com.afc.companion.watch

import android.app.Activity
import android.app.AlertDialog
import android.os.Bundle
import com.afc.companion.BuildConfig
import com.afc.companion.Shell
import com.afc.companion.alerts.AlertInbox
import com.afc.companion.alerts.AlertNotifier
import com.afc.companion.net.SessionStore
import com.afc.companion.panel.panelModeFor
import com.afc.companion.profile.ProfileStore
import kotlin.coroutines.resume
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import kotlinx.coroutines.suspendCancellableCoroutine

/** The notification's Watch target: one [WatchLauncher.watchAlert] attempt for the alert, then finish. */
class WatchActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val eventId = intent.getStringExtra(AlertNotifier.EXTRA_EVENT_ID)
        val client = Shell().client(BuildConfig.AFC_API_BASE_URL, SessionStore(this)::token)
        // A recreated activity never starts a second attempt (AFC-PR-031).
        if (savedInstanceState != null || eventId == null || client == null) {
            finish()
            return
        }
        val route = AlertInbox.find(intent.getStringExtra(AlertNotifier.EXTRA_ALERT_ID))?.route
        // Not tied to this noHistory activity: the outcome report must outlive it once the provider starts.
        CoroutineScope(SupervisorJob() + Dispatchers.Main).launch {
            val switchingConfirm = ProfileStore(client).load()?.switchingConfirm ?: true
            WatchLauncher(this@WatchActivity)
                .watchAlert(eventId, route, client, switchingConfirm, panelModeFor(null), ::confirmSwitch)
            finish()
        }
    }

    private suspend fun confirmSwitch(): Boolean = suspendCancellableCoroutine { answer ->
        AlertDialog.Builder(this)
            .setMessage("Switch to the provider app to watch?")
            .setPositiveButton("Watch") { _, _ -> if (answer.isActive) answer.resume(true) }
            .setNegativeButton("Cancel") { _, _ -> if (answer.isActive) answer.resume(false) }
            .setOnCancelListener { if (answer.isActive) answer.resume(false) }
            .show()
    }
}

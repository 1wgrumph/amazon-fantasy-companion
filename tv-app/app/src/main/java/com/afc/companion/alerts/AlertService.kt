package com.afc.companion.alerts

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import com.afc.companion.BuildConfig
import com.afc.companion.net.ApiClient
import com.afc.companion.net.SessionStore
import com.afc.companion.profile.Presentation
import com.afc.companion.profile.ProfileStore
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

/**
 * ALERTSVC: the foreground long-poll loop over [AlertFeed]. Delivered alerts go to [AlertNotifier]
 * when the customer's presentation is heads-up; panel-only posts nothing (the panel renders the
 * alert). Voice is never spoken here: no voice route is verified (P2-X11 absent), so
 * voiceRouteVerified stays false and [AlertPresenter] keeps speak off. The session token is read
 * only by [ApiClient] and never logged.
 */
class AlertService : Service() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var polling: Job? = null
    private var feed: AlertFeed? = null
    private var profiles: ProfileStore? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_DISMISS) {
            (intent.getStringExtra(AlertNotifier.EXTRA_ALERT_ID))?.let { id ->
                feed?.dismiss(id)
                AlertNotifier(this).cancel(id)
            }
            if (polling?.isActive != true) stopSelf(startId)
            return START_NOT_STICKY
        }
        val client = client() ?: run {
            stopSelf(startId)
            return START_NOT_STICKY
        }
        if (polling?.isActive == true) return START_STICKY
        startForeground()
        val activeFeed = AlertFeed(client).also { feed = it }
        val activeProfiles = ProfileStore(client).also { profiles = it }
        val notifier = AlertNotifier(this)
        polling = scope.launch {
            while (isActive) {
                val startedAt = System.currentTimeMillis()
                val delivered = activeFeed.poll()
                if (delivered.isNotEmpty()) {
                    val profile = activeProfiles.load()
                    if (profile?.presentation != Presentation.PanelOnly) delivered.forEach(notifier::show)
                } else if (System.currentTimeMillis() - startedAt < FAST_FAILURE_MS) {
                    delay(ERROR_BACKOFF_MS) // a fast return is an error, not a long poll expiring
                }
            }
        }
        return START_STICKY
    }

    override fun onDestroy() {
        scope.cancel()
        super.onDestroy()
    }

    private fun client(): ApiClient? {
        if (BuildConfig.AFC_API_BASE_URL.isBlank()) return null
        val sessions = SessionStore(this)
        return runCatching { ApiClient(BuildConfig.AFC_API_BASE_URL, sessions::token) }.getOrNull()
    }

    private fun startForeground() {
        val manager = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= 26 && manager.getNotificationChannel(STATUS_CHANNEL_ID) == null) {
            manager.createNotificationChannel(
                NotificationChannel(STATUS_CHANNEL_ID, "Alert monitoring", NotificationManager.IMPORTANCE_LOW)
                    .apply { description = "Shown while game alerts are being monitored" },
            )
        }
        val notification = NotificationCompat.Builder(this, STATUS_CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("Watching for game alerts")
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
        ServiceCompat.startForeground(
            this, STATUS_NOTIFICATION_ID, notification,
            if (Build.VERSION.SDK_INT >= 29) ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC else 0,
        )
    }

    companion object {
        const val ACTION_DISMISS = "com.afc.companion.alerts.DISMISS"
        private const val STATUS_CHANNEL_ID = "afc-alert-monitoring"
        private const val STATUS_NOTIFICATION_ID = 1
        private const val FAST_FAILURE_MS = 1_000L
        private const val ERROR_BACKOFF_MS = 5_000L
    }
}

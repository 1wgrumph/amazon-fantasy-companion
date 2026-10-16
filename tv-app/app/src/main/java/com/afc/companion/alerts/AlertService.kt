package com.afc.companion.alerts

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import com.afc.companion.BuildConfig
import com.afc.companion.MonitorControl
import com.afc.companion.net.Alert
import com.afc.companion.net.ApiClient
import com.afc.companion.net.SessionStore
import com.afc.companion.profile.Presentation
import com.afc.companion.profile.ProfileState
import com.afc.companion.profile.ProfileStore
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
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
                AlertInbox.publish()
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
        AlertInbox.attach(activeFeed)
        val activeProfiles = ProfileStore(client).also { profiles = it }
        val notifier = AlertNotifier(this)
        val gate = PresentationGate()
        polling = scope.launch {
            while (isActive) {
                val startedAt = System.currentTimeMillis()
                val delivered = activeFeed.poll()
                if (delivered.isNotEmpty()) AlertInbox.publish()
                if (delivered.isNotEmpty() || gate.hasPending()) {
                    gate.drain(delivered, activeProfiles.load()).forEach(notifier::show)
                }
                if (delivered.isEmpty() && System.currentTimeMillis() - startedAt < FAST_FAILURE_MS) {
                    delay(ERROR_BACKOFF_MS) // a fast return is an error, not a long poll expiring
                }
            }
        }
        return START_STICKY
    }

    override fun onDestroy() {
        scope.cancel()
        AlertInbox.attach(null)
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

/** Starts and stops [AlertService] from the shell (DES-AFC-P2-TV). */
class AlertServiceControl(private val context: Context) : MonitorControl {
    override fun start() = ContextCompat.startForegroundService(context, Intent(context, AlertService::class.java))
    override fun stop() {
        context.stopService(Intent(context, AlertService::class.java))
    }
}

/**
 * In-process hand-off from [AlertService] to the panel. P2-X02 FAILS (Fire OS 8.1 never shows a heads-up
 * notification), so the panel is the only customer-reachable alert surface: it shows every retained
 * alert whatever the presentation setting, and its Dismiss acknowledges locally like the notification's.
 */
object AlertInbox {
    private val state = MutableStateFlow<List<Alert>>(emptyList())
    @Volatile private var feed: AlertFeed? = null

    val alerts: StateFlow<List<Alert>> = state.asStateFlow()

    /** Null when monitoring stops: the panel then shows no alerts. */
    fun attach(feed: AlertFeed?) {
        this.feed = feed
        publish()
    }

    fun publish() {
        state.value = feed?.queue.orEmpty()
    }

    fun find(id: String?): Alert? = alerts.value.firstOrNull { it.envelope.id == id }

    fun dismiss(id: String) {
        feed?.dismiss(id)
        publish()
    }
}

/**
 * Fail-closed presentation gate: a null profile (timeout, 500, bad body) never means heads-up.
 * The last validated presentation decides; with none validated yet, alerts are deferred (bounded,
 * newest revision per id) until a profile loads, then flushed only if it is heads-up. Panel-only
 * drops the notifier backlog because [AlertFeed] already retains those alerts for the panel.
 */
internal class PresentationGate {
    private var lastValidated: Presentation? = null
    private val pending = LinkedHashMap<String, Alert>()

    @Synchronized fun hasPending(): Boolean = pending.isNotEmpty()

    @Synchronized fun drain(delivered: List<Alert>, profile: ProfileState?): List<Alert> {
        if (profile != null) lastValidated = profile.presentation
        return when (profile?.presentation ?: lastValidated) {
            Presentation.HeadsUp -> {
                val ready = LinkedHashMap<String, Alert>()
                for (alert in pending.values + delivered) {
                    val held = ready[alert.envelope.id]
                    if (held == null || alert.envelope.revision >= held.envelope.revision) ready[alert.envelope.id] = alert
                }
                pending.clear()
                ready.values.toList()
            }
            Presentation.PanelOnly -> {
                pending.clear()
                emptyList()
            }
            null -> {
                for (alert in delivered) {
                    val held = pending[alert.envelope.id]
                    if (held == null || alert.envelope.revision >= held.envelope.revision) {
                        pending.remove(alert.envelope.id)
                        pending[alert.envelope.id] = alert
                    }
                }
                while (pending.size > AlertFeed.QUEUE_MAX) pending.remove(pending.keys.first())
                emptyList()
            }
        }
    }
}

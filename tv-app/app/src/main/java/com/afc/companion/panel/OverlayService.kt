package com.afc.companion.panel

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.graphics.PixelFormat
import android.net.Uri
import android.os.Build
import android.os.IBinder
import android.provider.Settings
import android.view.Gravity
import android.view.WindowManager
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.dp
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import com.afc.companion.BuildConfig
import com.afc.companion.Shell
import com.afc.companion.alerts.AlertInbox
import com.afc.companion.net.SessionStore
import com.afc.companion.profile.ProfileState
import com.afc.companion.profile.ProfileStore
import com.afc.companion.ui.theme.TvPalette
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * Overlay host: the compact side panel over the playing game and the top-right alert card, both
 * nonfocusable windows, so the remote keeps driving the game. Panel data comes from the shared
 * [runPanelUpdates] owner and alerts from [AlertInbox]; this service adds no data path of its own.
 */
class OverlayService : Service() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private val windows by lazy { getSystemService(WindowManager::class.java) }
    private val client by lazy { Shell().client(BuildConfig.AFC_API_BASE_URL, SessionStore(this)::token) }
    private var controller = overlay(null)
    private var cardSnapshot: PanelSnapshot? = null
    private val cards by lazy { AlertCardOverlay(this, windows, { cardSnapshot }, ::onCard) }
    private var panelWindow: OverlayView? = null
    private var cardBox: Box? = null
    private var updates: Job? = null
    private var tick by mutableIntStateOf(0)
    private var fetchAttempted by mutableStateOf(false)

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        cards.onAlerts(AlertInbox.alerts.value)
        scope.launch {
            AlertInbox.alerts.collect { alerts ->
                controller.panel.onAlerts(panelAlerts(alerts))
                if (cards.active && alerts.isNotEmpty()) cardSnapshot = client?.let { alertCardPanel(it) }
                cards.onAlerts(alerts)
                tick++
            }
        }
        scope.launch {
            while (true) {
                delay(CARD_TICK_MS)
                cards.tick()
            }
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground()
        when (intent?.action) {
            ACTION_TOGGLE -> scope.launch {
                // Each show re-reads the profile, so a team/league changed in Settings is picked up.
                if (panelWindow == null) controller = overlay(client?.let { ProfileStore(it).load() })
                controller.toggle()
                stopIfIdle()
            }
            ACTION_ALERTS -> { cards.start(); stopIfIdle() }
            ACTION_STOP_ALERTS -> { cards.stop(); cardSnapshot = null; stopIfIdle() }
            else -> stopIfIdle()
        }
        return START_NOT_STICKY
    }

    override fun onDestroy() {
        controller.hide()
        cards.stop()
        scope.cancel()
        super.onDestroy()
    }

    private fun stopIfIdle() {
        if (panelWindow == null && !cards.active) stopSelf()
    }

    private fun overlay(profile: ProfileState?): OverlayController {
        val teamLeague = panelTeamLeague(profile)
        val panel = PanelController(listOfNotNull(teamLeague), teamLeague, false)
        panel.onAlerts(panelAlerts(AlertInbox.alerts.value))
        return OverlayController(panel, { Settings.canDrawOverlays(this) }, ::requestPermission, ::addPanel, ::removePanel)
    }

    /** Opens this app's "Display over other apps" switch; Companion shows the manual steps if Fire OS has no such screen. */
    private fun requestPermission() {
        val settings = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        runCatching { startActivity(settings) }
    }

    private fun addPanel() {
        val panel = controller.panel
        updates?.cancel()
        fetchAttempted = false
        updates = client?.let { api ->
            scope.launch {
                runPanelUpdates(api, panel) { fetched ->
                    if (fetched) fetchAttempted = true
                    tick++
                }
            }
        }
        if (panelWindow != null) return
        val window = OverlayView(this) {
            @Suppress("UNUSED_EXPRESSION") tick // reads tick so controller mutations recompose
            val density = LocalDensity.current
            // The shared renderer is sized for the full-screen panel; the overlay draws it smaller.
            CompositionLocalProvider(LocalDensity provides Density(density.density * PANEL_SCALE, density.fontScale)) {
                Box(
                    Modifier.fillMaxSize().clip(RoundedCornerShape(16.dp))
                        .background(Color(TvPalette.surfaceArgb).copy(alpha = 0.88f)).padding(4.dp),
                ) {
                    PanelContent(
                        alerts = controller.panel.panelAlerts.take(1),
                        armedWatch = null,
                        watchOutcome = null,
                        snapshot = controller.panel.snapshot,
                        teamLeague = controller.panel.teamLeague,
                        focused = null,
                        fetchAttempted = fetchAttempted,
                        nowMs = System.currentTimeMillis(),
                        compact = true,
                    )
                }
            }
        }
        if (runCatching { windows.addView(window.view, panelParams()) }.isSuccess) panelWindow = window else window.destroy()
    }

    private fun removePanel() {
        updates?.cancel()
        updates = null
        val window = panelWindow ?: return
        panelWindow = null
        runCatching { windows.removeView(window.view) }
        window.destroy()
    }

    /** A showing card reserves the top-right slot; the panel moves below it and back when it goes. */
    private fun onCard(box: Box?) {
        cardBox = box
        panelWindow?.let { window -> runCatching { windows.updateViewLayout(window.view, panelParams()) } }
    }

    private fun panelParams(): WindowManager.LayoutParams {
        val (width, height) = screenSize(windows)
        val box = cardBox?.let { OverlayGeometry.layoutWithAlertCard(width, height, it) } ?: OverlayGeometry.layout(width, height)
        return WindowManager.LayoutParams(
            box.width, box.height, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
            PixelFormat.TRANSLUCENT,
        ).apply {
            gravity = Gravity.TOP or Gravity.LEFT
            x = box.left
            y = box.top
        }
    }

    private fun startForeground() {
        val manager = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= 26 && manager.getNotificationChannel(CHANNEL_ID) == null) {
            manager.createNotificationChannel(NotificationChannel(CHANNEL_ID, "Game overlay", NotificationManager.IMPORTANCE_LOW))
        }
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("Fantasy overlay ready")
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
        ServiceCompat.startForeground(
            this, NOTIFICATION_ID, notification,
            if (Build.VERSION.SDK_INT >= 29) ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC else 0,
        )
    }

    companion object {
        const val ACTION_TOGGLE = "com.afc.companion.panel.TOGGLE_OVERLAY"
        const val ACTION_STOP_ALERTS = "com.afc.companion.panel.STOP_ALERT_CARDS"
        const val ACTION_ALERTS = "com.afc.companion.panel.START_ALERT_CARDS"
        private const val CHANNEL_ID = "afc-overlay"
        private const val NOTIFICATION_ID = 2
        private const val CARD_TICK_MS = 250L
        private const val PANEL_SCALE = 0.65f
    }
}

/** Starts the overlay host: [toggle] from Companion's "Show over game" button, [startAlerts] from monitoring. */
class OverlayServiceControl(private val context: Context) {
    fun toggle() {
        ContextCompat.startForegroundService(context, Intent(context, OverlayService::class.java).setAction(OverlayService.ACTION_TOGGLE))
    }

    fun stopAlerts() {
        context.startService(Intent(context, OverlayService::class.java).setAction(OverlayService.ACTION_STOP_ALERTS))
    }

    fun startAlerts() {
        ContextCompat.startForegroundService(context, Intent(context, OverlayService::class.java).setAction(OverlayService.ACTION_ALERTS))
    }
}

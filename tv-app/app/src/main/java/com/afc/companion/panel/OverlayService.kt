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
import android.view.KeyEvent
import android.view.WindowManager
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
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
import com.afc.companion.access.MenuHold
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
 * Overlay host over the playing game: the corner card (default), its held-≡ menu, the expanded side
 * panel, and the top-right alert card. The card and alert windows never take focus, so the remote
 * keeps driving the game; only the menu and expanded panel take it while open. Panel data comes from
 * the shared [runPanelUpdates] owner and alerts from [AlertInbox]; this service adds no data path of its own.
 */
class OverlayService : Service() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private val windows by lazy { getSystemService(WindowManager::class.java) }
    private val client by lazy { Shell().client(BuildConfig.AFC_API_BASE_URL, SessionStore(this)::token) }
    private var controller = overlay(null)
    private var cardSnapshot: PanelSnapshot? = null
    private val cards by lazy { AlertCardOverlay(this, windows, { cardSnapshot }, ::onCard) }
    private var cardWindow: OverlayView? = null
    private var menuWindow: OverlayView? = null
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
                if (controller.mode == OverlayMode.Off) controller = overlay(client?.let { ProfileStore(it).load() })
                controller.toggle()
                render()
                stopIfIdle()
            }
            ACTION_HOLD -> scope.launch {
                if (controller.mode == OverlayMode.Off) controller = overlay(client?.let { ProfileStore(it).load() })
                controller.hold()
                render()
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
        if (controller.mode == OverlayMode.Off && !cards.active) stopSelf()
    }

    private fun overlay(profile: ProfileState?): OverlayController {
        val panel = PanelController(overlayTeamLeagues(profile), panelTeamLeague(profile), false)
        panel.onAlerts(panelAlerts(AlertInbox.alerts.value))
        return OverlayController(panel, { Settings.canDrawOverlays(this) }, ::requestPermission, ::startUpdates, ::stopUpdates)
    }

    /** Opens this app's "Display over other apps" switch; Companion shows the manual steps if Fire OS has no such screen. */
    private fun requestPermission() {
        val settings = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        runCatching { startActivity(settings) }
    }

    private fun startUpdates() {
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
    }

    private fun stopUpdates() {
        updates?.cancel()
        updates = null
        render()
    }

    /** Matches the windows to [OverlayController.mode]: card in Card and Menu, menu in Menu, side panel in Expanded. */
    private fun render() {
        val mode = controller.mode
        cardWindow = sync(cardWindow, mode == OverlayMode.Card || mode == OverlayMode.Menu, ::cardParams, null) {
            @Suppress("UNUSED_EXPRESSION") tick // reads tick so controller mutations and the clock recompose
            val enabled = MenuHold.enabled(Settings.Secure.getString(contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES))
            CornerCardContent(controller.panel.snapshot, controller.panel.teamLeague, System.currentTimeMillis(), enabled)
        }
        menuWindow = sync(menuWindow, mode == OverlayMode.Menu, ::menuParams, ::onFocusedKey) {
            @Suppress("UNUSED_EXPRESSION") tick
            OverlayMenuContent(controller.menuFocus, controller.panel.teamLeague)
        }
        panelWindow = sync(panelWindow, mode == OverlayMode.Expanded, ::panelParams, ::onFocusedKey) {
            @Suppress("UNUSED_EXPRESSION") tick
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
    }

    /** Menu and panel keys go to the tested state machine; Back on either returns focus to the game. */
    private fun onFocusedKey(event: KeyEvent): Boolean {
        if (event.action != KeyEvent.ACTION_DOWN || !controller.onFocusedKey(event.keyCode)) return false
        tick++
        render()
        stopIfIdle()
        return true
    }

    /** Adds or removes one window so it exists exactly when [visible]; a failed add shows nothing. */
    private fun sync(
        window: OverlayView?,
        visible: Boolean,
        params: () -> WindowManager.LayoutParams,
        onKey: ((KeyEvent) -> Boolean)?,
        content: @Composable () -> Unit,
    ): OverlayView? {
        if (visible == (window != null)) return window
        if (window != null) {
            runCatching { windows.removeViewImmediate(window.view) }
            window.destroy()
            return null
        }
        val added = OverlayView(this, onKey, content)
        return if (runCatching { windows.addView(added.view, params()) }.isSuccess) added else null.also { added.destroy() }
    }

    /** A showing alert card keeps the corner; the card, menu and panel move below it and back when it goes. */
    private fun onCard(box: Box?) {
        if (cardBox == box) return
        cardBox = box
        // Reattach at the final rectangle: moving a live window animates through the card on older Android.
        for ((window, params) in listOf(cardWindow to ::cardParams, menuWindow to ::menuParams, panelWindow to ::panelParams)) {
            window ?: continue
            val moved = runCatching {
                windows.removeViewImmediate(window.view)
                windows.addView(window.view, params())
            }
            if (moved.isFailure) {
                controller.hide() // a gone display or revoked permission: drop the whole surface
                stopIfIdle()
                return
            }
        }
    }

    private fun cardParams(): WindowManager.LayoutParams {
        val (width, height) = screenSize(windows)
        return windowParams(OverlayGeometry.cornerCard(width, height, cardBox), overlayWindowFlags(focusable = false))
    }

    private fun menuParams(): WindowManager.LayoutParams {
        val (width, height) = screenSize(windows)
        val card = OverlayGeometry.cornerCard(width, height, cardBox)
        return windowParams(OverlayGeometry.menu(width, height, card), overlayWindowFlags(focusable = true))
    }

    private fun panelParams(): WindowManager.LayoutParams {
        val (width, height) = screenSize(windows)
        val box = cardBox?.let { OverlayGeometry.layoutWithAlertCard(width, height, it) } ?: OverlayGeometry.layout(width, height)
        return windowParams(box, overlayWindowFlags(focusable = true))
    }

    private fun windowParams(box: Box, flags: Int) = WindowManager.LayoutParams(
        box.width, box.height, WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY, flags, PixelFormat.TRANSLUCENT,
    ).apply {
        gravity = Gravity.TOP or Gravity.LEFT
        x = box.left
        y = box.top
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
        const val ACTION_HOLD = "com.afc.companion.panel.HOLD_OVERLAY"
        private const val CHANNEL_ID = "afc-overlay"
        private const val NOTIFICATION_ID = 2
        private const val CARD_TICK_MS = 250L
        private const val PANEL_SCALE = 0.65f
    }
}

/**
 * Starts the overlay host: [toggle] from Companion's "Show over game" button, [hold] from the held-≡
 * accessibility service, [startAlerts] from monitoring.
 */
class OverlayServiceControl(private val context: Context) {
    fun toggle() {
        ContextCompat.startForegroundService(context, Intent(context, OverlayService::class.java).setAction(OverlayService.ACTION_TOGGLE))
    }

    fun hold() {
        ContextCompat.startForegroundService(context, Intent(context, OverlayService::class.java).setAction(OverlayService.ACTION_HOLD))
    }

    fun stopAlerts() {
        context.startService(Intent(context, OverlayService::class.java).setAction(OverlayService.ACTION_STOP_ALERTS))
    }

    fun startAlerts() {
        ContextCompat.startForegroundService(context, Intent(context, OverlayService::class.java).setAction(OverlayService.ACTION_ALERTS))
    }
}

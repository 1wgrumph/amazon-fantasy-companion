package com.afc.companion

import android.app.Activity
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.core.content.edit
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text
import com.afc.companion.alerts.AlertServiceControl
import com.afc.companion.alerts.alertFeedMemory
import com.afc.companion.link.LinkView
import com.afc.companion.net.ApiClient
import com.afc.companion.net.SessionStore
import com.afc.companion.panel.LineupPanel
import com.afc.companion.panel.OverlayServiceControl
import com.afc.companion.panel.panelModeFor
import com.afc.companion.profile.ProfileSettingsScreen
import com.afc.companion.profile.ProfileStore
import com.afc.companion.ui.theme.AfcTheme
import com.afc.companion.ui.theme.LocalTvSafeZoneApplied
import com.afc.companion.ui.theme.afcBackground
import com.afc.companion.ui.theme.TvButton as Button
import com.afc.companion.ui.theme.tvSafeZonePadding

/** SHELL: single activity hosting Link, Profile/Settings and Panel. Only P2-A05 edits this file after P2-A01. */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val sessions = SessionStore(this)
        val shell = Shell()
        val client = shell.client(BuildConfig.AFC_API_BASE_URL, sessions::token)
        setContent {
            AfcTheme {
                Box(Modifier.fillMaxSize().afcBackground()) {
                    if (client == null) NotConfigured() else AppShell(shell, client, sessions)
                }
            }
        }
    }
}

@Composable
private fun NotConfigured() {
    Column(Modifier.tvSafeZonePadding().padding(8.dp), verticalArrangement = Arrangement.spacedBy(24.dp)) {
        Text("Backend not configured", style = MaterialTheme.typography.headlineMedium)
        Text("Build with -PafcApiBaseUrl=<API URL> to connect this TV.", style = MaterialTheme.typography.bodyLarge)
    }
}

/**
 * Shows the card or expanded lineup over the game, then returns to the app that was playing. Without the
 * overlay permission it stays here: Android's switch opens, and the manual steps show in case
 * Fire OS has no such screen.
 */
@Composable
private fun ShowOverGame(canExpand: Boolean) {
    val context = LocalContext.current
    val overlay = remember(context) { OverlayServiceControl(context) }
    var needsPermission by remember { mutableStateOf(false) }
    Button(onClick = {
        overlay.toggle()
        needsPermission = !Settings.canDrawOverlays(context)
        if (!needsPermission) (context as? Activity)?.moveTaskToBack(true)
    }) { Text("Show over game") }
    if (canExpand) {
        Button(onClick = {
            overlay.expand()
            needsPermission = !Settings.canDrawOverlays(context)
            if (!needsPermission) (context as? Activity)?.moveTaskToBack(true)
        }) { Text("Expand over game") }
    }
    if (needsPermission) {
        Text(
            "Allow Companion to display over other apps, then try again.\n" +
                "Settings > Applications > Special app access > Display over other apps.",
            modifier = Modifier.widthIn(max = 280.dp),
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}

@Composable
private fun AppShell(shell: Shell, client: ApiClient, sessions: SessionStore) {
    var destination by remember { mutableStateOf(shell.start(sessions.token() != null)) }
    val context = LocalContext.current
    val monitor = AlertServiceControl(context)
    // Every navigation re-reads the enablement, so leaving Profile/Settings applies a changed alert-type choice.
    LaunchedEffect(destination) {
        val hasSession = sessions.token() != null
        shell.syncMonitoring(hasSession, if (hasSession) ProfileStore(client).load() else null, monitor)
    }
    Row(Modifier.fillMaxSize().tvSafeZonePadding()) {
        Column(Modifier.padding(horizontal = 12.dp, vertical = 8.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
            Destination.entries.forEach { target ->
                Button(onClick = { destination = target }) { Text(target.label) }
            }
            ShowOverGame(canExpand = destination == Destination.Panel)
        }
        Box(Modifier.weight(1f).fillMaxSize()) {
            CompositionLocalProvider(LocalTvSafeZoneApplied provides true) {
                when (destination) {
                    Destination.Link -> LinkView(client, onLinked = { token ->
                        sessions.save(token)
                        alertFeedMemory(context).edit { clear() }
                        destination = Destination.ProfileSettings
                    })
                    Destination.ProfileSettings -> ProfileSettingsScreen(client)
                    // P2-X04 FAILS (spikes/sp4-panel-video/VERDICT.md): no modeB route on Fire OS 8.1,
                    // so the panel is fullScreen with no stand-in video.
                    Destination.Panel -> LineupPanel(client, panelModeFor(null))
                }
            }
        }
    }
}

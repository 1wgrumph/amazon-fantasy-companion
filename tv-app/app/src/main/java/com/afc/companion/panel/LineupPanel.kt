package com.afc.companion.panel

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text
import com.afc.companion.net.ApiClient

/** PanelMode fixed by the P2-X04 verdict: modeB side-by-side route or fullScreen in this app. */
enum class PanelMode { ModeB, FullScreen }

// AFC-STUB: P2-A05 implements PANEL (rows, totals, basis, freshness) behind this final signature.
@Composable
fun LineupPanel(client: ApiClient, mode: PanelMode, modifier: Modifier = Modifier) {
    Column(modifier.padding(48.dp), verticalArrangement = Arrangement.spacedBy(24.dp)) {
        Text("Panel", style = MaterialTheme.typography.headlineMedium)
        Text("The lineup panel is not available in this build.", style = MaterialTheme.typography.bodyLarge)
    }
}

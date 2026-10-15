package com.afc.companion.profile

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text
import com.afc.companion.net.ApiClient

// AFC-STUB: P2-A02 implements PROFILE (selections and every control) behind this final signature.
@Composable
fun ProfileSettingsScreen(client: ApiClient, modifier: Modifier = Modifier) {
    Column(modifier.padding(48.dp), verticalArrangement = Arrangement.spacedBy(24.dp)) {
        Text("Profile/Settings", style = MaterialTheme.typography.headlineMedium)
        Text("Profile and settings are not available in this build.", style = MaterialTheme.typography.bodyLarge)
    }
}

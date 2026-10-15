package com.afc.companion.profile

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.tv.material3.Button
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text
import com.afc.companion.net.ApiClient
import com.afc.companion.net.ScoringPreset
import kotlinx.coroutines.launch

/**
 * Profile/Settings: loads the persisted profile, offers every control whose
 * platform route is supported, and saves through ProfileStore. A control
 * hidden by an unsupported route shows its stated limit instead.
 */
@Composable
fun ProfileSettingsScreen(client: ApiClient, modifier: Modifier = Modifier) {
    val store = remember(client) { ProfileStore(client) }
    var state by remember { mutableStateOf<ProfileState?>(null) }
    var message by remember { mutableStateOf("Loading profile…") }
    val scope = rememberCoroutineScope()
    // No verified voice route exists in this build, so Voice stays hidden with its stated limit (AFC-PR-022).
    val controls = profileControls(detectionSupported = true, voiceRouteVerified = false)

    LaunchedEffect(store) {
        state = store.load()
        message = if (state == null) "Profile is unavailable. Check the connection and try again." else "Profile loaded."
    }

    Column(
        modifier.padding(48.dp).verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Text("Profile/Settings", style = MaterialTheme.typography.headlineMedium)
        Text(message, style = MaterialTheme.typography.bodyLarge)
        val current = state ?: return@Column
        for (control in ProfileControl.entries) {
            val limit = controls.limits[control]
            if (limit != null) {
                Text("$control: $limit", style = MaterialTheme.typography.bodyLarge)
                continue
            }
            when (control) {
                ProfileControl.ScoringPreset -> Button(onClick = {
                    state = current.copy(scoringPreset = if (current.scoringPreset == ScoringPreset.Ppr) ScoringPreset.HalfPpr else ScoringPreset.Ppr)
                }) { Text("Scoring preset: ${current.scoringPreset.wire} (select to switch)") }
                ProfileControl.Presentation -> Button(onClick = {
                    state = current.copy(presentation = Presentation.entries[(current.presentation.ordinal + 1) % Presentation.entries.size])
                }) { Text("Presentation: ${current.presentation}") }
                ProfileControl.Excitement -> Button(onClick = {
                    state = current.copy(excitement = Excitement.entries[(current.excitement.ordinal + 1) % Excitement.entries.size])
                }) { Text("Excitement: ${current.excitement}") }
                ProfileControl.Frequency -> Button(onClick = {
                    state = current.copy(minGapSeconds = listOf(0, 60, 120, 300, 600).let { it[(it.indexOf(current.minGapSeconds) + 1).mod(it.size)] })
                }) { Text("Alert frequency: at most one alert per ${current.minGapSeconds} s per game") }
                ProfileControl.SpoilerDelay -> Button(onClick = {
                    state = current.copy(spoilerDelaySeconds = listOf(0, 15, 30, 45, 60, 120).let { it[(it.indexOf(current.spoilerDelaySeconds) + 1).mod(it.size)] })
                }) { Text("Spoiler delay: ${current.spoilerDelaySeconds} s") }
                ProfileControl.SwitchingConfirmation -> Button(onClick = {
                    state = current.copy(switchingConfirm = !current.switchingConfirm)
                }) { Text("Confirm before switching: ${onOff(current.switchingConfirm)}") }
                ProfileControl.PanelVisibility -> Button(onClick = {
                    state = current.copy(panel = current.panel.copy(visible = !current.panel.visible))
                }) { Text("Panel visible: ${onOff(current.panel.visible)}") }
                ProfileControl.DetectionOptIn -> Button(onClick = {
                    state = current.copy(detectionOptIn = !current.detectionOptIn)
                }) { Text("Installed-app detection: ${onOff(current.detectionOptIn)}") }
                ProfileControl.Voice -> Button(onClick = {
                    state = current.copy(voiceEnabled = !current.voiceEnabled)
                }) { Text("Voice alerts: ${onOff(current.voiceEnabled)}") }
                ProfileControl.GameDay -> Button(onClick = {
                    state = current.copy(gameDay = current.gameDay.copy(enabled = !current.gameDay.enabled))
                }) { Text("Game-day mode: ${onOff(current.gameDay.enabled)} (${current.gameDay.periods.size} periods)") }
                ProfileControl.Selections -> Text(
                    "Selections: ${current.selections.leagues.size} leagues, ${current.selections.teams.size} teams, " +
                        "${current.selections.players.size} players, ${current.selections.favoriteTeams.size} favorite teams",
                    style = MaterialTheme.typography.bodyLarge,
                )
                ProfileControl.TeamLeague -> Text(
                    "Team/league: ${current.teamLeague?.let { "${it.team} in ${it.league}" } ?: "none selected"}",
                    style = MaterialTheme.typography.bodyLarge,
                )
                ProfileControl.AlertTypes -> Text("Alert types: ${current.alertTypes.joinToString().ifBlank { "none" }}", style = MaterialTheme.typography.bodyLarge)
                ProfileControl.QuietHours -> Text("Quiet hours: ${current.quietHours.size} windows", style = MaterialTheme.typography.bodyLarge)
                ProfileControl.ProviderPreference -> Text(
                    "Providers: ${current.providerPref.order.joinToString().ifBlank { "no preference" }}; " +
                        "market ${current.providerPref.localMarket ?: "unset"}; ${current.providerPref.appOverrides.size} overrides",
                    style = MaterialTheme.typography.bodyLarge,
                )
            }
        }
        Button(onClick = {
            scope.launch {
                val saved = store.save(current)
                state = saved ?: current
                message = if (saved == null) "Save failed; the profile changed elsewhere or is unavailable." else "Profile saved."
            }
        }) { Text("Save profile") }
    }
}

private fun onOff(value: Boolean): String = if (value) "on" else "off"

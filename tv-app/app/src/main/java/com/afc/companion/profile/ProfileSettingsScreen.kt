package com.afc.companion.profile

import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.FocusDirection
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.key
import androidx.compose.ui.input.key.onPreInterceptKeyBeforeSoftKeyboard
import androidx.compose.ui.input.key.type
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.semantics.onClick
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.tv.material3.Button
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text
import com.afc.companion.BuildConfig
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
    val stateHolder = remember { mutableStateOf<ProfileState?>(null) }
    var state by stateHolder
    var message by remember { mutableStateOf("Loading profile…") }
    val scope = rememberCoroutineScope()
    // No verified voice route exists in this build, so Voice stays hidden with its stated limit (AFC-PR-022).
    // X07_VERDICT_PENDING: no verified installed-app detection route exists yet, so detection
    // stays hidden with its stated limit until P2-X07 verifies one (DEVICE_INSTALL_PENDING).
    val controls = profileControls(detectionSupported = false, voiceRouteVerified = false)

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
        DeviceSettingsControls()
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
                ProfileControl.GameDay -> {
                    Button(onClick = {
                        state = current.copy(gameDay = current.gameDay.copy(enabled = !current.gameDay.enabled))
                    }) { Text("Game-day mode: ${onOff(current.gameDay.enabled)} (${current.gameDay.periods.size} periods)") }
                    GameDayPeriodsEditor(current, stateHolder)
                }
                ProfileControl.Selections -> SelectionsEditor(current, stateHolder)
                ProfileControl.TeamLeague -> {
                    Text(
                        "Team/league: ${current.teamLeague?.let { "${it.team} in ${it.league}" } ?: "none selected"}",
                        style = MaterialTheme.typography.bodyLarge,
                    )
                    TeamLeagueEditor(current, stateHolder)
                }
                ProfileControl.AlertTypes -> {
                    Text("Alert types: ${current.alertTypes.joinToString().ifBlank { "none" }}", style = MaterialTheme.typography.bodyLarge)
                    AlertTypesEditor(current, stateHolder)
                }
                ProfileControl.QuietHours -> QuietHoursEditor(current, stateHolder)
                ProfileControl.ProviderPreference -> {
                    Text(
                        "Providers: ${current.providerPref.order.joinToString().ifBlank { "no preference" }}; " +
                            "market ${current.providerPref.localMarket ?: "unset"}; ${current.providerPref.appOverrides.size} overrides",
                        style = MaterialTheme.typography.bodyLarge,
                    )
                    ProviderPreferenceEditor(current, stateHolder)
                }
            }
        }
        SportTogglesEditor(current, stateHolder)
        Button(onClick = {
            scope.launch {
                var saved = store.save(current)
                var submitted: ProfileState = current
                // A draft edited while a save is in flight is re-saved, never overwritten by the older response.
                while (saved != null && state != null && state != submitted) {
                    submitted = state!!
                    saved = store.save(submitted)
                }
                message = when {
                    saved == null -> "Save failed; the profile changed elsewhere or is unavailable."
                    state == submitted -> {
                        state = saved
                        "Profile saved."
                    }
                    else -> "Profile saved. Edits made since then are not saved yet."
                }
            }
        }) { Text("Save profile") }
    }
}

@Composable
private fun SportTogglesEditor(current: ProfileState, state: MutableState<ProfileState?>) {
    for ((sport, label) in sportToggles(current, nbaEnabled = BuildConfig.AFC_ENABLE_NBA)) {
        Button(onClick = { state.value = current.toggledSport(sport) }) { Text(label) }
    }
}

/** Stored on this TV and applied at once, so it is offered even when the server profile is unavailable. */
@Composable
private fun DeviceSettingsControls() {
    val context = LocalContext.current
    val settings = remember { DeviceSettings(context) }
    var showPanelOnNewAlert by remember { mutableStateOf(settings.showPanelOnNewAlert) }
    Button(onClick = {
        showPanelOnNewAlert = !showPanelOnNewAlert
        settings.showPanelOnNewAlert = showPanelOnNewAlert
    }) { Text(DeviceSettings.label(showPanelOnNewAlert)) }
}

private fun onOff(value: Boolean): String = if (value) "on" else "off"

// Select edits a field; otherwise vertical D-pad input belongs to form navigation.
@OptIn(ExperimentalComposeUiApi::class)
@Composable
private fun ProfileTextField(value: String, onValueChange: (String) -> Unit) {
    val focusManager = LocalFocusManager.current
    val focusRequester = remember { FocusRequester() }
    val keyboard = LocalSoftwareKeyboardController.current
    var editing by remember { mutableStateOf(false) }
    var focused by remember { mutableStateOf(false) }
    LaunchedEffect(editing) { if (editing) keyboard?.show() }
    BasicTextField(
        value = value,
        onValueChange = onValueChange,
        readOnly = !editing,
        modifier = Modifier.focusRequester(focusRequester)
            .semantics { onClick { focusRequester.requestFocus(); editing = true; true } }
            .onFocusChanged {
                focused = it.isFocused
                if (!it.isFocused) editing = false
            }
            .border(2.dp, if (focused) MaterialTheme.colorScheme.onSurface else Color.Transparent)
            .onPreInterceptKeyBeforeSoftKeyboard { event ->
                if (event.type != KeyEventType.KeyDown) {
                    false
                } else if (editing) {
                    if (event.key == Key.Back) {
                        editing = false
                        keyboard?.hide()
                        true
                    } else false
                } else when (event.key) {
                    Key.DirectionCenter, Key.Enter -> {
                        editing = true
                        true
                    }
                    Key.DirectionDown -> focusManager.moveFocus(FocusDirection.Down)
                    Key.DirectionUp -> focusManager.moveFocus(FocusDirection.Up)
                    else -> false
                }
        },
        textStyle = TextStyle(color = MaterialTheme.colorScheme.onSurface),
        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Next),
        keyboardActions = KeyboardActions(
            onNext = {
                editing = false
                keyboard?.hide()
                focusManager.moveFocus(FocusDirection.Next)
            },
            onDone = { editing = false; defaultKeyboardAction(ImeAction.Done) },
        ),
    )
}

private fun minuteOfDay(minute: Int): String = "${(minute / 60).toString().padStart(2, '0')}:${(minute % 60).toString().padStart(2, '0')}"

/** One remote-editable name list: type a name and add it, or remove an entry. */
@Composable
private fun NameListEditor(label: String, values: List<String>, onToggle: (String) -> Unit) {
    var draft by remember(label) { mutableStateOf("") }
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("$label: ${values.joinToString().ifBlank { "none" }}", style = MaterialTheme.typography.bodyLarge)
        for (value in values) {
            Button(onClick = { onToggle(value) }) { Text("Remove $value from $label") }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ProfileTextField(value = draft, onValueChange = { draft = it })
            Button(onClick = {
                onToggle(draft)
                draft = ""
            }) { Text("Add to $label") }
        }
    }
}

/** One remote-editable list of time windows; edges move in 30-minute steps. */
@Composable
private fun WindowListEditor(label: String, windows: List<TimeWindow>, default: TimeWindow, onChange: (List<TimeWindow>) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("$label: ${windows.size} windows", style = MaterialTheme.typography.bodyLarge)
        windows.forEachIndexed { index, window ->
            Text("Window ${index + 1}: ${minuteOfDay(window.startMinute)} to ${minuteOfDay(window.endMinute)}", style = MaterialTheme.typography.bodyLarge)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { onChange(windows.adjustWindow(index, adjustStart = true, deltaMinutes = -30)) }) { Text("Start -30m") }
                Button(onClick = { onChange(windows.adjustWindow(index, adjustStart = true, deltaMinutes = 30)) }) { Text("Start +30m") }
                Button(onClick = { onChange(windows.adjustWindow(index, adjustStart = false, deltaMinutes = -30)) }) { Text("End -30m") }
                Button(onClick = { onChange(windows.adjustWindow(index, adjustStart = false, deltaMinutes = 30)) }) { Text("End +30m") }
                Button(onClick = { onChange(windows.removeWindowAt(index)) }) { Text("Remove window ${index + 1}") }
            }
        }
        Button(onClick = { onChange(windows + default) }) { Text("Add $label window") }
    }
}

@Composable
private fun SelectionsEditor(current: ProfileState, state: MutableState<ProfileState?>) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        for (kind in SelectionKind.entries) {
            NameListEditor(kind.name, current.selections.values(kind).sorted()) { value ->
                state.value = current.copy(selections = current.selections.toggled(kind, value))
            }
        }
    }
}

@Composable
private fun TeamLeagueEditor(current: ProfileState, state: MutableState<ProfileState?>) {
    var league by remember(current.teamLeague) { mutableStateOf(current.teamLeague?.league ?: "") }
    var team by remember(current.teamLeague) { mutableStateOf(current.teamLeague?.team ?: "") }
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("League", style = MaterialTheme.typography.bodyLarge)
        ProfileTextField(value = league, onValueChange = { league = it })
        Text("Team", style = MaterialTheme.typography.bodyLarge)
        ProfileTextField(value = team, onValueChange = { team = it })
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = {
                teamLeagueOf(league, team)?.let { state.value = current.copy(teamLeague = it) }
            }) { Text("Set team/league") }
            Button(onClick = { state.value = current.copy(teamLeague = null) }) { Text("Clear team/league") }
        }
    }
}

@Composable
private fun AlertTypesEditor(current: ProfileState, state: MutableState<ProfileState?>) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        for (type in AlertType.entries) {
            Button(onClick = {
                state.value = current.copy(alertTypes = current.alertTypes.toggled(type))
            }) { Text("$type alerts: ${onOff(type in current.alertTypes)}") }
        }
    }
}

@Composable
private fun QuietHoursEditor(current: ProfileState, state: MutableState<ProfileState?>) {
    WindowListEditor("Quiet hours", current.quietHours, TimeWindow(22 * 60, 7 * 60)) { windows ->
        state.value = current.copy(quietHours = windows)
    }
}

@Composable
private fun GameDayPeriodsEditor(current: ProfileState, state: MutableState<ProfileState?>) {
    WindowListEditor("Game-day periods", current.gameDay.periods, TimeWindow(13 * 60, 23 * 60)) { periods ->
        state.value = current.copy(gameDay = current.gameDay.copy(periods = periods))
    }
}

@Composable
private fun ProviderPreferenceEditor(current: ProfileState, state: MutableState<ProfileState?>) {
    val pref = current.providerPref
    var market by remember(pref.localMarket) { mutableStateOf(pref.localMarket ?: "") }
    var overrideDraft by remember { mutableStateOf("") }
    fun update(next: ProviderPreference) {
        state.value = current.copy(providerPref = next)
    }
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        pref.order.forEachIndexed { index, provider ->
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("${index + 1}. $provider", style = MaterialTheme.typography.bodyLarge)
                if (index > 0) Button(onClick = { update(pref.moveProviderUp(index)) }) { Text("Move up") }
                Button(onClick = { update(pref.toggleConfirmedAccess(provider)) }) {
                    Text("Access confirmed: ${onOff(provider in pref.confirmedAccess)}")
                }
                Button(onClick = { update(pref.removeProvider(provider)) }) { Text("Remove") }
            }
        }
        NameListEditor("New provider", emptyList()) { value -> update(pref.addProvider(value)) }
        Text("Detected-app overrides (automatic / installed / not installed)", style = MaterialTheme.typography.bodyLarge)
        for ((packageName, installed) in pref.appOverrides.toSortedMap()) {
            Button(onClick = { update(pref.cycleAppOverride(packageName)) }) {
                Text("$packageName: ${if (installed) "installed" else "not installed"} (select to change)")
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ProfileTextField(value = overrideDraft, onValueChange = { overrideDraft = it })
            Button(onClick = {
                update(pref.cycleAppOverride(overrideDraft))
                overrideDraft = ""
            }) { Text("Add app override") }
        }
        Text("Local market", style = MaterialTheme.typography.bodyLarge)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            ProfileTextField(value = market, onValueChange = { market = it })
            Button(onClick = { update(pref.withLocalMarket(market)) }) { Text("Set market") }
            Button(onClick = { update(pref.withLocalMarket(null)) }) { Text("Clear market") }
        }
    }
}

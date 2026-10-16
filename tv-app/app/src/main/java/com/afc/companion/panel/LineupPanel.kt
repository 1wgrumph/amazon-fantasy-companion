package com.afc.companion.panel

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.focusable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.onPreviewKeyEvent
import androidx.compose.ui.input.key.type
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text
import com.afc.companion.net.ApiClient
import com.afc.companion.profile.ProfileState
import com.afc.companion.profile.ProfileStore
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext

/** PanelMode fixed by the P2-X04 verdict: modeB side-by-side route or fullScreen in this app. */
enum class PanelMode { ModeB, FullScreen }

/**
 * Lineup panel (DES-AFC-P2-PANEL): rows, total, progress and scoring basis for
 * the followed team/league, refreshed every 30 s while visible. All state and
 * key handling live in [PanelController]; this composable only renders it.
 * Rows are keyed by player ID, so an update recomposes only changed rows.
 */
@Composable
fun LineupPanel(client: ApiClient, mode: PanelMode, modifier: Modifier = Modifier) {
    val store = remember(client) { ProfileStore(client) }
    var profile by remember { mutableStateOf<ProfileState?>(null) }
    var profileLoaded by remember { mutableStateOf(false) }
    LaunchedEffect(store) {
        profile = store.load()
        profileLoaded = true
    }
    if (!profileLoaded) {
        PanelMessage("Loading profile…", modifier)
        return
    }
    val current = profile
    val teamLeague = current?.teamLeague?.let { "${it.league}/${it.team}" }
    if (current == null || teamLeague == null) {
        PanelMessage("Panel unavailable: no team/league is selected in Profile/Settings.", modifier)
        return
    }
    val controller = remember(client, teamLeague) {
        // The profile stores exactly one team/league pair (ProfileState.teamLeague);
        // its leagues/teams selection sets are unpaired, so the switch cycles this
        // one actual selection and a one-choice switch is a no-op in the controller.
        PanelController(listOf(teamLeague), teamLeague, current.panel.visible)
    }
    var tick by remember(controller) { mutableIntStateOf(0) }
    var fetchAttempted by remember(controller) { mutableStateOf(false) }
    val focusRequester = remember { FocusRequester() }

    LaunchedEffect(controller) {
        runCatching { focusRequester.requestFocus() }
        while (true) {
            if (controller.shouldFetch(System.currentTimeMillis())) {
                try {
                    // Network and parsing stay off the rendering thread (AFC-PR-063).
                    val decoded = withContext(Dispatchers.Default) {
                        client.getPanel(controller.teamLeague).value?.let(::decodePanel)
                    }
                    decoded?.let { controller.onFetched(it, System.currentTimeMillis()) }
                } catch (cancelled: CancellationException) {
                    throw cancelled
                } catch (_: Exception) {
                    // A failed or malformed fetch shows as unavailable, never as stale zeros.
                }
                fetchAttempted = true
                tick++
            }
            delay(1_000)
            // Invalidate every second while composed so a value crossing the 60 s
            // stale boundary re-renders stale without waiting for the 30 s fetch.
            tick++
        }
    }

    BoxWithConstraints(
        modifier
            .fillMaxSize()
            .focusRequester(focusRequester)
            .focusable()
            .onPreviewKeyEvent { event ->
                if (event.type != KeyEventType.KeyDown) {
                    false
                } else {
                    controller.onKey(event.nativeKeyEvent.keyCode, System.currentTimeMillis()).also { if (it) tick++ }
                }
            },
    ) {
        @Suppress("UNUSED_EXPRESSION") tick // reads tick so controller mutations recompose
        val density = LocalDensity.current
        val widthPx = with(density) { maxWidth.roundToPx() }
        val heightPx = with(density) { maxHeight.roundToPx() }
        val layout = panelLayout(mode, widthPx, heightPx)
        // ModeB reserves the left video box and draws nothing there; fullScreen has no video box.
        Box(
            Modifier
                .offset(
                    x = with(density) { layout.panel.left.toDp() },
                    y = with(density) { layout.panel.top.toDp() },
                )
                .size(
                    width = with(density) { layout.panel.width.toDp() },
                    height = with(density) { layout.panel.height.toDp() },
                )
                .background(MaterialTheme.colorScheme.background)
                .padding(32.dp),
        ) {
            if (!controller.visible) {
                Text(
                    "Panel hidden. Press Menu to show it.",
                    style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = Color.White),
                )
            } else {
                // Pass changed immutable state, not the controller: equal parameters
                // would let Compose skip the child and freeze later scores/focus.
                PanelContent(
                    snapshot = controller.snapshot,
                    teamLeague = controller.teamLeague,
                    focused = controller.focused,
                    fetchAttempted = fetchAttempted,
                    nowMs = System.currentTimeMillis(),
                )
            }
        }
    }
}

@Composable
private fun PanelContent(
    snapshot: PanelSnapshot?,
    teamLeague: String?,
    focused: FocusTarget?,
    fetchAttempted: Boolean,
    nowMs: Long,
) {
    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        FocusableRow(focused == FocusTarget.TeamLeagueSwitch) {
            Text(
                "Team/league: ${teamLeague ?: "Unavailable"}",
                style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = Color.White),
            )
        }
        if (snapshot == null) {
            Text(
                if (fetchAttempted) "Panel data unavailable." else "Loading panel…",
                style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = Color.White),
            )
            return@Column
        }
        Text(
            "${PanelText.basis(snapshot.basis)} · ${PanelText.lineupSource(snapshot.source)}",
            style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = Color.White),
        )
        LazyColumn(
            modifier = Modifier.weight(1f).fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            items(snapshot.rows, key = { it.playerId }) { row ->
                FocusableRow(focused == FocusTarget.Row(row.playerId)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(24.dp),
                    ) {
                        Text(
                            row.name,
                            modifier = Modifier.weight(1f),
                            style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = Color.White),
                        )
                        Text(
                            PanelText.gameStatus(row.gameStatus),
                            style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = Color.White),
                        )
                        Text(
                            PanelText.value(row.points, nowMs),
                            style = TextStyle(fontSize = PanelTextSizes.scoreSp.sp, color = Color.White),
                        )
                    }
                }
            }
        }
        FocusableRow(focused == FocusTarget.Total) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    "Team total: ${PanelText.value(snapshot.teamTotal, nowMs)}",
                    style = TextStyle(fontSize = PanelTextSizes.scoreSp.sp, color = Color.White),
                )
                Text(
                    "Progress: ${PanelText.value(snapshot.progress, nowMs)}",
                    style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = Color.White),
                )
            }
        }
    }
}

@Composable
private fun FocusableRow(focused: Boolean, content: @Composable () -> Unit) {
    Box(
        Modifier
            .fillMaxWidth()
            .border(3.dp, if (focused) Color.White else Color.Transparent)
            .padding(12.dp),
    ) { content() }
}

@Composable
private fun PanelMessage(text: String, modifier: Modifier = Modifier) {
    Column(modifier.padding(48.dp), verticalArrangement = Arrangement.spacedBy(24.dp)) {
        Text("Panel", style = MaterialTheme.typography.headlineMedium)
        Text(text, style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = Color.White))
    }
}

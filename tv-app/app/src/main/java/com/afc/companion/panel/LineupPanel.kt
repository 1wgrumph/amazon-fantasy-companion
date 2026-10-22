package com.afc.companion.panel

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.focusable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.relocation.BringIntoViewRequester
import androidx.compose.foundation.relocation.bringIntoViewRequester
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.onPreviewKeyEvent
import androidx.compose.ui.input.key.type
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text
import com.afc.companion.R
import com.afc.companion.alerts.AlertInbox
import com.afc.companion.alerts.AlertNotifier
import com.afc.companion.net.ApiClient
import com.afc.companion.profile.DeviceSettings
import com.afc.companion.profile.ProfileState
import com.afc.companion.profile.ProfileStore
import com.afc.companion.profile.Sport
import com.afc.companion.ui.theme.AfcLoadingIndicator
import com.afc.companion.ui.theme.TvFocusStyle
import com.afc.companion.ui.theme.TvPalette
import com.afc.companion.ui.theme.tvFocusStyle
import com.afc.companion.ui.theme.tvSafeZonePadding
import com.afc.companion.watch.WatchLauncher
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlin.math.roundToInt

/** PanelMode fixed by the P2-X04 verdict: modeB side-by-side route or fullScreen in this app. */
enum class PanelMode { ModeB, FullScreen }

/**
 * Lineup panel (DES-AFC-P2-PANEL): rows, total, progress and scoring basis for
 * the followed team/league, refreshed every 30 s while visible. All state and
 * key handling live in [PanelController]; this composable only renders it.
 * Rows are keyed by player ID, so an update recomposes only changed rows.
 * Monitoring alerts sit above the lineup (panel-only presentation, P2-X02), each
 * with Watch and Dismiss, also when no team/league is selected.
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
        PanelMessage(modifier) { AfcLoadingIndicator("Loading profile…") }
        return
    }
    val current = profile
    val teamLeague = panelTeamLeague(current)
    val context = LocalContext.current
    val revealOnNewAlert = remember(mode) { revealsOnNewAlert(DeviceSettings(context).showPanelOnNewAlert, mode) }
    val controller = remember(client, teamLeague) {
        // The profile stores exactly one team/league pair (ProfileState.teamLeague);
        // its leagues/teams selection sets are unpaired, so the switch cycles this
        // one actual selection and a one-choice switch is a no-op in the controller.
        PanelController(listOfNotNull(teamLeague), teamLeague, current?.panel?.visible ?: true, revealOnNewAlert)
    }
    var tick by remember(controller) { mutableIntStateOf(0) }
    var fetchAttempted by remember(controller) { mutableStateOf(false) }
    var watchOutcome by remember { mutableStateOf<String?>(null) }
    var watching by remember { mutableStateOf(false) }
    val focusRequester = remember { FocusRequester() }
    val scope = rememberCoroutineScope()

    LaunchedEffect(controller) {
        AlertInbox.alerts.collect { alerts ->
            controller.onAlerts(panelAlerts(alerts))
            tick++
        }
    }

    fun onAlertCommand(command: AlertCommand) {
        when (command) {
            is AlertCommand.Dismiss -> {
                AlertInbox.dismiss(command.alertId)
                AlertNotifier(context).cancel(command.alertId)
            }
            is AlertCommand.Watch -> {
                val alert = AlertInbox.find(command.alertId) ?: return
                val eventId = AlertNotifier.watchEventId(alert) ?: return
                if (watching) return
                watching = true
                scope.launch {
                    try {
                        // The second OK press was the switching confirmation (PanelController.select).
                        // WatchLauncher reports a started attempt even if this scope is cancelled meanwhile.
                        WatchLauncher(context).watchAlert(eventId, alert.route, client, current?.switchingConfirm ?: true, mode) { true }
                            ?.let { watchOutcome = PanelText.watchOutcome(it) }
                    } finally {
                        watching = false
                    }
                }
            }
        }
    }

    LaunchedEffect(controller) {
        runCatching { focusRequester.requestFocus() }
        runPanelUpdates(client, controller) { fetched ->
            if (fetched) fetchAttempted = true
            tick++
        }
    }

    BoxWithConstraints(
        modifier
            .fillMaxSize()
            .tvSafeZonePadding()
            .focusRequester(focusRequester)
            .focusable()
            .onPreviewKeyEvent { event ->
                if (event.type != KeyEventType.KeyDown) {
                    false
                } else {
                    val key = event.nativeKeyEvent.keyCode
                    if (controller.bindings()[key] == PanelAction.Select) {
                        controller.select(current?.switchingConfirm ?: true)?.let(::onAlertCommand)
                    }
                    controller.onKey(key, System.currentTimeMillis()).also { if (it) tick++ }
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
                .background(MaterialTheme.colorScheme.surface.copy(alpha = 0.72f), RoundedCornerShape(16.dp))
                .padding(8.dp),
        ) {
            if (!controller.visible) {
                Text(
                    "My lineup is hidden. Press Menu to show it.",
                    style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = MaterialTheme.colorScheme.onSurface),
                )
            } else {
                // Pass changed immutable state, not the controller: equal parameters
                // would let Compose skip the child and freeze later scores/focus.
                PanelContent(
                    alerts = controller.panelAlerts,
                    armedWatch = controller.armedWatch,
                    watchOutcome = watchOutcome,
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

/** The profile's one team/league pair as the panel key, or null when none is selected. */
fun panelTeamLeague(profile: ProfileState?): String? = profile?.teamLeague?.let { "${it.league}/${it.team}" }

/**
 * The one panel update owner, shared by [LineupPanel] and the overlay: fetches the selected
 * team/league while [controller] is visible. [onTick] runs after each fetch attempt (true) and
 * every second (false), so a value crossing the 60 s stale boundary re-renders without a fetch.
 */
suspend fun runPanelUpdates(client: ApiClient, controller: PanelController, onTick: (fetched: Boolean) -> Unit): Nothing {
    while (true) {
        if (controller.teamLeague != null && controller.shouldFetch(System.currentTimeMillis())) {
            try {
                // Network and parsing stay off the rendering thread (AFC-PR-063).
                val decoded = controller.teamLeague?.let { loadPanelSnapshot(client, it) }
                decoded?.let { controller.onFetched(it, System.currentTimeMillis()) }
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (_: Exception) {
                // A failed or malformed fetch shows as unavailable, never as stale zeros.
            }
            onTick(true)
        }
        delay(1_000)
        onTick(false)
    }
}

/** The existing panel endpoint and decoder also supply cards while the panel window is hidden. */
private suspend fun loadPanelSnapshot(client: ApiClient, teamLeague: String): PanelSnapshot? =
    withContext(Dispatchers.Default) { client.getPanel(teamLeague).value?.let { decodePanel(it) } }

internal suspend fun alertCardPanel(client: ApiClient): PanelSnapshot? = try {
    val selected = panelTeamLeague(ProfileStore(client).load())
    selected?.let { loadPanelSnapshot(client, it)?.takeIf { snapshot -> snapshot.teamLeague == selected } }
} catch (cancelled: CancellationException) {
    throw cancelled
} catch (_: Exception) {
    null
}

@Composable
internal fun PanelContent(
    alerts: List<PanelAlert>,
    armedWatch: String?,
    watchOutcome: String?,
    snapshot: PanelSnapshot?,
    teamLeague: String?,
    focused: FocusTarget?,
    fetchAttempted: Boolean,
    nowMs: Long,
    compact: Boolean = false,
) {
    if (compact && snapshot != null && teamLeague != null) {
        CompactPanelContent(snapshot, alerts, nowMs)
        return
    }
    val loading = snapshot == null && teamLeague != null && !fetchAttempted
    Box(Modifier.fillMaxSize()) {
        if (snapshot == null) {
            if (loading) AfcLoadingIndicator("Loading panel…")
        }
        // One scrolling column: up to three alert cards are taller than the panel, so the focused
        // target is brought into view instead of being laid out below the window.
        Column(
            // Pending-data controls scroll above the centred loading layer, without covering it.
            Modifier.fillMaxHeight(if (loading) 0.25f else 1f).fillMaxWidth()
                .verticalScroll(rememberScrollState()).padding(8.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            if (!compact) LineupHeading()
            watchOutcome?.let {
                Text(it, style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = MaterialTheme.colorScheme.onSurface))
            }
            alerts.forEach { alert -> AlertCard(alert, armedWatch == alert.id, focused, revealWholeCard = !loading, compact = compact) }
            // The overlay cannot take focus, so its compact form leaves out the team/league switch.
            if (!compact) FocusableRow(focused == FocusTarget.TeamLeagueSwitch) {
                Text(
                    "Team/league: ${teamLeague ?: "Unavailable"}",
                    style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = MaterialTheme.colorScheme.onSurface),
                )
            }
            if (teamLeague == null) {
                Row(horizontalArrangement = Arrangement.spacedBy(24.dp), verticalAlignment = Alignment.CenterVertically) {
                    // Decorative: the sentence beside it carries the meaning.
                    Image(painterResource(R.drawable.ic_lineup_empty), contentDescription = null, modifier = Modifier.size(160.dp, 120.dp))
                    Text(
                        "No lineup yet. Choose a team and league in My setup.",
                        style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = MaterialTheme.colorScheme.onSurface),
                    )
                }
                return@Column
            }
            if (snapshot == null) {
                if (fetchAttempted) {
                    Text(
                        "Panel data unavailable.",
                        style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = MaterialTheme.colorScheme.onSurface),
                    )
                }
                return@Column
            }
            PanelHeader(snapshot)
            snapshot.rows.forEach { row ->
                key(row.playerId) {
                    FocusableRow(focused == FocusTarget.Row(row.playerId)) {
                        val body = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = MaterialTheme.colorScheme.onSurface)
                        // Compact: the name gets its own line, so a long stale label cannot squeeze it out.
                        Column {
                            if (compact) Text(row.name, style = body)
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(24.dp),
                            ) {
                                if (!compact) Text(row.name, modifier = Modifier.weight(1f), style = body)
                                Text(
                                    PanelText.gameStatus(row.gameStatus),
                                    modifier = if (compact) Modifier.weight(1f) else Modifier,
                                    style = body,
                                )
                                Text(
                                    PanelText.value(row.points, nowMs),
                                    style = TextStyle(fontSize = PanelTextSizes.scoreSp.sp, color = MaterialTheme.colorScheme.onSurface),
                                )
                            }
                        }
                    }
                }
            }
            FocusableRow(focused == FocusTarget.Total) {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        "Team total: ${PanelText.value(snapshot.teamTotal, nowMs)}",
                        style = TextStyle(fontSize = PanelTextSizes.scoreSp.sp, color = MaterialTheme.colorScheme.onSurface),
                    )
                    Text(
                        "Lineup progress: ${progressText(snapshot.progress, nowMs)}",
                        style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = MaterialTheme.colorScheme.onSurface),
                    )
                }
            }
        }
    }
}

/** A fixed total and timed lineup pages: this window cannot receive remote scrolling. */
@Composable
private fun CompactPanelContent(snapshot: PanelSnapshot, alerts: List<PanelAlert>, nowMs: Long) {
    val body = TextStyle(fontSize = 22.sp, color = MaterialTheme.colorScheme.onSurface)
    Column(Modifier.fillMaxSize().padding(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        LineupHeading()
        PanelHeader(snapshot)
        alerts.take(1).forEach { Text(it.text.headline, style = body) }
        BoxWithConstraints(Modifier.weight(1f).fillMaxWidth()) {
            val pageSize = (maxHeight.value / 120f).toInt().coerceAtLeast(1)
            val pages = snapshot.rows.chunked(pageSize)
            var page by remember(snapshot.teamLeague, pageSize) { mutableIntStateOf(0) }
            LaunchedEffect(pages.size) {
                page = 0
                while (pages.size > 1) {
                    delay(5_000)
                    page = (page + 1) % pages.size
                }
            }
            Column {
                pages.getOrNull(page)?.forEach { row ->
                    Column(Modifier.height(120.dp)) {
                        Text(row.name, style = body, maxLines = 2, overflow = TextOverflow.Ellipsis)
                        Text(PanelText.gameStatus(row.gameStatus), style = body)
                        Text(PanelText.value(row.points, nowMs), style = body)
                    }
                }
            }
        }
        Text("Team total: ${PanelText.value(snapshot.teamTotal, nowMs)}", style = body)
        Text("Lineup progress: ${progressText(snapshot.progress, nowMs)}", style = body)
    }
}

@Composable
private fun AlertCard(alert: PanelAlert, armed: Boolean, focused: FocusTarget?, revealWholeCard: Boolean, compact: Boolean = false) {
    // Reveal the whole card when it fits; loading leaves the focused action to scroll into view.
    val cardFocused = focused == FocusTarget.AlertWatch(alert.id) || focused == FocusTarget.AlertDismiss(alert.id)
    val flare = MaterialTheme.colorScheme.tertiary
    Column(
        Modifier.fillMaxWidth().bringIntoViewWhen(cardFocused && revealWholeCard).tvFocusStyle(cardFocused)
            // Alert flare: a stripe on the card's leading edge, inside the focus outline.
            .drawBehind {
                val inset = TvFocusStyle.borderWidthDp.dp.toPx()
                drawRect(flare, topLeft = Offset(inset, inset), size = Size(8.dp.toPx(), size.height - 2 * inset))
            }
            .padding(start = 28.dp, top = 16.dp, end = 16.dp, bottom = 16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        val body = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = MaterialTheme.colorScheme.onSurface)
        Text(alert.text.headline, style = TextStyle(fontSize = PanelTextSizes.scoreSp.sp, color = MaterialTheme.colorScheme.onSurface))
        // Compact (overlay): headline and player only; access, commentary, Watch and Dismiss stay in Companion, which can take focus.
        if (compact) {
            alert.text.context.ifEmpty { null }?.let { Text(it, style = body) }
            return@Column
        }
        listOfNotNull(alert.text.context.ifEmpty { null }, alert.text.access, alert.text.commentary).forEach { Text(it, style = body) }
        // Stacked, matching the UP/DOWN focus order.
        if (alert.watchable) {
            FocusableRow(focused == FocusTarget.AlertWatch(alert.id)) {
                Text(if (armed) "Press OK again to switch apps" else "Watch", style = body)
            }
        }
        FocusableRow(focused == FocusTarget.AlertDismiss(alert.id)) { Text("Dismiss", style = body) }
    }
}

@Composable
private fun FocusableRow(focused: Boolean, content: @Composable () -> Unit) {
    Box(
        Modifier
            .fillMaxWidth()
            .bringIntoViewWhen(focused)
            .tvFocusStyle(focused)
            .padding(12.dp),
    ) { content() }
}

/** Scrolls the enclosing column until this element is on screen whenever [focused] becomes true. */
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun Modifier.bringIntoViewWhen(focused: Boolean): Modifier {
    val requester = remember { BringIntoViewRequester() }
    LaunchedEffect(focused) { if (focused) requester.bringIntoView() }
    return bringIntoViewRequester(requester)
}

@Composable
private fun LineupHeading() {
    Text("My lineup", style = MaterialTheme.typography.headlineMedium, color = MaterialTheme.colorScheme.onSurface)
}

/** Progress (0..1, the lineup's mean game state) as a whole percent, keeping PanelText's replay/stale labels. */
internal fun progressText(progress: PanelValue, nowMs: Long): String {
    val text = PanelText.value(progress, nowMs)
    val number = progress.value ?: return text
    return "${(number * 100).roundToInt()}%" + text.removePrefix(number.toString())
}

/** Scoring basis and lineup source; a tagged sport gets its accent as a chip. */
@Composable
private fun PanelHeader(snapshot: PanelSnapshot) {
    val sport = Sport.entries.find { it.label == snapshot.sport }
    val modifier = if (sport == null) Modifier else {
        Modifier.background(Color(TvPalette.sportAccentArgb(sport)), RoundedCornerShape(50)).padding(horizontal = 20.dp, vertical = 6.dp)
    }
    Text(
        PanelText.header(snapshot),
        modifier = modifier,
        style = TextStyle(
            fontSize = PanelTextSizes.bodySp.sp,
            fontWeight = FontWeight.Medium,
            color = sport?.let { Color(TvPalette.onSportAccentArgb(it)) } ?: MaterialTheme.colorScheme.onSurface,
        ),
    )
}

@Composable
private fun PanelMessage(modifier: Modifier = Modifier, content: @Composable () -> Unit) {
    Box(modifier.fillMaxSize().tvSafeZonePadding().padding(8.dp)) {
        Text("My lineup", style = MaterialTheme.typography.headlineMedium)
        content()
    }
}

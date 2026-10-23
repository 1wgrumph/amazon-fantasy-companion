package com.afc.companion.panel

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.foundation.layout.width
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
        // Starts on the profile's selected pair; the other lineup pairs arrive with
        // the first panel fetch (PanelSnapshot.teamLeagues) and join the switch.
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
                    tabs = controller.teamLeagueTabs,
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
    tabs: List<String> = listOfNotNull(teamLeague),
    nowMs: Long,
    compact: Boolean = false,
) {
    if (compact && snapshot != null && teamLeague != null) {
        CompactPanelContent(snapshot)
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
            // The overlay cannot take focus, so its compact form leaves out the sport tab strip.
            if (!compact) {
                LineupHeading()
                SportTabs(tabs, teamLeague, snapshot, focused == FocusTarget.TeamLeagueSwitch)
            }
            watchOutcome?.let {
                Text(it, style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = MaterialTheme.colorScheme.onSurface))
            }
            alerts.forEach { alert -> AlertCard(alert, armedWatch == alert.id, focused, revealWholeCard = !loading, compact = compact) }
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
                        "Scores didn't load. Retrying.",
                        style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = MaterialTheme.colorScheme.onSurface),
                    )
                }
                return@Column
            }
            // The selected tab already names the sport; the header adds only a real matchup.
            if (PanelText.title(snapshot) != CornerCardText.sport(snapshot)) PanelHeader(snapshot)
            val clock = PanelText.clock(snapshot)
            FocusableRow(focused == FocusTarget.Total) { ScoreLine(snapshot, clock, PanelTextSizes.scoreSp * 1.5f) }
            PanelText.byPoints(snapshot.rows).forEach { row ->
                key(row.playerId) {
                    FocusableRow(focused == FocusTarget.Row(row.playerId)) {
                        PlayerLine(row, clock, PanelTextSizes.bodySp, PanelTextSizes.scoreSp)
                    }
                }
            }
        }
    }
}

/** "Total 121.8" in the brand gold with the game clock on its own line below, so a wide total never overlaps it. */
@Composable
private fun ScoreLine(snapshot: PanelSnapshot, clock: String?, size: Float) {
    Column(Modifier.fillMaxWidth()) {
        Text(
            "Total ${PanelText.points(snapshot.teamTotal)}",
            maxLines = 1,
            softWrap = false,
            style = TextStyle(fontSize = size.sp, fontWeight = FontWeight.Black, color = Color(TvPalette.primaryArgb), fontFeatureSettings = "tnum"),
        )
        clock?.let {
            Text(it, style = TextStyle(fontSize = (size * 0.55f).sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurface))
        }
    }
}

/** One player on one line: muted slot, name, their own game's status when it differs from the header clock, points. */
@Composable
private fun PlayerLine(row: PanelRow, clock: String?, nameSp: Float, pointsSp: Float) {
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        row.slot?.let {
            // Fixed column wide enough for "UTIL"/"FLEX" so names align under each other.
            Text(
                it,
                modifier = Modifier.width((nameSp * 2.2f).dp),
                maxLines = 1,
                softWrap = false,
                style = TextStyle(fontSize = (nameSp * 0.7f).sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)),
            )
        }
        Text(
            PanelText.shortName(row.name),
            modifier = Modifier.weight(1f),
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            style = TextStyle(fontSize = nameSp.sp, color = MaterialTheme.colorScheme.onSurface),
        )
        row.gameStatus?.takeIf { it.isNotBlank() && it != clock }?.let {
            Text(it, maxLines = 1, style = TextStyle(fontSize = (nameSp * 0.7f).sp, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)))
        }
        Text(
            PanelText.points(row.points),
            style = TextStyle(fontSize = pointsSp.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface, fontFeatureSettings = "tnum"),
        )
    }
}

/** Matchup, total and clock, then every player by points; a fresh window or pair starts at the top. */
@Composable
private fun CompactPanelContent(snapshot: PanelSnapshot) {
    val clock = PanelText.clock(snapshot)
    Column(Modifier.fillMaxSize().padding(horizontal = 12.dp, vertical = 8.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
        PanelHeader(snapshot)
        ScoreLine(snapshot, clock, 44f)
        key(snapshot.teamLeague) {
            Column(Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                PanelText.byPoints(snapshot.rows).forEach { PlayerLine(it, clock, 24f, 28f) }
            }
        }
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
        if (alert.text.headline != "Score update") {
            Text(alert.text.headline, style = TextStyle(fontSize = PanelTextSizes.scoreSp.sp, color = MaterialTheme.colorScheme.onSurface))
        }
        // Compact overlay leaves access, commentary, Watch and Dismiss in Companion, which can take focus.
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

/**
 * One pill per lineup, labelled by sport: the selected one filled with its sport accent, the others
 * outlined in theirs. Focusing a tab selects it, so the gold focus ring sits on the selected pill.
 */
@Composable
private fun SportTabs(tabs: List<String>, selected: String?, snapshot: PanelSnapshot?, focused: Boolean) {
    Row(Modifier.bringIntoViewWhen(focused), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
        if (tabs.isEmpty()) {
            Text("No team", style = TextStyle(fontSize = PanelTextSizes.bodySp.sp, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)))
        }
        tabs.forEach { tab ->
            val label = PanelText.sport(tab) ?: CornerCardText.sport(snapshot?.takeIf { it.teamLeague == tab }) ?: "Lineup"
            val sport = Sport.entries.find { it.label == label }
            val accent = sport?.let { Color(TvPalette.sportAccentArgb(it)) } ?: Color(TvPalette.primaryArgb)
            val isSelected = tab == selected
            val pill = RoundedCornerShape(50)
            Text(
                label,
                modifier = Modifier
                    .then(if (isSelected && focused) Modifier.border(TvFocusStyle.borderWidthDp.dp, Color(TvFocusStyle.focusedBorderArgb), pill).padding(TvFocusStyle.borderWidthDp.dp) else Modifier)
                    .then(if (isSelected) Modifier.background(accent, pill) else Modifier.border(2.dp, accent, pill))
                    .padding(horizontal = 28.dp, vertical = 8.dp),
                maxLines = 1,
                softWrap = false,
                style = TextStyle(
                    fontSize = PanelTextSizes.scoreSp.sp,
                    fontWeight = if (isSelected) FontWeight.Black else FontWeight.SemiBold,
                    color = if (isSelected) sport?.let { Color(TvPalette.onSportAccentArgb(it)) } ?: Color(TvPalette.surfaceArgb) else accent,
                ),
            )
        }
    }
}

/** Sport and matchup; a tagged sport gets its accent as a chip. */
@Composable
private fun PanelHeader(snapshot: PanelSnapshot) {
    val sport = Sport.entries.find { it.label == snapshot.sport }
    val modifier = if (sport == null) Modifier else {
        Modifier.background(Color(TvPalette.sportAccentArgb(sport)), RoundedCornerShape(50)).padding(horizontal = 20.dp, vertical = 6.dp)
    }
    Text(
        PanelText.title(snapshot),
        modifier = modifier,
        style = TextStyle(
            fontSize = PanelTextSizes.bodySp.sp,
            fontWeight = FontWeight.Bold,
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

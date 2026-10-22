package com.afc.companion.panel

import androidx.activity.ComponentActivity
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Density
import androidx.compose.ui.Modifier
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.unit.dp
import com.afc.companion.ui.theme.AfcTheme
import com.afc.companion.alerts.AlertText
import org.junit.Rule
import org.junit.Test

/** F02: observed 1080p card-reserved geometry at overlay density 1.3; resource group: owned TV display. */
class CompactPanelLayoutTest {
    @get:Rule val rule = createAndroidComposeRule<ComponentActivity>()

    @Test fun totalRemainsVisibleAndLineupAdvancesWithoutRemoteScrolling() {
        val now = System.currentTimeMillis()
        val snapshot = PanelSnapshot("review/team", 1, ScoringBasis.HalfPpr,
            (1..9).map { PanelRow("p$it", if (it == 9) "Sample Player With A Long Surname Nine" else "Sample Player $it", PanelValue(it.toDouble(), null, "live", now - 70_000), "Q2 08:14") },
            PanelValue(112.5, null, "live", now), PanelValue(0.5, null, "live", now), sport = "NFL")
        rule.mainClock.autoAdvance = false
        rule.setContent {
            AfcTheme {
                CompositionLocalProvider(LocalDensity provides Density(1.3f)) {
                Box(Modifier.size(369.dp, 600.dp)) {
                    PanelContent(listOf(PanelAlert("alert", AlertText("Player score update", "Sample Receiver", "", null), false)), null, null, snapshot, snapshot.teamLeague, null, true, now, compact = true)
                }
                }
            }
        }
        rule.mainClock.advanceTimeBy(100)
        rule.onNodeWithText("Team total: 112.5").assertIsDisplayed()
        rule.onNodeWithText("Sample Player 1").assertIsDisplayed()
        // Rows must become visible under the same measured bounds without any focus/key/scroll action.
        repeat(9) {
            rule.mainClock.advanceTimeBy(5_100)
            rule.onNodeWithText("Team total: 112.5").assertIsDisplayed()
            if (rule.onAllNodesWithText("Sample Player With A Long Surname Nine").fetchSemanticsNodes().isNotEmpty()) {
                rule.onNodeWithText("Sample Player With A Long Surname Nine").assertIsDisplayed()
                rule.onNodeWithText("9.0 (stale 70s)").assertIsDisplayed()
                return
            }
        }
        throw AssertionError("last lineup row never becomes visible without remote input")
    }
}

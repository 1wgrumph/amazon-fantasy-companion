package com.afc.companion.panel

import com.afc.companion.ui.theme.assertLoadingCall
import com.afc.companion.ui.theme.productSource
import com.afc.companion.ui.theme.sourceBlock
import org.junit.Test

class PanelLoadingTest {
    @Test fun panelProfileLoadingUsesSharedIndicator() {
        val screen = sourceBlock(productSource("panel/LineupPanel.kt"), Regex("\\bfun\\s+LineupPanel\\s*\\("))
        val loading = sourceBlock(screen, Regex("if\\s*\\(\\s*!profileLoaded\\s*\\)"))
        assertLoadingCall(loading, "Loading profile…")
    }

    @Test fun panelDataLoadingUsesSharedIndicator() {
        val content = sourceBlock(productSource("panel/LineupPanel.kt"), Regex("\\bfun\\s+PanelContent\\s*\\("))
        val loading = sourceBlock(content, Regex("if\\s*\\(\\s*snapshot\\s*==\\s*null\\s*\\)"))
        assertLoadingCall(loading, "Loading panel…")
    }
}

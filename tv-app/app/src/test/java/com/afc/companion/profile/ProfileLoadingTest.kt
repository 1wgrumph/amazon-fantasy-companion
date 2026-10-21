package com.afc.companion.profile

import com.afc.companion.ui.theme.assertLoadingCall
import com.afc.companion.ui.theme.productSource
import com.afc.companion.ui.theme.sourceBlock
import org.junit.Test

class ProfileLoadingTest {
    @Test fun settingsProfileLoadingUsesSharedIndicator() {
        val screen = sourceBlock(productSource("profile/ProfileSettingsScreen.kt"), Regex("\\bfun\\s+ProfileSettingsScreen\\s*\\("))
        assertLoadingCall(screen, "Loading profile…")
    }
}

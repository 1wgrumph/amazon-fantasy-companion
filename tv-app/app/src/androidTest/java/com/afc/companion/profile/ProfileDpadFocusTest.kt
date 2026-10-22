package com.afc.companion.profile

import android.view.KeyEvent
import androidx.activity.ComponentActivity
import androidx.compose.ui.test.assertIsFocused
import androidx.compose.ui.test.assertTextEquals
import androidx.compose.ui.test.hasAnyDescendant
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.test.performSemanticsAction
import androidx.compose.ui.test.performImeAction
import androidx.compose.ui.test.performTextReplacement
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.requestFocus
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.UiDevice
import com.afc.companion.net.ApiClient
import com.afc.companion.ui.theme.AfcTheme
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.io.File
import java.io.OutputStream
import java.net.HttpURLConnection
import java.net.URL
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test

/**
 * BUG-A02-1: profile text fields must not trap D-pad focus on TV. DPAD_DOWN
 * from the control before League enters League, a further DPAD_DOWN leaves
 * League for Team, and DPAD_UP returns to League. Synthetic fixture only.
 * Resource group: fire-tv-stick (one device, serialized under its lease).
 */
class ProfileDpadFocusTest {
    @get:Rule val rule = createAndroidComposeRule<ComponentActivity>()

    @Before fun loadProfileFixture() {
        rule.setContent { AfcTheme { ProfileSettingsScreen(fakeClient()) } }
        rule.waitUntil(timeoutMillis = 5_000) {
            rule.onAllNodes(hasText("LeagueOne")).fetchSemanticsNodes().size == 1 &&
                rule.onAllNodes(hasText("TeamOne")).fetchSemanticsNodes().size == 1
        }
    }

    @Test fun dpadDownLeavesLeagueFieldAndUpReturns() {
        val league = rule.onNode(hasText("LeagueOne"))
        val team = rule.onNode(hasText("TeamOne"))
        val beforeLeague = rule.onNode(hasClickAction() and hasAnyDescendant(hasText("Add favorite team")), useUnmergedTree = true)
        league.performScrollTo()
        beforeLeague.performScrollTo()
        beforeLeague.requestFocus()
        beforeLeague.assertIsFocused()
        key(KeyEvent.KEYCODE_DPAD_DOWN)
        league.assertIsFocused()
        key(KeyEvent.KEYCODE_DPAD_DOWN)
        team.assertIsFocused()
        key(KeyEvent.KEYCODE_DPAD_UP)
        league.assertIsFocused()
    }

    @Test fun imeNextMovesForwardAndPreservesEditedText() {
        val league = rule.onNode(hasText("LeagueOne"))
        league.performScrollTo()
        league.requestFocus()
        key(KeyEvent.KEYCODE_DPAD_CENTER)
        league.performTextReplacement("Edited league")
        rule.onNode(hasText("Edited league")).performImeAction()
        rule.onNode(hasText("TeamOne")).assertIsFocused()
        rule.onNode(hasText("Edited league")).assertTextEquals("Edited league")
    }

    @Test fun keyboardNavigationWorksDuringEditingAndBackRestoresFormNavigation() {
        val league = rule.onNode(hasText("LeagueOne"))
        league.performScrollTo()
        league.performSemanticsAction(SemanticsActions.OnClick) { it() }
        key(KeyEvent.KEYCODE_DPAD_UP)
        league.assertIsFocused()
        key(KeyEvent.KEYCODE_BACK)
        key(KeyEvent.KEYCODE_DPAD_DOWN)
        rule.onNode(hasText("TeamOne")).assertIsFocused()
        key(KeyEvent.KEYCODE_DPAD_CENTER)
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val device = UiDevice.getInstance(instrumentation)
        device.waitForIdle()
        assertTrue(device.takeScreenshot(
            File(instrumentation.targetContext.cacheDir, "profile-team-focus.png"),
        ))
    }

    private fun key(keyCode: Int) {
        InstrumentationRegistry.getInstrumentation().sendKeyDownUpSync(keyCode)
        rule.waitForIdle()
    }

    private fun fakeClient(): ApiClient = ApiClient(
        baseUrl = "http://127.0.0.1:9",
        openConnection = { url -> FakeConnection(url, PROFILE_JSON) },
        backoff = {},
    )

    private class FakeConnection(url: URL, private val body: String) : HttpURLConnection(url) {
        override fun connect() { connected = true }
        override fun disconnect() { connected = false }
        override fun usingProxy(): Boolean = false
        override fun getResponseCode(): Int = 200
        override fun getInputStream(): InputStream = ByteArrayInputStream(body.toByteArray(Charsets.UTF_8))
        override fun getOutputStream(): OutputStream = ByteArrayOutputStream()
    }

    private companion object {
        const val PROFILE_JSON =
            """{"schemaVersion":1,"id":"profile-fixture","revision":1,"source":"manual",""" +
                """"updatedAt":"2026-10-14T12:00:00Z","data":{"scoringPreset":"halfPpr",""" +
                """"teamLeague":{"league":"LeagueOne","team":"TeamOne"}}}"""
    }
}

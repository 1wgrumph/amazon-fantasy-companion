package com.afc.companion.profile

import androidx.compose.runtime.mutableStateOf
import com.afc.companion.net.ApiClient
import java.io.File
import java.lang.reflect.Method
import java.net.HttpURLConnection
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.cancel
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test

/**
 * Repair regressions for A02-R-F01/F02/F03: the screen editors change every field and the
 * values survive save/reload, detection stays hidden while X07 is pending, and an in-flight
 * save never overwrites a newer draft.
 */
class ProfileRepairTest {
    private fun store(server: ProfileServer) = ProfileStore(ApiClient(server.baseUrl, { "session-fixture" }))

    @Test fun editorOperationsChangeEveryFieldAndSurviveSaveReload() = runBlocking {
        ProfileServer().use { server ->
            val store = store(server)
            val loaded = store.load()
            assertNotNull(loaded)
            var edited = loaded!!
            // Same edit operations the screen buttons invoke (ProfileEdits + copy into the draft).
            edited = edited.copy(
                selections = edited.selections
                    .toggled(SelectionKind.Leagues, "league-a")
                    .toggled(SelectionKind.Teams, "team-7")
                    .toggled(SelectionKind.Players, "player-11")
                    .toggled(SelectionKind.Players, "player-23")
                    .toggled(SelectionKind.Players, "player-23")
                    .toggled(SelectionKind.FavoriteTeams, "KC"),
            )
            edited = edited.copy(teamLeague = teamLeagueOf(" league-a ", " team-7 "))
            edited = edited.copy(alertTypes = edited.alertTypes.toggled(AlertType.RedZone).toggled(AlertType.CloseGame))
            edited = edited.copy(quietHours = (edited.quietHours + TimeWindow(22 * 60, 7 * 60)).adjustWindow(0, adjustStart = true, deltaMinutes = -30))
            edited = edited.copy(
                gameDay = edited.gameDay.copy(
                    periods = ((edited.gameDay.periods + TimeWindow(13 * 60, 23 * 60)).adjustWindow(0, adjustStart = false, deltaMinutes = -30) +
                        TimeWindow(0, 60)).removeWindowAt(1),
                ),
            )
            edited = edited.copy(
                providerPref = edited.providerPref
                    .addProvider("provider-a").addProvider("provider-b").moveProviderUp(1)
                    .toggleConfirmedAccess("provider-b")
                    .cycleAppOverride("com.example.provider.a").cycleAppOverride("com.example.provider.a")
                    .cycleAppOverride("com.example.provider.c")
                    .withLocalMarket(" market-501 "),
            )
            assertEquals(setOf("player-11"), edited.selections.players)
            assertEquals(TeamLeague("league-a", "team-7"), edited.teamLeague)
            assertEquals(listOf(TimeWindow(21 * 60 + 30, 7 * 60)), edited.quietHours)
            assertEquals(listOf(TimeWindow(13 * 60, 22 * 60 + 30)), edited.gameDay.periods)
            assertEquals(listOf("provider-b", "provider-a"), edited.providerPref.order)
            assertEquals(mapOf("com.example.provider.a" to false, "com.example.provider.c" to true), edited.providerPref.appOverrides)
            assertEquals("market-501", edited.providerPref.localMarket)

            assertEquals(edited, store.save(edited))
            assertEquals("edited profile survives reload", edited, store(server).load())
        }
    }

    @Test fun editorOperationsRejectBlankInputAndCycleOverrides() {
        val selections = FantasySelections(setOf("league-a"), emptySet(), emptySet(), emptySet())
        assertEquals(selections, selections.toggled(SelectionKind.Leagues, "  "))
        assertEquals(null, teamLeagueOf("", "team-7"))
        val pref = ProviderPreference(listOf("provider-a"), emptySet(), emptyMap(), null)
        assertEquals(pref, pref.addProvider("provider-a"))
        assertEquals(pref, pref.cycleAppOverride("com.example.provider.a")
            .cycleAppOverride("com.example.provider.a").cycleAppOverride("com.example.provider.a"))
        assertEquals(null, pref.withLocalMarket("market-501").withLocalMarket(" ").localMarket)
        assertEquals(listOf(TimeWindow(0, 1439)), listOf(TimeWindow(30, 1409)).adjustWindow(0, adjustStart = true, deltaMinutes = -30)
            .adjustWindow(0, adjustStart = false, deltaMinutes = 30))
    }

    @Test fun screenBindsDetectionUnsupportedUntilX07AndWritesEveryEditedField() {
        val source = screenSource()
        val binding = Regex("""profileControls\(detectionSupported = (true|false), voiceRouteVerified = (true|false)\)""").find(source)
        assertNotNull("screen capability binding", binding)
        assertEquals("X07 pending means detection unsupported", "false", binding!!.groupValues[1])
        val controls = profileControls(detectionSupported = false, voiceRouteVerified = false)
        assertFalse(ProfileControl.DetectionOptIn in controls.visible)
        assertTrue(controls.limits[ProfileControl.DetectionOptIn]!!.isNotBlank())
        for (field in listOf("selections", "teamLeague", "alertTypes", "quietHours", "providerPref", "periods")) {
            assertTrue("screen writes $field", Regex("""\b$field\s*=""").containsMatchIn(source))
        }
    }

    @Test fun saveInFlightEditIsResavedNotOverwritten() {
        val race = SaveRace()
        try {
            race.startSave()
            race.editExcitementToMild()
            race.releaseSave()
            assertEquals("Profile saved.", race.awaitMessage())
            assertEquals("newer edit kept", Excitement.Mild, race.state.value!!.excitement)
            assertEquals("newer edit actually submitted", 2, race.server.puts.get())
            assertEquals("Mild", race.server.data.getString("excitement"))
        } finally {
            race.close()
        }
    }

    @Test fun failedSavePreservesNewerDraft() = runBlocking {
        val race = SaveRace()
        try {
            race.startSave()
            race.editExcitementToMild()
            // Another writer bumps the revision, so the in-flight save fails as stale.
            val other = store(race.server)
            val current = other.load()
            assertNotNull(other.save(current!!.copy(excitement = Excitement.Hype)))
            race.releaseSave()
            assertTrue(race.awaitMessage().startsWith("Save failed"))
            assertEquals("newer draft preserved on failure", Excitement.Mild, race.state.value!!.excitement)
        } finally {
            race.close()
        }
    }

    private fun screenSource(): String {
        val relative = "com/afc/companion/profile/ProfileSettingsScreen.kt"
        var dir: File? = File(System.getProperty("user.dir")).absoluteFile
        while (dir != null) {
            for (prefix in listOf("tv-app/app/src/main/java", "app/src/main/java", "src/main/java")) {
                val candidate = File(dir, "$prefix/$relative")
                if (candidate.isFile) return candidate.readText()
            }
            dir = dir.parentFile
        }
        fail("ProfileSettingsScreen.kt not found above ${System.getProperty("user.dir")}")
        error("unreachable")
    }

    /**
     * Drives the screen's actual compiled Save and Excitement callbacks against a real HTTP
     * peer whose connection is held open, mirroring the independent review reproducer.
     */
    private class SaveRace {
        val server = ProfileServer()
        private val saveEntered = CountDownLatch(1)
        private val release = CountDownLatch(1)
        private val delayConnection = AtomicBoolean(false)
        private val scope = CoroutineScope(Dispatchers.Default)
        private val client = ApiClient(server.baseUrl, { "session-fixture" }, { url ->
            if (delayConnection.get()) {
                saveEntered.countDown()
                if (!release.await(10, TimeUnit.SECONDS)) throw IllegalStateException("Network delay was not released")
            }
            url.openConnection() as HttpURLConnection
        }, {}, Dispatchers.IO)
        private val store = ProfileStore(client)
        private val before: ProfileState = runBlocking { store.load() } ?: error("Profile fixture did not load")
        val state = mutableStateOf<ProfileState?>(before)
        private val message = mutableStateOf("Profile loaded.")

        fun startSave() {
            delayConnection.set(true)
            callback("ProfileSettingsScreen\$lambda\$8\$23\$0").invoke(null, scope, store, before, state, message)
            check(saveEntered.await(10, TimeUnit.SECONDS)) { "Save did not enter transport" }
        }

        fun editExcitementToMild() {
            callback("ProfileSettingsScreen\$lambda\$8\$4\$0").invoke(null, before, state)
            check(state.value!!.excitement == Excitement.Mild) { "Excitement click did not apply" }
        }

        fun releaseSave() = release.countDown()

        fun awaitMessage(): String {
            val deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(10)
            while (message.value == "Profile loaded." && System.nanoTime() < deadline) Thread.sleep(10)
            return message.value
        }

        fun close() {
            release.countDown()
            scope.cancel()
            server.close()
        }

        private fun callback(name: String): Method =
            Class.forName("com.afc.companion.profile.ProfileSettingsScreenKt").declaredMethods
                .first { it.name == name }.apply { isAccessible = true }
    }
}

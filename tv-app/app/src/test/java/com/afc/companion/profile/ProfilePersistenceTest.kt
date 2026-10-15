package com.afc.companion.profile

import com.afc.companion.net.ApiClient
import com.afc.companion.net.ScoringPreset
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Test

/**
 * AFC-PR-002/-005/-066: selections and every control survive an app restart. A restart is a new ApiClient and
 * ProfileStore against the same backend peer, which is all the TV keeps across process death besides its token.
 */
class ProfilePersistenceTest {
    private fun store(server: ProfileServer) = ProfileStore(ApiClient(server.baseUrl, { "session-fixture" }))

    @Test fun firstLoadOfEmptyProfileIsHalfPpr() = runBlocking {
        ProfileServer().use { server ->
            val loaded = store(server).load()
            assertNotNull("Missing behavior: load decodes GET /v1/profile", loaded)
            assertEquals(ScoringPreset.HalfPpr, loaded!!.scoringPreset)
        }
    }

    @Test fun everySelectionAndControlPersistsAcrossRestart() = runBlocking {
        ProfileServer().use { server ->
            val before = store(server)
            assertNotNull(before.load())
            val saved = before.save(customized())
            assertEquals("save returns the stored profile", customized(), saved)
            assertEquals("one PUT per save", 1, server.puts.get())
            val afterRestart = store(server).load()
            assertNotNull("Missing behavior: profile reloads after restart", afterRestart)
            val expected = customized()
            assertEquals("selections", expected.selections, afterRestart!!.selections)
            assertEquals("team/league", expected.teamLeague, afterRestart.teamLeague)
            assertEquals("alert types", expected.alertTypes, afterRestart.alertTypes)
            assertEquals("frequency", expected.minGapSeconds, afterRestart.minGapSeconds)
            assertEquals("quiet hours", expected.quietHours, afterRestart.quietHours)
            assertEquals("game-day", expected.gameDay, afterRestart.gameDay)
            assertEquals("spoiler delay", expected.spoilerDelaySeconds, afterRestart.spoilerDelaySeconds)
            assertEquals("presentation", expected.presentation, afterRestart.presentation)
            assertEquals("voice", expected.voiceEnabled, afterRestart.voiceEnabled)
            assertEquals("excitement", expected.excitement, afterRestart.excitement)
            assertEquals("provider preference and overrides", expected.providerPref, afterRestart.providerPref)
            assertEquals("switching confirmation", expected.switchingConfirm, afterRestart.switchingConfirm)
            assertEquals("panel visibility", expected.panel, afterRestart.panel)
            assertEquals("detection opt-in", expected.detectionOptIn, afterRestart.detectionOptIn)
            assertEquals("scoring preset", expected.scoringPreset, afterRestart.scoringPreset)
            assertEquals(expected, afterRestart)
        }
    }

    @Test fun pprSelectionPersistsAndHalfPprReturnsAfterSwitchBack() = runBlocking {
        ProfileServer().use { server ->
            val first = store(server)
            assertNotNull(first.load())
            assertNotNull(first.save(customized().copy(scoringPreset = ScoringPreset.Ppr)))
            assertEquals("ppr", server.data.opt("scoringPreset"))
            assertEquals(ScoringPreset.Ppr, store(server).load()?.scoringPreset)
            val second = store(server)
            assertNotNull(second.load())
            assertNotNull(second.save(customized().copy(scoringPreset = ScoringPreset.HalfPpr)))
            assertEquals(ScoringPreset.HalfPpr, store(server).load()?.scoringPreset)
        }
    }

    /** AFC-PR-005: a detection refresh after restart never discards the customer's override or local market. */
    @Test fun overrideSurvivesRestartAndDetectionRefresh() = runBlocking {
        ProfileServer().use { server ->
            val first = store(server)
            assertNotNull(first.load())
            assertNotNull(first.save(customized()))
            val reloaded = store(server).load()
            assertNotNull(reloaded)
            val refreshed = setOf("com.example.provider.a", "com.example.provider.b")
            assertEquals(setOf("com.example.provider.b", "com.example.provider.c"), reloaded!!.effectiveInstalled(refreshed))
            assertEquals(reloaded.effectiveInstalled(refreshed), reloaded.effectiveInstalled(refreshed + "com.example.provider.a"))
            assertEquals("market-501", reloaded.providerPref.localMarket)
        }
    }

    /** CONTRACT-AFC-P2-ENVELOPE: a save over a stale revision is not silently forced onto the newer profile. */
    @Test fun staleSaveDoesNotOverwriteNewerProfile() = runBlocking {
        ProfileServer().use { server ->
            val deviceA = store(server)
            val deviceB = store(server)
            assertNotNull(deviceA.load()); assertNotNull(deviceB.load())
            val newer = customized().copy(excitement = Excitement.Mild)
            assertEquals(newer, deviceB.save(newer))
            assertNull("stale save reports failure", deviceA.save(customized().copy(excitement = Excitement.Off)))
            assertEquals(newer, store(server).load())
        }
    }

    /** Persisted settings are untrusted: an invalid stored profile is not applied as if valid. */
    @Test fun invalidStoredProfileIsNotApplied() = runBlocking {
        ProfileServer(JSONObject().put("excitement", 12345).put("frequency", "ludicrous")).use { server ->
            assertNull(store(server).load())
        }
        ProfileServer(JSONObject().put("scoringPreset", "standard")).use { server ->
            assertNull("no third preset is accepted", store(server).load())
        }
    }
}

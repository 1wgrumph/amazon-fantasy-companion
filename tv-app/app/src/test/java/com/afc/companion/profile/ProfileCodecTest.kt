package com.afc.companion.profile

import com.afc.companion.net.ScoringPreset
import com.afc.companion.net.Settings
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertThrows
import org.junit.Test

/** PROFILE settings codec: every control round-trips through its frozen Settings field (openapi.yaml Settings). */
class ProfileCodecTest {
    private fun roundTrip(state: ProfileState): ProfileState? =
        Settings.from(ProfileCodec.encode(state).toJson())?.let(ProfileCodec::decode)

    @Test fun emptySettingsDecodeToDocumentedDefaults() {
        val defaults = ProfileCodec.decode(Settings.from(JSONObject())!!)
        assertNotNull("Missing behavior: empty persisted settings decode to defaults", defaults)
        assertEquals("AFC-PR-066 default preset", ScoringPreset.HalfPpr, defaults!!.scoringPreset)
        assertEquals("alert_min_gap default", 120, defaults.minGapSeconds)
        assertEquals("spoiler_delay default", 0, defaults.spoilerDelaySeconds)
        assertEquals("AFC-PR-035 confirmation is on by default", true, defaults.switchingConfirm)
        assertEquals("AFC-PR-037 detection is opt-in", false, defaults.detectionOptIn)
        assertEquals("AFC-PR-022 voice is off by default", false, defaults.voiceEnabled)
    }

    @Test fun everyControlRoundTrips() {
        val state = customized()
        val decoded = roundTrip(state)
        assertNotNull("Missing behavior: encoded settings decode", decoded)
        assertEquals(state, decoded)
    }

    @Test fun eachExcitementLevelRoundTrips() {
        assertEquals("excitement_levels are exactly Off / Mild / Hype", listOf("Off", "Mild", "Hype"), Excitement.entries.map { it.name })
        for (level in Excitement.entries) assertEquals(level, roundTrip(customized().copy(excitement = level))?.excitement)
    }

    @Test fun eachScoringPresetRoundTripsWithFrozenWire() {
        assertEquals("no third preset", listOf(ScoringPreset.Ppr, ScoringPreset.HalfPpr), ScoringPreset.entries.toList())
        for (preset in ScoringPreset.entries) {
            val state = customized().copy(scoringPreset = preset)
            assertEquals(preset.wire, ProfileCodec.encode(state).toJson().opt("scoringPreset"))
            assertEquals(preset, roundTrip(state)?.scoringPreset)
        }
    }

    @Test fun eachPresentationRoundTrips() {
        for (choice in Presentation.entries) assertEquals(choice, roundTrip(customized().copy(presentation = choice))?.presentation)
    }

    /** Each control lives in its own Settings field, which the backend policy reads; changing one changes only that field. */
    @Test fun eachControlWritesOnlyItsOwnSettingsField() {
        val base = customized()
        val changes = mapOf(
            "fantasySelections" to base.copy(selections = base.selections.copy(players = setOf("player-99"))),
            "teamLeague" to base.copy(teamLeague = TeamLeague("league-b", "team-2")),
            "alertTypes" to base.copy(alertTypes = setOf(AlertType.PlayerScore)),
            "frequency" to base.copy(minGapSeconds = 600),
            "quietHours" to base.copy(quietHours = listOf(TimeWindow(0, 360))),
            "gameDayPeriods" to base.copy(gameDay = GameDayMode(false, base.gameDay.periods)),
            "spoilerDelay" to base.copy(spoilerDelaySeconds = 120),
            "presentation" to base.copy(presentation = Presentation.HeadsUp),
            "voice" to base.copy(voiceEnabled = false),
            "excitement" to base.copy(excitement = Excitement.Mild),
            "providerPref" to base.copy(providerPref = base.providerPref.copy(order = listOf("provider-a", "provider-b"))),
            "switchingConfirm" to base.copy(switchingConfirm = true),
            "panelPrefs" to base.copy(panel = PanelPrefs(true)),
            "detectionOptIn" to base.copy(detectionOptIn = false),
            "scoringPreset" to base.copy(scoringPreset = ScoringPreset.HalfPpr),
        )
        assertEquals("every Settings field has a control", Settings.CONTROLS + "scoringPreset", changes.keys)
        val before = ProfileCodec.encode(base).toJson()
        for ((field, changed) in changes) {
            val after = ProfileCodec.encode(changed).toJson()
            val differing = (before.keys().asSequence().toSet() + after.keys().asSequence().toSet()).filter { before.opt(it)?.toString() != after.opt(it)?.toString() }
            assertEquals("changing $field rewrites only $field", listOf(field), differing)
        }
    }

    @Test fun overridesAndLocalMarketRoundTrip() {
        val pref = customized().providerPref
        val decoded = roundTrip(customized())
        assertEquals(pref.appOverrides, decoded?.providerPref?.appOverrides)
        assertEquals("market-501", decoded?.providerPref?.localMarket)
    }

    /** Persisted settings are untrusted input: a wrong-typed control is rejected whole, never partially applied. */
    @Test fun wrongTypedControlIsRejected() {
        val valid = ProfileCodec.encode(customized()).toJson()
        for (field in Settings.CONTROLS) {
            val bad: Any = if (valid.opt(field) is String) 12345 else "ludicrous"
            val settings = Settings.from(JSONObject(valid.toString()).put(field, bad))
            assertNotNull(settings)
            assertNull("$field=$bad must be rejected", ProfileCodec.decode(settings!!))
        }
    }

    @Test fun outOfRangeValuesCannotBeEncoded() {
        val base = customized()
        assertThrows("alert_min_gap above 600 s", IllegalArgumentException::class.java) { ProfileCodec.encode(base.copy(minGapSeconds = 601)) }
        assertThrows("negative alert_min_gap", IllegalArgumentException::class.java) { ProfileCodec.encode(base.copy(minGapSeconds = -1)) }
        assertThrows("spoiler_delay above 120 s", IllegalArgumentException::class.java) { ProfileCodec.encode(base.copy(spoilerDelaySeconds = 121)) }
        assertThrows("minute of day above 1439", IllegalArgumentException::class.java) { ProfileCodec.encode(base.copy(quietHours = listOf(TimeWindow(0, 1440)))) }
        val boundary = base.copy(minGapSeconds = 600, spoilerDelaySeconds = 120, quietHours = listOf(TimeWindow(0, 1439)))
        assertEquals("boundary values are accepted", boundary, roundTrip(boundary))
    }
}

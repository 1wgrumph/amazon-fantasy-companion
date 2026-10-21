package com.afc.companion.profile

import com.afc.companion.BuildConfig
import com.afc.companion.net.Settings
import java.io.File
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test

// M16 NBA stretch (#137): per-sport notification toggle behind AFC_ENABLE_NBA.
// Contract for the Implementer:
// - enum Sport(wire, label) { Nfl("nfl", "NFL"), Nba("nba", "NBA") } in this package.
// - ProfileState.sportEnabled(sport): a sport never toggled is on (NFL on; NBA on when the flag is on).
// - ProfileState.toggledSport(sport) in ProfileEdits.kt flips one sport.
// - sportToggles(state, nbaEnabled): the screen's toggle rows, (Sport, "<label> alerts: on|off"); empty with the flag off.
// - Settings field "sports" = {"nfl": bool, "nba": bool}; encode writes it only once a sport was toggled, so an
//   untoggled profile encodes as today. Settings.from(json, nbaEnabled = BuildConfig.AFC_ENABLE_NBA) accepts it only
//   with the flag on; decode rejects a malformed value whole. Settings.CONTROLS and ProfileControl stay unchanged, so
//   the frozen openapi Settings contract and the existing control tests hold with the flag off.

/** Per-sport notification toggle: defaults on, flips one sport, round-trips, and is invisible with the flag off. */
class SportToggleTest {
    private fun decodeOn(json: JSONObject): ProfileState? = Settings.from(json, nbaEnabled = true)?.let(ProfileCodec::decode)

    @Test fun sportsDefaultOn() {
        assertTrue("NFL defaults on", customized().sportEnabled(Sport.Nfl))
        assertTrue("NBA defaults on", customized().sportEnabled(Sport.Nba))
        val empty = decodeOn(JSONObject())
        assertNotNull(empty)
        assertTrue(empty!!.sportEnabled(Sport.Nfl) && empty.sportEnabled(Sport.Nba))
        val partial = decodeOn(JSONObject().put("sports", JSONObject().put("nba", false)))
        assertNotNull("a missing sport key is allowed", partial)
        assertTrue("a missing sport key defaults on", partial!!.sportEnabled(Sport.Nfl))
        assertFalse(partial.sportEnabled(Sport.Nba))
    }

    @Test fun sportWireAndLabelsAreFixed() {
        assertEquals(listOf("nfl", "nba"), Sport.entries.map { it.wire })
        assertEquals(listOf("NFL", "NBA"), Sport.entries.map { it.label })
    }

    @Test fun togglingFlipsOnlyThatSport() {
        val nbaOff = customized().toggledSport(Sport.Nba)
        assertFalse(nbaOff.sportEnabled(Sport.Nba))
        assertTrue(nbaOff.sportEnabled(Sport.Nfl))
        val nflOff = customized().toggledSport(Sport.Nfl)
        assertFalse(nflOff.sportEnabled(Sport.Nfl))
        assertTrue(nflOff.sportEnabled(Sport.Nba))
        assertTrue("toggling twice turns it back on", nbaOff.toggledSport(Sport.Nba).sportEnabled(Sport.Nba))
    }

    @Test fun screenRowsWithTheFlagOn() {
        assertEquals(listOf(Sport.Nfl to "NFL alerts: on", Sport.Nba to "NBA alerts: on"), sportToggles(customized(), nbaEnabled = true))
        assertEquals(listOf(Sport.Nfl to "NFL alerts: on", Sport.Nba to "NBA alerts: off"),
            sportToggles(customized().toggledSport(Sport.Nba), nbaEnabled = true))
        assertEquals(listOf(Sport.Nfl to "NFL alerts: off", Sport.Nba to "NBA alerts: on"),
            sportToggles(customized().toggledSport(Sport.Nfl), nbaEnabled = true))
    }

    @Test fun toggledSportsEncodeAndRoundTrip() {
        val state = customized().toggledSport(Sport.Nba)
        val json = ProfileCodec.encode(state).toJson()
        val sports = json.optJSONObject("sports")
        assertNotNull("Missing behavior: a toggled sport is written to Settings.sports", sports)
        assertEquals(setOf("nfl", "nba"), sports!!.keys().asSequence().toSet())
        assertEquals(true, sports.get("nfl"))
        assertEquals(false, sports.get("nba"))
        val decoded = decodeOn(json)
        assertEquals(state, decoded)
        assertFalse(decoded!!.sportEnabled(Sport.Nba))
    }

    @Test fun aSportToggleRewritesOnlyTheSportsField() {
        val before = ProfileCodec.encode(customized()).toJson()
        val after = ProfileCodec.encode(customized().toggledSport(Sport.Nfl)).toJson()
        val differing = (before.keys().asSequence().toSet() + after.keys().asSequence().toSet())
            .filter { before.opt(it)?.toString() != after.opt(it)?.toString() }
        assertEquals(listOf("sports"), differing)
    }

    @Test fun malformedSportsIsRejectedWhole() {
        val bad = listOf<Any>(
            JSONObject().put("mlb", true), JSONObject().put("nba", "off"), JSONObject().put("nba", 1),
            JSONObject().put("nfl", JSONObject.NULL), JSONArray().put("nfl"), "nfl", JSONObject.NULL,
        )
        for (value in bad) {
            val json = ProfileCodec.encode(customized()).toJson().put("sports", value)
            assertNull("sports=$value must be rejected", decodeOn(json))
        }
    }

    // Flag off: no toggle shown or accepted; profile behavior byte-identical to today.

    @Test fun flagOffShowsNoSportToggle() {
        assertEquals(emptyList<Pair<Sport, String>>(), sportToggles(customized(), nbaEnabled = false))
        assertEquals(emptyList<Pair<Sport, String>>(), sportToggles(customized().toggledSport(Sport.Nba), nbaEnabled = false))
        assertTrue("the control list is unchanged", ProfileControl.entries.none { "Sport" in it.name })
        assertFalse("Settings.CONTROLS stays the frozen openapi set", "sports" in Settings.CONTROLS)
    }

    @Test fun flagOffRejectsSportsAndEncodesAsToday() {
        val today = ProfileCodec.encode(customized()).toJson()
        assertFalse("an untoggled profile writes no sports field", today.has("sports"))
        assertEquals(today.toString(), Settings.from(today, nbaEnabled = false)!!.toJson().toString())
        assertEquals(customized(), Settings.from(today, nbaEnabled = false)?.let(ProfileCodec::decode))
        val withSports = JSONObject(today.toString()).put("sports", JSONObject().put("nfl", true).put("nba", true))
        assertNull("flag off: sports is an unknown Settings field", Settings.from(withSports, nbaEnabled = false))
    }

    @Test fun defaultSettingsDecodeFollowsTheBuildFlag() {
        assertFalse(BuildConfig.AFC_ENABLE_NBA)
        val withSports = ProfileCodec.encode(customized()).toJson().put("sports", JSONObject().put("nba", false))
        assertNull("the default Settings.from follows AFC_ENABLE_NBA", Settings.from(withSports))
        assertNotNull(Settings.from(withSports, nbaEnabled = true))
    }

    /**
     * The screen renders sportToggles as Buttons; the only raw text field stays inside the #129 D-pad helper
     * ProfileTextField, so the new controls cannot reintroduce the focus trap BUG-A02-1 fixed.
     */
    @Test fun screenRendersSportTogglesWithoutANewTextField() {
        val source = screenSource()
        assertTrue("Missing behavior: ProfileSettingsScreen renders sportToggles(...)", "sportToggles(" in source)
        assertEquals("BasicTextField is used only inside ProfileTextField (#129)", 1, Regex("""\bBasicTextField\(""").findAll(source).count())
        assertTrue("the #129 helper is still present", "private fun ProfileTextField(" in source)
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
}

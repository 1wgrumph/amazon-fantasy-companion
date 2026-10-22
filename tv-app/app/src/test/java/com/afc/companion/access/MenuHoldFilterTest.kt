package com.afc.companion.access

import android.view.KeyEvent
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** Shared hold: every key reaches the playing app; AFC observes each hold once. */
class MenuHoldFilterTest {
    private var holds = 0
    private val filter = MenuHoldFilter { holds++ }
    private val down = KeyEvent.ACTION_DOWN
    private val up = KeyEvent.ACTION_UP
    private val menu = KeyEvent.KEYCODE_MENU

    @Test fun holdIsSevenHundredMilliseconds() {
        assertEquals(700L, MenuHoldFilter.HOLD_MS)
    }

    @Test fun shortMenuPressPassesThroughUntouched() {
        assertFalse("down passes", filter.onKey(menu, down, 0, 1_000))
        filter.onHoldTimeout(1_300) // an early timer must not fire
        assertFalse("up passes", filter.onKey(menu, up, 0, 1_300))
        assertEquals(0, holds)
    }

    @Test fun pressJustUnderTheHoldPassesItsUp() {
        assertFalse(filter.onKey(menu, down, 0, 0))
        assertFalse("pre-threshold repeat passes", filter.onKey(menu, down, 1, 500))
        assertFalse("released at 699 ms: the app still sees down and up", filter.onKey(menu, up, 0, 699))
        assertEquals(0, holds)
    }

    @Test fun longMenuPressFiresOnceWhileEveryEventPassesThrough() {
        assertFalse("the down cannot be known as long yet, so it passes", filter.onKey(menu, down, 0, 10_000))
        filter.onHoldTimeout(10_700)
        assertEquals("fires at 700 ms, before release", 1, holds)
        assertFalse("repeat passes", filter.onKey(menu, down, 1, 10_750))
        assertFalse("repeat passes", filter.onKey(menu, down, 2, 10_800))
        filter.onHoldTimeout(10_900)
        assertFalse("up passes", filter.onKey(menu, up, 0, 11_200))
        assertEquals("one hold, one action", 1, holds)
    }

    @Test fun lateTimerStillFiresFromTheRepeatOrTheUp() {
        filter.onKey(menu, down, 0, 0)
        assertFalse(filter.onKey(menu, down, 5, 720))
        assertEquals(1, holds)
        assertFalse(filter.onKey(menu, up, 0, 900))

        filter.onKey(menu, down, 0, 5_000)
        assertFalse("held 800 ms without any timer or repeat", filter.onKey(menu, up, 0, 5_800))
        assertEquals(2, holds)
    }

    @Test fun exactThresholdAndLongPressFlagFireOnceWithoutConsuming() {
        assertFalse(filter.onKey(menu, down, 0, 0))
        filter.onHoldTimeout(699)
        assertEquals(0, holds)
        assertFalse(filter.onKey(menu, up, 0, 700))
        filter.onHoldTimeout(900)
        assertEquals(1, holds)

        assertFalse(filter.onKey(menu, down, 0, 2_000))
        assertFalse(filter.onKey(menu, down, 1, 2_500, isLongPress = true))
        assertEquals("platform long-press flag is authoritative", 2, holds)
        assertFalse(filter.onKey(menu, down, 2, 2_800, isLongPress = true))
        assertFalse(filter.onKey(menu, up, 0, 2_900))
        filter.onHoldTimeout(3_000)
        assertEquals("flag and timeout cannot double-handle", 2, holds)
    }

    @Test fun nextShortPressAfterAHoldPassesAgain() {
        filter.onKey(menu, down, 0, 0)
        filter.onHoldTimeout(700)
        filter.onKey(menu, up, 0, 900)
        assertFalse(filter.onKey(menu, down, 0, 2_000))
        assertFalse(filter.onKey(menu, up, 0, 2_100))
        assertEquals(1, holds)
    }

    @Test fun otherKeysAreNeverConsumedEvenWhileMenuIsHeld() {
        val keys = listOf(
            KeyEvent.KEYCODE_BACK, KeyEvent.KEYCODE_HOME, KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_DPAD_UP,
            KeyEvent.KEYCODE_DPAD_DOWN, KeyEvent.KEYCODE_DPAD_LEFT, KeyEvent.KEYCODE_DPAD_RIGHT,
            KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE, KeyEvent.KEYCODE_MEDIA_FAST_FORWARD, KeyEvent.KEYCODE_MEDIA_REWIND,
            KeyEvent.KEYCODE_VOLUME_UP, KeyEvent.KEYCODE_ENTER,
        )
        for (key in keys) {
            assertFalse("$key down", filter.onKey(key, down, 0, 0))
            assertFalse("$key repeat", filter.onKey(key, down, 3, 900))
            assertFalse("$key up", filter.onKey(key, up, 0, 1_000))
        }
        filter.onKey(menu, down, 0, 2_000)
        filter.onHoldTimeout(2_700)
        for (key in keys) assertFalse("$key during a hold", filter.onKey(key, down, 0, 2_800))
        assertEquals(1, holds)
    }

    @Test fun repeatWithoutASeenDownPassesBecauseItsDownReachedTheAppUnfiltered() {
        assertFalse(filter.onKey(menu, down, 4, 1_000))
        assertFalse(filter.onKey(menu, up, 0, 1_200))
        assertEquals(0, holds)
    }

    @Test fun resetDropsAHalfSeenHold() {
        filter.onKey(menu, down, 0, 0)
        filter.reset()
        filter.onHoldTimeout(800)
        assertFalse(filter.onKey(menu, up, 0, 900))
        assertEquals(0, holds)
    }

    private var taps = 0
    private val tapFilter = MenuHoldFilter(onDoubleTap = { taps++ }, onHold = { holds++ })

    private fun press(downMs: Long, upMs: Long) {
        assertFalse("down passes", tapFilter.onKey(menu, down, 0, downMs))
        tapFilter.onHoldTimeout(upMs)
        assertFalse("up passes", tapFilter.onKey(menu, up, 0, upMs))
    }

    @Test fun twoShortPressesWithin400MillisecondsAreADoubleTap() {
        press(0, 100)
        assertEquals("one press is not a double-tap", 0, taps)
        press(500, 600) // second down 400 ms after the first up
        assertEquals(1, taps)
        assertEquals("a double-tap is not a hold", 0, holds)
        press(700, 800)
        assertEquals("a third press starts a new pair", 1, taps)
    }

    @Test fun pressesFiveHundredMillisecondsApartAreNotADoubleTap() {
        press(0, 100)
        press(600, 700)
        assertEquals(0, taps)
    }

    @Test fun resetDropsTheFirstTapAndTheNextPressStartsFresh() {
        press(0, 100)
        tapFilter.reset()
        press(200, 300)
        assertEquals("one press after a service reset is not a double-tap", 0, taps)
        press(400, 500)
        assertEquals("two presses after reset still form a double-tap", 1, taps)
        assertEquals(0, holds)
    }

    @Test fun aHoldIsNeverPartOfADoubleTap() {
        press(0, 100)
        press(300, 1_100) // held 800 ms
        assertEquals(1, holds)
        assertEquals(0, taps)
        press(1_200, 1_300)
        assertEquals("a short press right after a hold starts fresh", 0, taps)
    }

    @Test fun serviceOffFallbackReadsTheSecureSettingList() {
        assertFalse("no services", MenuHold.enabled(null))
        assertFalse(MenuHold.enabled(""))
        assertFalse("another app only", MenuHold.enabled("com.other/.Svc"))
        assertFalse("prefix is not a match", MenuHold.enabled("com.afc.companion/.access.MenuHoldServiceX"))
        assertTrue(MenuHold.enabled("com.afc.companion/com.afc.companion.access.MenuHoldService"))
        assertTrue(MenuHold.enabled("com.other/.Svc:com.afc.companion/.access.MenuHoldService"))
    }
}

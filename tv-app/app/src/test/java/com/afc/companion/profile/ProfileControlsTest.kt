package com.afc.companion.profile

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** Every profile control is offered; a control whose platform route is unsupported is hidden with a stated limit (P2-X07 rule). */
class ProfileControlsTest {
    @Test fun everyControlIsOfferedWhenRoutesAreSupported() {
        val controls = profileControls(detectionSupported = true, voiceRouteVerified = true)
        assertEquals(ProfileControl.entries.toSet(), controls.visible.toSet())
        assertEquals("no control listed twice", controls.visible.size, controls.visible.toSet().size)
        assertTrue(controls.limits.isEmpty())
    }

    @Test fun unsupportedDetectionHidesItsControlWithStatedLimit() {
        val controls = profileControls(detectionSupported = false, voiceRouteVerified = true)
        assertFalse(ProfileControl.DetectionOptIn in controls.visible)
        assertTrue("stated limit for hidden detection", controls.limits[ProfileControl.DetectionOptIn].orEmpty().isNotBlank())
        assertEquals(ProfileControl.entries.toSet() - ProfileControl.DetectionOptIn, controls.visible.toSet())
    }

    @Test fun unverifiedVoiceRouteHidesVoiceWithStatedLimit() {
        val controls = profileControls(detectionSupported = true, voiceRouteVerified = false)
        assertFalse(ProfileControl.Voice in controls.visible)
        assertTrue("stated limit for hidden voice", controls.limits[ProfileControl.Voice].orEmpty().isNotBlank())
        assertEquals(ProfileControl.entries.toSet() - ProfileControl.Voice, controls.visible.toSet())
    }

    /** AFC-PR-022: voice speaks only while enabled over a verified route. */
    @Test fun voiceGateNeedsBothEnablementAndVerifiedRoute() {
        assertTrue("enabled over a verified route speaks", customized().copy(voiceEnabled = true).voiceActive(routeVerified = true))
        assertFalse(customized().copy(voiceEnabled = true).voiceActive(routeVerified = false))
        assertFalse(customized().copy(voiceEnabled = false).voiceActive(routeVerified = true))
        assertFalse(customized().copy(voiceEnabled = false).voiceActive(routeVerified = false))
    }

    /** AFC-PR-005: the customer's review wins in both directions; unreviewed apps follow detection. */
    @Test fun customerOverrideWinsOverDetection() {
        val state = customized()
        assertEquals(setOf("com.example.provider.b", "com.example.provider.c"),
            state.effectiveInstalled(setOf("com.example.provider.a", "com.example.provider.b")))
        assertEquals(setOf("com.example.provider.c"), state.effectiveInstalled(emptySet()))
    }
}

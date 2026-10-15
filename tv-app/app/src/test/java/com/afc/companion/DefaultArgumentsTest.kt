package com.afc.companion

import com.afc.companion.net.ApiClient
import com.afc.companion.net.Profile
import com.afc.companion.net.ScoringPreset
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Test

/** Default-argument entry points: getPanel() and Profile.from(json) with no held revision. */
class DefaultArgumentsTest {
    @Test fun panelWithoutTeamOrRevisionHitsBarePathAndAcceptsAnyRevision() {
        LocalApi(listOf(200 to envelopeFixture(0).toString())).use { server ->
            val panel = runBlocking { ApiClient(server.baseUrl, { "t" }).getPanel() }
            assertEquals("/v1/panel", server.requests.single().path)
            assertEquals(0L, panel.value!!.envelope.revision)
        }
    }

    @Test fun profileFromWithoutHeldRevisionDecodesAndRejectsBadEnvelope() {
        val profile = Profile.from(envelopeFixture(0))!!
        assertEquals(0L, profile.envelope.revision)
        assertEquals(ScoringPreset.HalfPpr, profile.settings.scoringPreset)
        assertNull(Profile.from(envelopeFixture().put("schemaVersion", 2)))
    }
}

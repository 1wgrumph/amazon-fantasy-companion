package com.afc.companion.alerts

import com.afc.companion.profile.Presentation
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * DES-AFC-P2-ALERTPATH NOTIFIER: the customer's presentation (AFC-PR-015, -021), alert text with the triggering
 * context (AFC-PR-027) and no red-zone over-claim (AFC-PR-028), unknown access shown as unknown (AFC-PR-032, -033),
 * and voice only while enabled over a verified route (AFC-PR-022). Alert payloads are untrusted backend data.
 */
class AlertPresenterTest {
    private val overClaim = Regex(
        "(?i)on the field|on-field|will score|going to score|about to score|is scoring|set to score|sure to score|guaranteed",
    )

    // An access label may say "not verified"; it may never claim verification, inclusion or a subscription.
    private val accessClaim = Regex("(?i)\\binclud(ed|es)\\b|\\bsubscribed\\b|(?<!not )\\bverified\\b")

    private fun text(data: org.json.JSONObject = alertData()): AlertText {
        val text = AlertPresenter.text(alert(data))
        assertNotNull("Missing behavior: alert text rendered", text)
        return text!!
    }

    @Test fun headsUpSelectionShowsWatchAndDismiss() {
        val view = AlertPresenter.view(alert(), profile(Presentation.HeadsUp))
        assertNotNull("Missing behavior: alert view rendered", view)
        assertEquals(Presentation.HeadsUp, view!!.presentation)
        assertEquals(listOf(AlertAction.Watch, AlertAction.Dismiss), view.actions)
    }

    @Test fun panelOnlySelectionShowsNoHeadsUp() {
        val view = AlertPresenter.view(alert(), profile(Presentation.PanelOnly))
        assertNotNull("Missing behavior: alert view rendered", view)
        assertEquals(Presentation.PanelOnly, view!!.presentation)
        assertEquals("panel-only carries no heads-up actions", emptyList<AlertAction>(), view.actions)
    }

    @Test fun textCarriesTheTriggeringPlayerAndMatchup() {
        val text = text()
        assertTrue("player in context: ${text.context}", PLAYER in text.context)
        assertTrue("matchup in context: ${text.context}", MATCHUP in text.context)
    }

    @Test fun alertWithoutTriggeringContextIsNotRendered() {
        assertNull("no player", AlertPresenter.text(alert(alertData(player = null))))
        assertNull("no matchup", AlertPresenter.text(alert(alertData(matchup = null))))
        assertNull("blank player", AlertPresenter.text(alert(alertData(player = " "))))
    }

    @Test fun redZoneTextMakesNoOnFieldOrWillScoreClaim() {
        val text = text(alertData(type = "redZone"))
        assertFalse("over-claim in: ${text.all()}", overClaim.containsMatchIn(text.all()))
    }

    @Test fun redZoneCommentaryClaimingAPlayerWillScoreIsNotShown() {
        val text = text(alertData(type = "redZone", commentary = "$PLAYER is on the field and will score!"))
        assertTrue("context still shown", PLAYER in text.context)
        assertFalse("over-claim in: ${text.all()}", overClaim.containsMatchIn(text.all()))
    }

    @Test fun unknownAccessReadsUnknownAndPromisesNothing() {
        for (data in listOf(alertData(route = null), alertData(route = route("unknown")), alertData(route = route("unknown", provider = null)))) {
            val access = text(data).access
            assertTrue("unknown access label: $access", Regex("(?i)\\bunknown\\b").containsMatchIn(access))
            assertFalse("no inclusion promise: $access", accessClaim.containsMatchIn(access))
        }
    }

    @Test fun customerConfirmedAccessIsNotShownAsVerified() {
        val access = text(alertData(route = route("customerConfirmed"))).access
        assertTrue("access label rendered", access.isNotBlank())
        assertFalse("unverified access reads verified or included: $access", accessClaim.containsMatchIn(access))
    }

    @Test fun verifiedAccessIsNotShownAsUnknown() {
        val access = text(alertData(route = route("verified"))).access
        assertTrue("access label rendered", access.isNotBlank())
        assertFalse("verified access reads unknown: $access", Regex("(?i)\\bunknown\\b").containsMatchIn(access))
    }

    @Test fun voiceSpeaksOnlyWhenEnabledOverAVerifiedRoute() {
        val speaks = AlertPresenter.view(alert(), profile(voice = true), voiceRouteVerified = true)
        assertNotNull("Missing behavior: alert view rendered", speaks)
        assertTrue("enabled over a verified route speaks", speaks!!.speak)
        val disabled = AlertPresenter.view(alert(), profile(voice = false), voiceRouteVerified = true)
        assertNotNull(disabled)
        assertFalse("disabled stays silent", disabled!!.speak)
    }

    @Test fun voiceStaysOffWithoutAVerifiedRoute() {
        val unverified = AlertPresenter.view(alert(), profile(voice = true), voiceRouteVerified = false)
        assertNotNull("Missing behavior: alert view rendered", unverified)
        assertFalse("unverified route stays silent", unverified!!.speak)
        val shipped = AlertPresenter.view(alert(), profile(voice = true))
        assertNotNull(shipped)
        assertFalse("no verified voice route ships (P2-X11 absent)", shipped!!.speak)
    }
}

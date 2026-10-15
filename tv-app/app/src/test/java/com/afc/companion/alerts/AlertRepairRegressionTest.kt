package com.afc.companion.alerts

import com.afc.companion.net.Alert
import com.afc.companion.net.Envelope
import com.afc.companion.profile.Presentation
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** A03 repair regressions (R01/R03): hostile untrusted text and colliding alert identities. */
class AlertRepairRegressionTest {
    private val overClaim = Regex(
        "(?i)on the field|on-field|will score|going to score|about to score|is scoring|set to score|sure to score|guaranteed",
    )

    @Test fun unsafePlayerClaimIsNotRendered() {
        assertNull(
            "on-field/will-score player must not reach display",
            AlertPresenter.text(alert(alertData(player = "Player Eleven is on the field and will score"))),
        )
    }

    @Test fun unsafeMatchupClaimIsNotRendered() {
        assertNull(
            "will-score matchup must not reach display",
            AlertPresenter.text(alert(alertData(matchup = "KC at BUF — guaranteed to score"))),
        )
    }

    @Test fun whitespaceVariantCommentaryClaimIsDroppedButContextKept() {
        for (commentary in listOf("Player Eleven will  score!", "Player Eleven will\tscore!", "Player Eleven on  the   field")) {
            val text = AlertPresenter.text(alert(alertData(commentary = commentary)))
            assertNotNull("valid context still rendered for: $commentary", text)
            assertTrue("player in context", PLAYER in text!!.context)
            assertNull("unsafe commentary dropped: $commentary", text.commentary)
            assertFalse("over-claim in: ${text.all()}", overClaim.containsMatchIn(text.all()))
        }
    }

    @Test fun hyphenVariantCommentaryClaimIsDropped() {
        val text = AlertPresenter.text(alert(alertData(commentary = "Player Eleven is on-the-field")))
        assertNotNull(text)
        assertNull("hyphenated on-field claim dropped", text!!.commentary)
    }

    @Test fun benignTextStillRendered() {
        val text = AlertPresenter.text(alert(alertData(commentary = "Offense inside the twenty.")))
        assertNotNull(text)
        assertTrue(PLAYER in text!!.context)
        assertTrue(MATCHUP in text.context)
        assertTrue("benign commentary kept", "Offense inside the twenty." == text.commentary)
    }

    @Test fun collidingHashAlertIdsGetDistinctNotificationIds() {
        assertNotEquals(
            "Aa and BB share String.hashCode but must not share a notification id",
            AlertNotifier.notificationId("Aa"),
            AlertNotifier.notificationId("BB"),
        )
    }

    @Test fun collidingHashAlertIdsGetDistinctTagsRequestCodesAndActionData() {
        assertNotEquals(AlertNotifier.notificationTag("Aa"), AlertNotifier.notificationTag("BB"))
        assertNotEquals(AlertNotifier.requestCode("Aa", 1), AlertNotifier.requestCode("BB", 1))
        assertNotEquals(AlertNotifier.requestCode("Aa", 2), AlertNotifier.requestCode("BB", 2))
        assertNotEquals(AlertNotifier.actionData("Aa", "watch"), AlertNotifier.actionData("BB", "watch"))
        assertNotEquals(AlertNotifier.actionData("Aa", "dismiss"), AlertNotifier.actionData("BB", "dismiss"))
        assertNotEquals("watch and dismiss differ", AlertNotifier.actionData("Aa", "watch"), AlertNotifier.actionData("Aa", "dismiss"))
        // Stable for the same alert so post/update/cancel address one notification.
        assertTrue(AlertNotifier.notificationId("Aa") == AlertNotifier.notificationId("Aa"))
        assertTrue(AlertNotifier.requestCode("Aa", 1) == AlertNotifier.requestCode("Aa", 1))
    }
}

/** A03-R02: a failed profile lookup must never fall through to heads-up delivery. */
class PresentationGateTest {
    private fun alertWithId(id: String): Alert =
        checkNotNull(Envelope.from(alertJson(id))?.let(Alert::from)) { "fixture must decode" }

    private fun ids(alerts: List<Alert>): List<String> = alerts.map { it.envelope.id }

    @Test fun failedLookupAfterPanelOnlyDeliversNothing() {
        val gate = PresentationGate()
        assertEquals(emptyList<String>(), ids(gate.drain(listOf(alertWithId("a1")), profile(Presentation.PanelOnly))))
        assertEquals(
            "null profile retains validated PanelOnly, never heads-up",
            emptyList<String>(),
            ids(gate.drain(listOf(alertWithId("a2")), null)),
        )
        assertFalse(gate.hasPending())
    }

    @Test fun unknownPresentationDefersThenHeadsUpDeliversPending() {
        val gate = PresentationGate()
        assertEquals(emptyList<String>(), ids(gate.drain(listOf(alertWithId("a1")), null)))
        assertTrue(gate.hasPending())
        assertEquals(
            "deferred alert is not lost once settings recover as heads-up",
            listOf("a1", "a2"),
            ids(gate.drain(listOf(alertWithId("a2")), profile(Presentation.HeadsUp))),
        )
        assertFalse(gate.hasPending())
    }

    @Test fun failedLookupAfterHeadsUpRetainsHeadsUp() {
        val gate = PresentationGate()
        assertEquals(listOf("a1"), ids(gate.drain(listOf(alertWithId("a1")), profile(Presentation.HeadsUp))))
        assertEquals(listOf("a2"), ids(gate.drain(listOf(alertWithId("a2")), null)))
    }

    @Test fun panelOnlyRecoveryDoesNotLaterHeadsUpStalePending() {
        val gate = PresentationGate()
        gate.drain(listOf(alertWithId("a1")), null)
        assertEquals(emptyList<String>(), ids(gate.drain(emptyList(), profile(Presentation.PanelOnly))))
        assertEquals(listOf("a2"), ids(gate.drain(listOf(alertWithId("a2")), profile(Presentation.HeadsUp))))
    }
}

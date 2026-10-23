package com.afc.companion.panel

import com.afc.companion.ui.theme.productSource
import com.afc.companion.ui.theme.sourceBlock
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** Separate card window, shared private inbox, no player/network control. Actual playback needs device proof. */
class AlertCardIntegrationContractTest {
    private fun cardHost() = overlaySource("panel/AlertCardOverlay.kt")

    @Test fun monitoringStartsTheCardHostWithoutShowingTheSidePanel() {
        val service = overlaySource("panel/OverlayService.kt")
        val monitor = sourceBlock(productSource("alerts/AlertService.kt"), Regex("fun\\s+onStartCommand\\s*\\("))
        assertTrue("monitoring starts cards even if the panel was never opened", monitor.contains("OverlayServiceControl(this).startAlerts()"))
        val control = sourceBlock(service, Regex("class\\s+OverlayServiceControl\\b"))
        val start = sourceBlock(control, Regex("fun\\s+startAlerts\\s*\\("))
        assertTrue(start.contains("ContextCompat.startForegroundService("))
        assertTrue(start.contains("OverlayService::class.java"))
        assertTrue(start.contains("setAction(OverlayService.ACTION_ALERTS)"))
        val dispatch = sourceBlock(service, Regex("ACTION_ALERTS\\s*->"))
        assertTrue(dispatch.contains("cards.start()"))
        assertFalse("starting alert cards must not show the side panel", dispatch.contains("controller.show()") || dispatch.contains("controller.toggle()"))
        val collect = sourceBlock(service, Regex("AlertInbox\\.alerts\\.collect\\b"))
        assertTrue("the card surface receives the same NBA/NFL inbox", collect.contains("cards.onAlerts(alerts)"))
        assertFalse("card delivery independent of side-panel visibility", Regex("\\bif\\s*\\([^)]*(?:visible|shown)").containsMatchIn(collect))
        assertTrue("separate card-window owner", service.contains("AlertCardOverlay("))
    }

    @Test fun separateCardWindowIsNonFocusableAndNeverStartsOrControlsPlayback() {
        val host = cardHost()
        val show = sourceBlock(host, Regex("fun\\s+showCard\\s*\\("))
        assertTrue("card host checks overlay permission too", host.contains("Settings.canDrawOverlays("))
        assertTrue("actual card renderer is installed", show.contains("AlertCardContent("))
        assertTrue("actual overlay window", show.contains("TYPE_APPLICATION_OVERLAY"))
        assertTrue("game keeps remote input", show.contains("FLAG_NOT_FOCUSABLE"))
        assertTrue("tested top-right geometry", show.contains("AlertCardGeometry.layout("))
        assertTrue("install separate card view", show.contains(".addView("))
        val parameters = sourceBlock(show, Regex("(?:WindowManager\\.)?LayoutParams\\s*\\("))
        assertTrue(parameters.contains("Gravity.TOP") && parameters.contains("Gravity.LEFT"))
        assertTrue(parameters.contains(".left") && parameters.contains(".top"))
        assertTrue("square width", show.contains(".width"))
        assertTrue("square height", show.contains(".height"))
        val hide = sourceBlock(host, Regex("fun\\s+hideCard\\s*\\("))
        assertTrue("expiry removes the real window", Regex("\\.removeView(?:Immediate)?\\s*\\(").containsMatchIn(hide))
        assertFalse("no navigation, audio focus or media-key control on alert arrival", Regex("\\b(?:startActivity|moveTaskToBack|dispatchMediaKeyEvent|requestAudioFocus|performGlobalAction)\\s*\\(").containsMatchIn(host))
        for (call in listOf("ApiClient", "getPanel", "getAlerts")) {
            assertFalse("no new $call call", Regex("\\b$call\\s*\\(").containsMatchIn(host))
        }
    }

    @Test fun cardRendersOnlyPlayerAndNumberOnOneLineUnderASportBand() {
        val content = sourceBlock(cardHost(), Regex("fun\\s+AlertCardContent\\s*\\("))
        assertTrue("compact label formatter", content.contains("AlertCardText.label(notice.player, notice.value)"))
        assertTrue("NBA/NFL colour band", content.contains("sportAccentArgb") && content.contains("notice.sport"))
        assertTrue("one line", content.contains("maxLines = 1"))
        org.junit.Assert.assertEquals("one text node: the label only", 1, Regex("\\bText\\s*\\(").findAll(content).count())
        for (verbose in listOf("headline", "commentary", "matchup", "PanelContent(", "AlertCard(")) {
            assertFalse("separate minimal card, no $verbose", content.contains(verbose))
        }
    }

    @Test fun hostRunsTheQueueOnAMonotonicTimerAndRepositionsTheSidePanel() {
        val host = cardHost()
        assertTrue("uses tested queue", host.contains("AlertCardQueue("))
        val receive = sourceBlock(host, Regex("fun\\s+onAlerts\\s*\\("))
        assertTrue("queue new notices", receive.contains("queue.offer("))
        assertTrue("injected expiry time uses uptime rather than wall clock", receive.contains("SystemClock.elapsedRealtime()"))
        val tick = sourceBlock(host, Regex("fun\\s+tick\\s*\\("))
        assertTrue(tick.contains("queue.advance("))
        assertTrue(tick.contains("SystemClock.elapsedRealtime()"))
        assertTrue("hide expired window", tick.contains("queue.current") && tick.contains("hideCard("))
        val service = overlaySource("panel/OverlayService.kt")
        assertTrue("host ticks without remote interaction", service.contains("cards.tick()"))
        assertTrue("timer is scheduled", Regex("\\bdelay\\s*\\(").containsMatchIn(service))
        assertTrue("side-panel layout reserves the card slot", service.contains("OverlayGeometry.layoutWithAlertCard("))
        val placement = sourceBlock(service, Regex("fun\\s+onCard\\s*\\("))
        assertTrue("existing panel is reattached at the final rectangle", placement.contains(".removeViewImmediate(") && placement.contains(".addView("))
        val destroy = sourceBlock(service, Regex("fun\\s+onDestroy\\s*\\("))
        assertTrue("card window and session queue are cleaned up", destroy.contains("cards.stop()"))
        val stop = sourceBlock(host, Regex("fun\\s+stop\\s*\\("))
        assertTrue(stop.contains("queue.clear()") && stop.contains("hideCard("))
    }

    @Test fun autoDismissRetainsTheAlertForTheRemoteWatchPathInCompanion() {
        val host = cardHost()
        assertFalse("timeout must not dismiss the retained Watch alert", host.contains("AlertInbox.dismiss("))
        val main = productSource("MainActivity.kt")
        assertTrue("remote navigation retains Panel destination", main.contains("Destination.Panel -> LineupPanel("))
        val panel = productSource("panel/LineupPanel.kt")
        val card = sourceBlock(panel, Regex("fun\\s+AlertCard\\s*\\("))
        assertTrue("Watch remains D-pad reachable in Companion", card.contains("FocusTarget.AlertWatch(alert.id)"))
        assertTrue("same retained alert resolves the Watch command", panel.contains("AlertInbox.find(command.alertId)"))
        assertTrue("existing event identity", panel.contains("AlertNotifier.watchEventId(alert)"))
        assertTrue("existing confirmation and launch path", panel.contains("WatchLauncher(context).watchAlert("))
    }
}

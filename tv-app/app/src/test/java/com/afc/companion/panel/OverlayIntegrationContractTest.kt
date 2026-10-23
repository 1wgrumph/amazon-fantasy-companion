package com.afc.companion.panel

import com.afc.companion.ui.theme.productSource
import com.afc.companion.ui.theme.sourceBlock
import java.io.File
import javax.xml.parsers.DocumentBuilderFactory
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.w3c.dom.Element

/** Android wiring contracts follow existing source tests; window/focus behavior needs device verification. */
class OverlayIntegrationContractTest {
    private val android = "http://schemas.android.com/apk/res/android"
    private fun manifest() = DocumentBuilderFactory.newInstance().apply { isNamespaceAware = true }.newDocumentBuilder().parse(
        File(System.getProperty("afc.repoRoot"), "tv-app/app/src/main/AndroidManifest.xml"),
    )
    private fun service() = overlaySource("panel/OverlayService.kt")

    @Test fun manifestRequestsSystemAlertWindowPermission() {
        val permissions = manifest().getElementsByTagName("uses-permission")
        assertTrue("Missing SYSTEM_ALERT_WINDOW permission", (0 until permissions.length).any {
            (permissions.item(it) as Element).getAttributeNS(android, "name") == "android.permission.SYSTEM_ALERT_WINDOW"
        })
    }

    @Test fun manifestDeclaresAnAppPrivateForegroundOverlayService() {
        val services = manifest().getElementsByTagName("service")
        val overlay = (0 until services.length).map { services.item(it) as Element }.singleOrNull {
            it.getAttributeNS(android, "name") in setOf(".panel.OverlayService", "com.afc.companion.panel.OverlayService")
        } ?: throw AssertionError("Missing foreground overlay host: .panel.OverlayService")
        assertEquals("overlay service must not accept other apps' commands", "false", overlay.getAttributeNS(android, "exported"))
        assertTrue("foreground service type is declared", overlay.getAttributeNS(android, "foregroundServiceType").isNotBlank())
        val source = service()
        assertTrue("overlay is a Service", Regex("class\\s+OverlayService\\s*:\\s*Service\\s*\\(").containsMatchIn(source))
        assertTrue("host enters foreground", Regex("\\bstartForeground\\s*\\(").containsMatchIn(source))
    }

    @Test fun androidHostChecksPermissionAndProvidesTheManageOverlayPermissionRoute() {
        val source = service()
        assertTrue("runtime permission check", Regex("Settings\\.canDrawOverlays\\s*\\(").containsMatchIn(source))
        assertTrue("real permission-needed route", source.contains("Settings.ACTION_MANAGE_OVERLAY_PERMISSION"))
        assertTrue("settings target this package", source.contains("package:") && source.contains("packageName"))
        assertTrue("host uses tested controller", Regex("OverlayController\\s*\\(").containsMatchIn(source))
    }

    @Test fun actualWindowUsesNonFocusableOverlayTypeAndTestedGeometry() {
        val source = service()
        val parameters = sourceBlock(source, Regex("(?:WindowManager\\.)?LayoutParams\\s*\\("))
        assertTrue("overlay window type", source.contains("TYPE_APPLICATION_OVERLAY"))
        // The default corner card uses the tested non-focusable flags (CornerCardIntegrationContractTest).
        assertTrue("game keeps D-pad input", source.contains("overlayWindowFlags(focusable = false)"))
        assertTrue("tested pixel geometry", Regex("OverlayGeometry\\.layout\\s*\\(").containsMatchIn(source))
        for (field in listOf("left", "top")) assertTrue("window uses Box.$field", parameters.contains(".$field"))
        for (field in listOf("width", "height")) assertTrue("window uses tested $field", source.contains(".$field"))
        assertTrue("absolute offsets use top gravity", parameters.contains("Gravity.TOP"))
        assertTrue("absolute offsets use left gravity", parameters.contains("Gravity.LEFT"))
        assertTrue("host adds actual window", Regex("\\.addView\\s*\\(").containsMatchIn(source))
        assertTrue("host removes actual window", Regex("\\.removeView(?:Immediate)?\\s*\\(").containsMatchIn(source))
    }

    @Test fun overlayAndFullScreenRenderTheSamePanelContentWithoutANewFeed() {
        val source = service()
        val panel = productSource("panel/LineupPanel.kt")
        assertTrue("overlay calls shared renderer", Regex("\\bPanelContent\\s*\\(").containsMatchIn(source))
        assertTrue("full-screen calls shared renderer", Regex("\\bPanelContent\\s*\\(").containsMatchIn(panel))
        assertFalse("shared renderer callable by overlay", Regex("private\\s+fun\\s+PanelContent\\b").containsMatchIn(panel))
        assertTrue("shared snapshot", Regex("snapshot\\s*=\\s*controller\\.panel\\.snapshot").containsMatchIn(source))
        val content = sourceBlock(panel, Regex("fun\\s+PanelContent\\s*\\("))
        assertTrue(content.contains("PanelText.byPoints(snapshot.rows).forEach"))
        assertTrue(sourceBlock(panel, Regex("fun\\s+PlayerLine\\s*\\(")).contains("PanelText.points(row.points)"))
        assertTrue(sourceBlock(panel, Regex("fun\\s+ScoreLine\\s*\\(")).contains("PanelText.points(snapshot.teamTotal)"))
        assertTrue(content.contains("PanelHeader(snapshot)"))
        assertTrue(sourceBlock(panel, Regex("fun\\s+PanelHeader\\s*\\(")).contains("PanelText.title(snapshot)"))
        for (call in listOf("ApiClient", "getPanel", "getAlerts")) {
            assertFalse("reuse existing update source, no new $call call", Regex("\\b$call\\s*\\(").containsMatchIn(source))
        }
    }

    @Test fun overlaySubscribesToTheExistingInboxAndRetainsWatchIdentity() {
        val source = service()
        val collect = sourceBlock(source, Regex("AlertInbox\\.alerts\\.collect\\b"))
        assertTrue("shared alert presenter", collect.contains("panelAlerts("))
        assertTrue("inbox updates reach overlay", collect.contains("controller.panel.onAlerts("))
        assertFalse("no sport-specific delivery filter", Regex("\\b(?:filter|filterNot|filterIsInstance)\\s*[{(]").containsMatchIn(collect))
        assertTrue("renderer receives current alerts", Regex("alerts\\s*=\\s*controller\\.panel\\.panelAlerts").containsMatchIn(source))
        val panel = productSource("panel/LineupPanel.kt")
        val card = sourceBlock(panel, Regex("fun\\s+AlertCard\\s*\\("))
        assertTrue("visible title", card.contains("alert.text.headline"))
        assertTrue("Watch keeps alert reference", card.contains("FocusTarget.AlertWatch(alert.id)"))
        assertTrue("existing Watch resolver", panel.contains("AlertInbox.find(command.alertId)"))
    }

    @Test fun remoteReachableInAppActionSendsTheToggleIntentThenReturnsToTheGame() {
        val source = service()
        assertTrue("stable intent action", source.contains("com.afc.companion.panel.TOGGLE_OVERLAY"))
        val control = sourceBlock(source, Regex("class\\s+OverlayServiceControl\\b"))
        val toggle = sourceBlock(control, Regex("fun\\s+toggle\\s*\\("))
        assertTrue("start foreground host", toggle.contains("ContextCompat.startForegroundService("))
        assertTrue("explicit app-private target", toggle.contains("OverlayService::class.java"))
        assertTrue("toggle action", toggle.contains("setAction(OverlayService.ACTION_TOGGLE)"))
        val start = sourceBlock(source, Regex("fun\\s+onStartCommand\\s*\\("))
        assertTrue("reads intent action", start.contains("intent?.action"))
        assertTrue("routes toggle", start.contains("ACTION_TOGGLE") && start.contains("controller.toggle()"))
        val main = productSource("MainActivity.kt")
        assertTrue("visible action", main.contains("\"Show over game\""))
        assertTrue("uses overlay control", main.contains("OverlayServiceControl("))
        val onClick = sourceBlock(main, Regex("onClick\\s*=\\s*(?=\\{[^}]*\\.toggle\\s*\\()"))
        assertTrue("D-pad/OK button", main.contains("Button(onClick"))
        assertTrue("return to previous app", onClick.contains("moveTaskToBack(true)"))
        assertTrue("toggle before returning", onClick.indexOf(".toggle(") < onClick.indexOf("moveTaskToBack(true)"))
    }

    @Test fun destroyingTheHostHidesItsWindowAndCancelsItsCollectors() {
        val destroy = sourceBlock(service(), Regex("fun\\s+onDestroy\\s*\\("))
        assertTrue("remove overlay on shutdown", destroy.contains("controller.hide()"))
        assertTrue("cancel host-owned collectors", Regex("\\.cancel\\s*\\(").containsMatchIn(destroy))
    }
}

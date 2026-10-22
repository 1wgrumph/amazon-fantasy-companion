package com.afc.companion.panel

import android.view.WindowManager
import com.afc.companion.ui.theme.productSource
import com.afc.companion.ui.theme.sourceBlock
import java.io.File
import javax.xml.parsers.DocumentBuilderFactory
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.w3c.dom.Element

/** Android wiring for the corner card and the held-≡ service; key delivery itself needs emulator or device proof. */
class CornerCardIntegrationContractTest {
    private val android = "http://schemas.android.com/apk/res/android"
    private fun xml(path: String) = DocumentBuilderFactory.newInstance().apply { isNamespaceAware = true }.newDocumentBuilder()
        .parse(File(System.getProperty("afc.repoRoot"), "tv-app/app/src/main/$path"))
    private fun service() = overlaySource("panel/OverlayService.kt")
    private fun holdService() = overlaySource("access/MenuHoldService.kt")

    @Test fun cardWindowFlagsNeverTakeFocusWhileMenuAndPanelFlagsDo() {
        val card = overlayWindowFlags(focusable = false)
        assertTrue(card and WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE != 0)
        assertTrue(card and WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE != 0)
        val focused = overlayWindowFlags(focusable = true)
        assertEquals(0, focused and WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE)
        assertTrue("touches outside still reach the game", focused and WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL != 0)
    }

    @Test fun hostPlacesTheCardMenuAndPanelFromTestedGeometryAndFlags() {
        val source = service()
        val card = sourceBlock(source, Regex("fun\\s+cardParams\\s*\\("))
        assertTrue("card uses tested corner geometry", card.contains("OverlayGeometry.cornerCard("))
        assertTrue("card is never focusable", card.contains("overlayWindowFlags(focusable = false)"))
        assertTrue("menu uses tested geometry", source.contains("OverlayGeometry.menu("))
        assertTrue("menu and panel focus follows the state machine", source.contains("overlayWindowFlags(focusable = true)"))
        assertTrue("expanded keeps the existing side panel geometry", source.contains("OverlayGeometry.layoutWithAlertCard(") && source.contains("OverlayGeometry.layout("))
        assertTrue("focused windows route keys to the tested controller", source.contains("controller.onFocusedKey("))
        assertTrue("card renderer installed", source.contains("CornerCardContent("))
        assertTrue("menu renderer installed", source.contains("OverlayMenuContent("))
        assertTrue("expanded renders the shared panel", Regex("\\bPanelContent\\s*\\(").containsMatchIn(source))
    }

    @Test fun holdIntentRoutesToTheStateMachine() {
        val source = service()
        assertTrue(source.contains("com.afc.companion.panel.HOLD_OVERLAY"))
        val start = sourceBlock(source, Regex("fun\\s+onStartCommand\\s*\\("))
        assertTrue(start.contains("ACTION_HOLD") && start.contains("controller.hold()"))
        val control = sourceBlock(source, Regex("class\\s+OverlayServiceControl\\b"))
        val hold = sourceBlock(control, Regex("fun\\s+hold\\s*\\("))
        assertTrue(hold.contains("OverlayService::class.java") && hold.contains("setAction(OverlayService.ACTION_HOLD)"))
    }

    @Test fun overlayReadsTheProfileLeaguesForTheSwitcher() {
        val source = service()
        assertTrue("switcher list from the profile", source.contains("overlayTeamLeagues(profile)"))
        assertTrue("still selects the profile's pair", source.contains("panelTeamLeague(profile)"))
    }

    @Test fun manifestDeclaresTheKeyFilterServiceBehindTheSystemBindPermission() {
        val services = xml("AndroidManifest.xml").getElementsByTagName("service")
        val hold = (0 until services.length).map { services.item(it) as Element }.singleOrNull {
            it.getAttributeNS(android, "name") in setOf(".access.MenuHoldService", "com.afc.companion.access.MenuHoldService")
        } ?: throw AssertionError("Missing accessibility service .access.MenuHoldService")
        assertEquals("only the system may bind it", "android.permission.BIND_ACCESSIBILITY_SERVICE", hold.getAttributeNS(android, "permission"))
        assertTrue("user-visible label", hold.getAttributeNS(android, "label").startsWith("@string/"))
        val actions = hold.getElementsByTagName("action")
        assertTrue((0 until actions.length).any { (actions.item(it) as Element).getAttributeNS(android, "name") == "android.accessibilityservice.AccessibilityService" })
        val meta = hold.getElementsByTagName("meta-data").item(0) as Element
        assertEquals("android.accessibilityservice", meta.getAttributeNS(android, "name"))
        assertEquals("@xml/menu_hold_service", meta.getAttributeNS(android, "resource"))
    }

    @Test fun accessibilityConfigRequestsKeyFilteringAndNothingElse() {
        val config = xml("res/xml/menu_hold_service.xml").documentElement
        assertEquals("accessibility-service", config.tagName)
        assertEquals("true", config.getAttributeNS(android, "canRequestFilterKeyEvents"))
        assertTrue(config.getAttributeNS(android, "accessibilityFlags").split('|').contains("flagRequestFilterKeyEvents"))
        assertFalse("no screen reading", config.getAttributeNS(android, "canRetrieveWindowContent") == "true")
        assertTrue("explains itself in Settings", config.getAttributeNS(android, "description").startsWith("@string/"))
        val strings = File(System.getProperty("afc.repoRoot"), "tv-app/app/src/main/res/values/strings.xml").readText()
        for (name in listOf("menu_hold_service_label", "menu_hold_service_description")) assertTrue(strings.contains("name=\"$name\""))
    }

    @Test fun keyFilterServiceConsumesOnlyThroughTheTestedFilterAndControlsNothingElse() {
        val source = holdService()
        assertTrue(Regex("class\\s+MenuHoldService\\s*:\\s*AccessibilityService\\s*\\(").containsMatchIn(source))
        val onKey = sourceBlock(source, Regex("fun\\s+onKeyEvent\\s*\\("))
        assertTrue("tested filter decides", onKey.contains("filter.onKey("))
        assertTrue("hold timer at the tested threshold", source.contains("MenuHoldFilter.HOLD_MS") && source.contains("filter.onHoldTimeout("))
        assertTrue("hold drives the overlay host", source.contains("OverlayServiceControl(this).hold()"))
        for (call in listOf("performGlobalAction", "dispatchGesture", "getRootInActiveWindow", "startActivity")) {
            assertFalse("no $call", Regex("\\b$call\\b").containsMatchIn(source))
        }
    }

    @Test fun serviceOffFallbackKeepsTheInAppButtonAndShowsTheHintOnTheCard() {
        val main = productSource("MainActivity.kt")
        assertTrue("in-app control unchanged", main.contains("\"Show over game\"") && main.contains("OverlayServiceControl("))
        val source = service()
        assertTrue("host reads whether the switch is on", source.contains("MenuHold.enabled("))
        val content = sourceBlock(overlaySource("panel/CornerCardOverlay.kt"), Regex("fun\\s+CornerCardContent\\s*\\("))
        assertTrue("card shows the tested hint", content.contains("CornerCardText.hint("))
        assertTrue("card reads tested opacity", content.contains("CornerCardStyle.BACKGROUND_ALPHA"))
    }
}

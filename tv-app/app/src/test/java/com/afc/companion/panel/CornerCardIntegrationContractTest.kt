package com.afc.companion.panel

import android.view.WindowManager
import java.io.File
import javax.xml.parsers.DocumentBuilderFactory
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.w3c.dom.Element

/** Concrete flag and XML security contracts; actual host/key delivery is covered by CornerCardLifecycleTest. */
class CornerCardIntegrationContractTest {
    private val android = "http://schemas.android.com/apk/res/android"
    private fun xml(path: String) = DocumentBuilderFactory.newInstance().apply { isNamespaceAware = true }.newDocumentBuilder()
        .parse(File(System.getProperty("afc.repoRoot"), "tv-app/app/src/main/$path"))

    @Test fun cardWindowFlagsNeverTakeFocusWhileMenuAndPanelFlagsDo() {
        val card = overlayWindowFlags(focusable = false)
        assertTrue(card and WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE != 0)
        assertTrue(card and WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE != 0)
        val focused = overlayWindowFlags(focusable = true)
        assertEquals(0, focused and WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE)
        assertTrue("touches outside still reach the game", focused and WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL != 0)
    }

    @Test fun manifestDeclaresTheKeyFilterServiceBehindTheSystemBindPermission() {
        val services = xml("AndroidManifest.xml").getElementsByTagName("service")
        val hold = (0 until services.length).map { services.item(it) as Element }.singleOrNull {
            it.getAttributeNS(android, "name") in setOf(".access.MenuHoldService", "com.afc.companion.access.MenuHoldService")
        } ?: throw AssertionError("Missing accessibility service .access.MenuHoldService")
        assertEquals("only the system may bind it", "android.permission.BIND_ACCESSIBILITY_SERVICE", hold.getAttributeNS(android, "permission"))
        assertTrue("user-visible label", hold.getAttributeNS(android, "label").startsWith("@string/"))
        assertEquals("false", hold.getAttributeNS(android, "exported"))
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
        assertEquals("flagRequestFilterKeyEvents", config.getAttributeNS(android, "accessibilityFlags"))
        assertEquals("no unnecessary event subscription", "", config.getAttributeNS(android, "accessibilityEventTypes"))
        for (name in listOf("canPerformGestures", "canRequestTouchExplorationMode", "canRequestFingerprintGestures", "canControlMagnification", "canTakeScreenshot")) {
            assertFalse("no $name capability", config.getAttributeNS(android, name) == "true")
        }
        assertFalse("no screen reading", config.getAttributeNS(android, "canRetrieveWindowContent") == "true")
        assertTrue("explains itself in Settings", config.getAttributeNS(android, "description").startsWith("@string/"))
        val strings = File(System.getProperty("afc.repoRoot"), "tv-app/app/src/main/res/values/strings.xml").readText()
        for (name in listOf("menu_hold_service_label", "menu_hold_service_description")) assertTrue(strings.contains("name=\"$name\""))
    }

}

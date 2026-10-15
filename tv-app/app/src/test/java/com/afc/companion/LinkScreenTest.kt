package com.afc.companion

import com.afc.companion.link.LinkScreen
import java.util.UUID
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test

/** AFC-PR-038: host presentation contract, followed by separate on-stick demonstration. */
class LinkScreenTest {
    @Test fun codeShownWithItsExpiry() {
        val response = JSONObject().put("code", "ABCD2345").put("expires", "2026-10-14T12:10:00Z").put("handle", "fixture")
        val required = node("components", "schemas", "DeviceCode")["required"] as List<*>
        assertTrue(required.all { response.has(it.toString()) })
        val shown = LinkScreen().present(response)
        assertNotNull("Missing behavior: present issued device code", shown)
        assertEquals("codePending", shown!!.state); assertEquals("ABCD2345", shown.code)
        assertTrue("Expiry must remain visible", shown.message.contains(response.getString("expires")))
        assertFalse(shown.showProfile)
    }
    @Test fun pendingPollKeepsLinkFlowOpen() {
        val shown = LinkScreen().present(JSONObject().put("state", "codePending"))
        assertNotNull("Missing behavior: pending state", shown)
        assertEquals("codePending", shown!!.state); assertFalse(shown.showProfile)
    }
    @Test fun expiredCodeShowsExpiryAndCannotContinueToProfile() {
        val shown = LinkScreen().present(JSONObject().put("state", "expired"))
        assertNotNull("Missing behavior: expired state", shown)
        assertEquals("expired", shown!!.state); assertNull(shown.code)
        assertTrue(shown.message.lowercase().contains("expired")); assertFalse(shown.showProfile)
    }
    @Test fun linkedStateContinuesWithoutDisplayingSessionToken() {
        val token = UUID.randomUUID().toString()
        val shown = LinkScreen().present(JSONObject().put("state", "linked").put("sessionToken", token))
        assertNotNull("Missing behavior: linked state", shown)
        assertEquals("linked", shown!!.state); assertTrue(shown.showProfile); assertNull(shown.code)
        assertFalse("Session token must not reach displayed presentation", shown.toString().contains(token))
    }
    @Test fun unlinkedStateRequiresCodeIssuance() {
        val shown = LinkScreen().present(JSONObject().put("state", "unlinked"))
        assertNotNull("Missing behavior: unlinked state", shown)
        assertEquals("unlinked", shown!!.state); assertNull(shown.code); assertFalse(shown.showProfile)
    }
}

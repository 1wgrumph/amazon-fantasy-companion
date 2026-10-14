package com.afc.companion.link

import org.json.JSONObject

// AFC-STUB: pure presentation state; P2-A01 supplies behavior, device review stays separate.
class LinkScreen {
    fun present(response: JSONObject): LinkPresentation? = null
}

data class LinkPresentation(val state: String, val code: String?, val message: String, val showProfile: Boolean)

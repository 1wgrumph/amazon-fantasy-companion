package com.afc.companion.panel

import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLConnection
import java.net.URLStreamHandler
import org.json.JSONObject

/** URL allows one factory per process; both overlay suites share it and select their own fixture. */
internal object OverlayTestPeer {
    @Volatile private var response: (URL) -> JSONObject = { JSONObject() }

    init {
        URL.setURLStreamHandlerFactory { protocol -> if (protocol == "https") object : URLStreamHandler() {
            override fun openConnection(url: URL): URLConnection = object : HttpURLConnection(url) {
                override fun connect() = Unit
                override fun disconnect() = Unit
                override fun usingProxy() = false
                override fun getResponseCode() = 200
                override fun getOutputStream() = ByteArrayOutputStream()
                override fun getInputStream() = ByteArrayInputStream(response(url).toString().toByteArray())
            }
        } else null }
    }

    fun respondWith(fixture: (URL) -> JSONObject) { response = fixture }
}

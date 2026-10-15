package com.afc.companion.alerts

import com.afc.companion.net.Alert
import com.afc.companion.net.ApiClient

// AFC-STUB: P2-A03 implements ALERTSVC's long-poll cursor, bounded queue (alert_queue_max) and coalescing behind these signatures.
class AlertFeed(private val client: ApiClient) {
    /** Cursor sent on the next GET /v1/alerts; null before the first accepted page. */
    val cursor: String? get() = null

    /** Retained alerts for display and history, one entry per alert id. */
    val queue: List<Alert> get() = emptyList()

    /** One long poll; returns the alerts that are new or changed, never throws on a bad page. */
    suspend fun poll(): List<Alert> = emptyList()

    /** Dismiss acknowledges locally; true when a held alert was acknowledged. */
    fun dismiss(id: String): Boolean = false
}

package com.afc.companion.alerts

import com.afc.companion.net.Alert
import com.afc.companion.net.ApiClient
import kotlinx.coroutines.CancellationException

/**
 * ALERTSVC long poll behind [ApiClient.getAlerts]. Pages are untrusted: a bad page (error status,
 * malformed body, an invalid alert, or a cursor longer than the contract's 256 characters) delivers
 * nothing and leaves the cursor where it was. The queue keeps at most alert_queue_max = 20 alerts,
 * one entry per alert id at its newest revision; older or already-held revisions are never re-delivered.
 */
class AlertFeed(private val client: ApiClient) {
    private val lock = Any()
    private var currentCursor: String? = null
    private val held = LinkedHashMap<String, Alert>()
    private val dismissed = LinkedHashMap<String, Long>()

    /** Cursor sent on the next GET /v1/alerts; null before the first accepted page. */
    val cursor: String? get() = synchronized(lock) { currentCursor }

    /** Retained alerts for display and history, one entry per alert id. */
    val queue: List<Alert> get() = synchronized(lock) { held.values.toList() }

    /** One long poll; returns the alerts that are new or changed, never throws on a bad page. */
    suspend fun poll(): List<Alert> {
        val page = try {
            client.getAlerts(cursor).value
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            null
        } ?: return emptyList()
        if (page.cursor.length > MAX_CURSOR_LENGTH) return emptyList()

        val latest = LinkedHashMap<String, Alert>()
        for (alert in page.alerts) {
            val previous = latest[alert.envelope.id]
            if (previous == null || alert.envelope.revision > previous.envelope.revision) {
                latest[alert.envelope.id] = alert
            }
        }
        synchronized(lock) {
            val delivered = latest.values.filter { alert ->
                val known = maxOf(held[alert.envelope.id]?.envelope?.revision ?: -1L, dismissed[alert.envelope.id] ?: -1L)
                alert.envelope.revision > known
            }
            for (alert in delivered) {
                held.remove(alert.envelope.id)
                held[alert.envelope.id] = alert
                dismissed.remove(alert.envelope.id)
            }
            while (held.size > QUEUE_MAX) held.remove(held.keys.first())
            currentCursor = page.cursor
            return delivered
        }
    }

    /** Dismiss acknowledges locally; true when a held alert was acknowledged. Sends nothing. */
    fun dismiss(id: String): Boolean = synchronized(lock) {
        val alert = held.remove(id) ?: return false
        dismissed[id] = alert.envelope.revision
        while (dismissed.size > QUEUE_MAX) dismissed.remove(dismissed.keys.first())
        true
    }

    companion object {
        const val QUEUE_MAX = 20
        const val MAX_CURSOR_LENGTH = 256
    }
}

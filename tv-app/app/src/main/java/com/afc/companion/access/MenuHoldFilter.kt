package com.afc.companion.access

import android.view.KeyEvent

/**
 * Decides, per key event, whether the accessibility filter consumes it. Only a ≡ (Menu) held for
 * [HOLD_MS] is ours: its down already reached the playing app (it cannot be known as long yet), and
 * its auto-repeats and up are consumed. A short ≡ and every other key pass through untouched.
 * Times are the events' uptime milliseconds; the host calls [onHoldTimeout] [HOLD_MS] after the down.
 */
class MenuHoldFilter(private val onHold: () -> Unit) {
    private var downAtMs: Long? = null
    private var fired = false

    /** True when the event is consumed. */
    fun onKey(keyCode: Int, action: Int, repeatCount: Int, eventTimeMs: Long): Boolean {
        if (keyCode != KeyEvent.KEYCODE_MENU) return false
        return when (action) {
            KeyEvent.ACTION_DOWN -> if (repeatCount == 0) {
                downAtMs = eventTimeMs
                fired = false
                false
            } else {
                // A repeat whose down we never saw (service enabled mid-press) stays the app's.
                if (downAtMs == null) return false
                onHoldTimeout(eventTimeMs)
                // Repeats before the threshold are also ours, so the app never acts on its own ≡ long press.
                true
            }
            KeyEvent.ACTION_UP -> {
                if (downAtMs != null) onHoldTimeout(eventTimeMs)
                val consumed = fired
                reset()
                consumed
            }
            else -> false
        }
    }

    fun onHoldTimeout(nowMs: Long) {
        val down = downAtMs ?: return
        if (!fired && nowMs - down >= HOLD_MS) {
            fired = true
            onHold()
        }
    }

    fun reset() {
        downAtMs = null
        fired = false
    }

    companion object { const val HOLD_MS = 700L }
}

object MenuHold {
    private val names = setOf(
        "com.afc.companion/com.afc.companion.access.MenuHoldService",
        "com.afc.companion/.access.MenuHoldService",
    )

    /** Whether Settings.Secure ENABLED_ACCESSIBILITY_SERVICES (colon-separated components) has this app's service on. */
    fun enabled(setting: String?): Boolean = setting.orEmpty().split(':').any { it in names }
}

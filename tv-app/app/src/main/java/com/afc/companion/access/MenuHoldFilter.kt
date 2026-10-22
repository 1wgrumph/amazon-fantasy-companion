package com.afc.companion.access

import android.view.KeyEvent

/**
 * Observes a shared Menu hold without consuming any event. The foreground receives the original
 * balanced sequence and may also act on the hold, as the owner chose. Times are event uptimes.
 */
class MenuHoldFilter(private val onHold: () -> Unit) {
    private var downAtMs: Long? = null
    private var fired = false

    /** Always false: this observer never consumes or injects input. */
    fun onKey(keyCode: Int, action: Int, repeatCount: Int, eventTimeMs: Long, isLongPress: Boolean = false): Boolean {
        if (keyCode != KeyEvent.KEYCODE_MENU) return false
        if (action == KeyEvent.ACTION_DOWN && repeatCount == 0) {
            downAtMs = eventTimeMs
            fired = false
        }
        if (action == KeyEvent.ACTION_DOWN || action == KeyEvent.ACTION_UP) {
            if (downAtMs != null && isLongPress) fire() else onHoldTimeout(eventTimeMs)
            if (action == KeyEvent.ACTION_UP) reset()
        }
        return false
    }

    private fun fire() {
        if (!fired) {
            fired = true
            onHold()
        }
    }

    fun onHoldTimeout(nowMs: Long) {
        val down = downAtMs ?: return
        if (nowMs - down >= HOLD_MS) fire()
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

package com.afc.companion.access

import android.view.KeyEvent

/**
 * Observes a shared Menu hold and a Menu double-tap without consuming any event. The foreground
 * receives the original balanced sequence and may also act on them, as the owner chose. A
 * double-tap is two short presses whose second down comes within [DOUBLE_TAP_MS] of the first up.
 * Times are event uptimes.
 */
class MenuHoldFilter(private val onDoubleTap: () -> Unit = {}, private val onHold: () -> Unit) {
    private var downAtMs: Long? = null
    private var fired = false
    private var shortUpAtMs: Long? = null

    /** Always false: this observer never consumes or injects input. */
    fun onKey(keyCode: Int, action: Int, repeatCount: Int, eventTimeMs: Long, isLongPress: Boolean = false): Boolean {
        if (keyCode != KeyEvent.KEYCODE_MENU) return false
        if (action == KeyEvent.ACTION_DOWN && repeatCount == 0) {
            downAtMs = eventTimeMs
            fired = false
        }
        if (action == KeyEvent.ACTION_DOWN || action == KeyEvent.ACTION_UP) {
            if (downAtMs != null && isLongPress) fire() else onHoldTimeout(eventTimeMs)
            if (action == KeyEvent.ACTION_UP) {
                val down = downAtMs
                val firstUp = shortUpAtMs
                shortUpAtMs = null
                if (down != null && !fired) {
                    if (firstUp != null && down - firstUp in 0..DOUBLE_TAP_MS) onDoubleTap() else shortUpAtMs = eventTimeMs
                }
                downAtMs = null
                fired = false
            }
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
        shortUpAtMs = null
    }

    companion object {
        const val HOLD_MS = 700L
        const val DOUBLE_TAP_MS = 400L
    }
}

object MenuHold {
    private val names = setOf(
        "com.afc.companion/com.afc.companion.access.MenuHoldService",
        "com.afc.companion/.access.MenuHoldService",
    )

    /** Whether Settings.Secure ENABLED_ACCESSIBILITY_SERVICES (colon-separated components) has this app's service on. */
    fun enabled(setting: String?): Boolean = setting.orEmpty().split(':').any { it in names }
}

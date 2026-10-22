package com.afc.companion.access

import android.accessibilityservice.AccessibilityService
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.view.KeyEvent
import android.view.accessibility.AccessibilityEvent
import com.afc.companion.panel.OverlayServiceControl

/**
 * Held ≡ over any app: the user turns this on once in Settings > Accessibility. It only filters
 * keys (res/xml/menu_hold_service.xml); [MenuHoldFilter] passes every event through, and a hold is
 * sent to the overlay host. It reads no screen content and sends no input of its own.
 */
class MenuHoldService : AccessibilityService() {
    private val handler = Handler(Looper.getMainLooper())
    private val filter = MenuHoldFilter { runCatching { OverlayServiceControl(this).hold() } }
    private val timeout = Runnable { filter.onHoldTimeout(SystemClock.uptimeMillis()) }

    override fun onKeyEvent(event: KeyEvent): Boolean {
        if (event.keyCode == KeyEvent.KEYCODE_MENU && event.action == KeyEvent.ACTION_DOWN && event.repeatCount == 0) {
            handler.removeCallbacks(timeout)
            // Measured from the event's own time, so a slow delivery does not stretch the hold.
            handler.postAtTime(timeout, event.eventTime + MenuHoldFilter.HOLD_MS)
        }
        if (event.keyCode == KeyEvent.KEYCODE_MENU && event.action == KeyEvent.ACTION_UP) handler.removeCallbacks(timeout)
        return filter.onKey(event.keyCode, event.action, event.repeatCount, event.eventTime, event.isLongPress)
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) = Unit

    override fun onInterrupt() {
        handler.removeCallbacks(timeout)
        filter.reset()
    }

    override fun onDestroy() {
        handler.removeCallbacks(timeout)
        filter.reset()
        super.onDestroy()
    }
}

package com.afc.companion.alerts

import android.content.Context
import com.afc.companion.net.Alert

// AFC-STUB: P2-A03 implements NOTIFIER (heads-up with Watch / Dismiss, or panel-only) behind this signature.
class AlertNotifier(private val context: Context) {
    fun show(alert: Alert) = Unit
}

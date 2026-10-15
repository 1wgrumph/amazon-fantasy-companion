package com.afc.companion.alerts

import android.app.Service
import android.content.Intent
import android.os.IBinder

// AFC-STUB: P2-A03 implements ALERTSVC (foreground long poll, bounded queue) behind this component.
class AlertService : Service() {
    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        stopSelf(startId)
        return START_NOT_STICKY
    }

    companion object {
        const val ACTION_DISMISS = "com.afc.companion.alerts.DISMISS"
    }
}

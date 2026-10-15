package com.afc.companion.watch

import android.app.Activity
import android.os.Bundle

// AFC-STUB: P2-A04 runs WatchLauncher for the alert's route here (the notification Watch PendingIntent target).
class WatchActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        finish()
    }
}

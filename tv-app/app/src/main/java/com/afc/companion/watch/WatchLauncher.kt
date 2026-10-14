package com.afc.companion.watch

import android.content.Context
import com.afc.companion.net.ProviderRoute
import com.afc.companion.net.RoutingOutcome

// AFC-STUB: P2-A04 implements LAUNCHER (registry route to intent/URI); nothing launches, so nothing is verified.
class WatchLauncher(private val context: Context) {
    fun launch(route: ProviderRoute): RoutingOutcome = RoutingOutcome.AccessUnknown
}

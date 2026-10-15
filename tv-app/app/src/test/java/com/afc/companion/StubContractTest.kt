package com.afc.companion

import android.content.ContextWrapper
import com.afc.companion.net.AccessBasis
import com.afc.companion.net.ProviderRoute
import com.afc.companion.net.RoutingOutcome
import com.afc.companion.watch.WatchLauncher
import org.junit.Assert.assertEquals
import org.junit.Test

/** AFC-STUB contract until P2-A04: the launcher launches nothing, so it never claims a verified route. */
class StubContractTest {
    @Test fun watchLauncherStubReportsAccessUnknown() {
        val route = ProviderRoute("provider", null, null, AccessBasis.CustomerConfirmed)
        assertEquals(RoutingOutcome.AccessUnknown, WatchLauncher(ContextWrapper(null)).launch(route))
    }
}

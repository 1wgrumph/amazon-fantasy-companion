package com.afc.companion.detect

import android.content.pm.PackageManager
import com.afc.companion.net.ApiClient
import com.afc.companion.net.ApiResult
import com.afc.companion.net.InstalledApps

/** Platform-permitted installed-app query (P2-X07). */
fun interface InstalledAppQuery { fun isInstalled(packageName: String): Boolean }

// AFC-STUB: P2-A02 implements DETECTOR per the P2-X07 verdict; reports nothing until then.
class AppDetector(private val query: InstalledAppQuery, private val optedIn: () -> Boolean) {
    constructor(packageManager: PackageManager) : this(InstalledAppQuery { false }, { false })

    fun detect(candidates: Collection<String>): InstalledApps = InstalledApps(emptyList())

    /** Sends the detector report (POST /v1/installed-apps) only while detection is opted in; null when nothing was sent. */
    suspend fun report(client: ApiClient, candidates: Collection<String>): ApiResult<Unit>? = null
}

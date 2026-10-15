package com.afc.companion.detect

import android.content.pm.PackageManager
import com.afc.companion.net.ApiClient
import com.afc.companion.net.ApiResult
import com.afc.companion.net.InstalledApps

/** Platform-permitted installed-app query (P2-X07). */
fun interface InstalledAppQuery { fun isInstalled(packageName: String): Boolean }

/**
 * Reports installed candidates only while the customer opted detection in
 * (AFC-PR-010/-037): opted out means no package reads and no report.
 * Candidate names are untrusted input; malformed names are never queried.
 */
class AppDetector(private val query: InstalledAppQuery, private val optedIn: () -> Boolean) {
    // shortcut: queries named packages only (no <queries> manifest entries) until the P2-X07 stick verdict names the permitted API.
    constructor(packageManager: PackageManager) : this(
        InstalledAppQuery { name ->
            try {
                @Suppress("DEPRECATION") packageManager.getPackageInfo(name, 0)
                true
            } catch (e: PackageManager.NameNotFoundException) {
                false
            }
        },
        { false },
    )

    fun detect(candidates: Collection<String>): InstalledApps {
        if (!optedIn()) return InstalledApps(emptyList())
        return InstalledApps(
            candidates.distinct().filter { PACKAGE.matches(it) }.filter(query::isInstalled)
                .take(InstalledApps.MAX_PACKAGES),
        )
    }

    /** Sends the detector report (POST /v1/installed-apps) only while detection is opted in; null when nothing was sent. */
    suspend fun report(client: ApiClient, candidates: Collection<String>): ApiResult<Unit>? {
        if (!optedIn()) return null
        return client.reportInstalledApps(detect(candidates))
    }

    private companion object {
        val PACKAGE = Regex("^[A-Za-z0-9._]{1,255}$")
    }
}

package com.afc.companion.detect

import android.content.pm.PackageManager
import com.afc.companion.net.InstalledApps

// AFC-STUB: P2-A02 implements DETECTOR per the P2-X07 verdict; reports nothing until then.
class AppDetector(private val packageManager: PackageManager) {
    fun detect(candidates: Collection<String>): InstalledApps = InstalledApps(emptyList())
}

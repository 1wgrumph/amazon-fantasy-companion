package com.afc.companion

import com.afc.companion.watch.WatchLauncher
import java.nio.file.Files
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

/** Post-P2-A04 contract: the Watch stubs are gone; every Watch runs the reporting attempt path. */
class StubContractTest {
    @Test fun noAfcStubRemainsInMainSourcesAfterP2A04() {
        val stubs = Files.walk(repo.resolve("tv-app/app/src/main")).use { files ->
            files.filter { Files.isRegularFile(it) && "AFC-STUB" in String(Files.readAllBytes(it), Charsets.UTF_8) }.map { repo.relativize(it).toString() }.toList()
        }
        assertEquals(emptyList<String>(), stubs)
    }

    @Test fun stubLaunchWithoutAReportIsRemovedAfterP2A04() {
        assertTrue(
            "only watch/watchAlert launch, and both report exactly one outcome",
            WatchLauncher::class.java.methods.none { it.name == "launch" },
        )
    }
}

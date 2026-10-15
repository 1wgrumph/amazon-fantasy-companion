package com.afc.companion.detect

import com.afc.companion.LocalApi
import com.afc.companion.net.ApiClient
import com.afc.companion.net.InstalledApps
import java.util.Collections
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

/** DETECTOR (AFC-PR-003, -010, -037): installed-app facts only through the platform query, only while opted in. */
class AppDetectorTest {
    private val installed = setOf("com.example.provider.a", "com.example.provider.c")
    private val candidates = listOf("com.example.provider.a", "com.example.provider.b", "com.example.provider.c")
    private val queried: MutableList<String> = Collections.synchronizedList(mutableListOf())
    private val query = InstalledAppQuery { queried.add(it); it in installed }

    @Test fun reportsEachInstalledCandidateAndNoAbsentOne() {
        val apps = AppDetector(query) { true }.detect(candidates)
        assertEquals("each supported installed app reported", installed, apps.packages.toSet())
        assertEquals("no duplicates", apps.packages.size, apps.packages.toSet().size)
        assertTrue("absent app never reported", "com.example.provider.b" !in apps.packages)
    }

    @Test fun optedOutPerformsNoReads() {
        val apps = AppDetector(query) { false }.detect(candidates)
        assertTrue(apps.packages.isEmpty())
        assertTrue("no detection reads while opted out", queried.isEmpty())
    }

    /** Candidate names are untrusted: malformed names are never queried or reported. */
    @Test fun malformedCandidatesAreSkipped() {
        val apps = AppDetector({ queried.add(it); true }) { true }.detect(listOf("com.example.provider.a", "bad name;", ""))
        assertEquals(listOf("com.example.provider.a"), apps.packages)
        assertEquals(listOf("com.example.provider.a"), queried.toList())
    }

    @Test fun reportIsBoundedByTheContractCap() {
        val many = (0 until InstalledApps.MAX_PACKAGES + 100).map { "com.example.p$it" }
        val apps = AppDetector({ true }) { true }.detect(many)
        assertEquals(InstalledApps.MAX_PACKAGES, apps.packages.size)
    }

    @Test fun detectorReportPostsInstalledApps() = runBlocking {
        LocalApi(listOf(200 to "{}")).use { server ->
            val result = AppDetector(query) { true }.report(ApiClient(server.baseUrl, { "session-fixture" }), candidates)
            assertNotNull("Missing behavior: detector report sent", result)
            assertEquals(200, result!!.status)
            val sent = server.requests.single()
            assertEquals("POST", sent.method); assertEquals("/v1/installed-apps", sent.path)
            assertEquals(installed, JSONObject(sent.body).getJSONArray("packages").let { a -> (0 until a.length()).map(a::getString).toSet() })
        }
    }

    @Test fun optedOutSendsNoReport() = runBlocking {
        LocalApi(listOf(200 to "{}")).use { server ->
            AppDetector(query) { false }.report(ApiClient(server.baseUrl, { "session-fixture" }), candidates)
            assertTrue(server.requests.isEmpty())
            assertTrue(queried.isEmpty())
        }
    }
}

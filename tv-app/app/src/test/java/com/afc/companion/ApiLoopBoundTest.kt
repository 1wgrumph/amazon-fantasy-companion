package com.afc.companion

import com.afc.companion.net.ApiClient
import com.afc.companion.net.ApiResponse
import java.io.ByteArrayInputStream
import java.net.HttpURLConnection
import java.net.URL
import kotlin.coroutines.Continuation
import kotlin.coroutines.intrinsics.COROUTINE_SUSPENDED
import kotlin.coroutines.intrinsics.suspendCoroutineUninterceptedOrReturn
import kotlin.coroutines.resume
import kotlin.coroutines.startCoroutine
import kotlinx.coroutines.Dispatchers
import org.junit.Assert.*
import org.junit.Test

// Inputs were exercised against LocalApi in pit-bounded-loops/focused.txt; no shared resources.
class ApiLoopBoundTest {
    @Test fun transientRetriesStopAtTheAttemptCapAfterSuspendedBackoffs() {
        var attempts = 0
        val waits = mutableListOf<Long>()
        var pending: Continuation<Unit>? = null
        var completion: Result<ApiResponse>? = null
        val client = ApiClient("https://api.example.test", openConnection = { url ->
            assertNull("No request before its backoff resumes", pending)
            assertTrue("At most one request plus three retries", attempts++ < 4)
            responseConnection(url, 503, "{}".toByteArray())
        }, backoff = { millis ->
            assertTrue("At most three backoffs", waits.size < 3)
            waits.add(millis)
            // The test resumes this continuation only after request has returned its suspension marker.
            suspendCoroutineUninterceptedOrReturn<Unit> { pending = it; COROUTINE_SUSPENDED }
        }, ioDispatcher = Dispatchers.Unconfined)
        val request: suspend () -> ApiResponse = { client.request("GET", "/v1/profile") }
        request.startCoroutine(object : Continuation<ApiResponse> {
            override val context = Dispatchers.Unconfined
            override fun resumeWith(result: Result<ApiResponse>) { completion = result }
        })
        val expected = listOf(1_000L, 2_000L, 4_000L)
        for (index in expected.indices) {
            assertNull("Request must remain suspended until backoff resumes", completion)
            assertEquals(expected.take(index + 1), waits)
            assertEquals(index + 1, attempts)
            val continuation = checkNotNull(pending)
            pending = null
            continuation.resume(Unit)
        }
        assertEquals(503, checkNotNull(completion).getOrThrow().status)
        assertEquals(4, attempts)
        assertNull(pending)
    }

    @Test fun oversizedResponseStopsReadingAtTheByteCap() {
        val input = object : ByteArrayInputStream(ByteArray(65_537) { 'x'.code.toByte() }) {
            override fun read(bytes: ByteArray, offset: Int, length: Int): Int {
                assertTrue("Bounded reader must stop before requesting zero bytes", length > 0)
                return super.read(bytes, offset, length)
            }
        }
        val failure = assertThrows(IllegalArgumentException::class.java) { ApiClient.readBounded(input) }
        assertEquals("Response body exceeds 64 KiB", failure.message)
    }

    private fun responseConnection(url: URL, status: Int, body: ByteArray): HttpURLConnection =
        object : HttpURLConnection(url) {
            override fun connect() {}
            override fun disconnect() {}
            override fun usingProxy(): Boolean = false
            override fun getResponseCode(): Int = status
            override fun getInputStream(): ByteArrayInputStream = ByteArrayInputStream(body)
            override fun getErrorStream(): ByteArrayInputStream = inputStream
        }
}

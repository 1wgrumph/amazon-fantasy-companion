package com.afc.companion

import com.afc.companion.net.ApiClient
import java.io.ByteArrayInputStream
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.selects.select
import org.junit.Assert.*
import org.junit.Test

// Inputs were exercised against LocalApi in pit-bounded-loops/focused.txt; no shared resources.
class ApiLoopBoundTest {
    @Test fun transientRetriesStopAtTheAttemptCapAfterSuspendedBackoffs() = runBlocking(Dispatchers.IO) {
        val attempts = AtomicInteger()
        val backoffs = AtomicInteger()
        val resumed = AtomicInteger()
        val waiting = Channel<Long>(Channel.UNLIMITED)
        val resume = Channel<Unit>()
        // Start inline on the request dispatcher so the first backoff has suspended before resumption.
        val response = async(start = CoroutineStart.UNDISPATCHED) {
            ApiClient("https://api.example.test", openConnection = { url ->
                assertEquals("No request before its backoff resumes", backoffs.get(), resumed.get())
                assertTrue("At most one request plus three retries", attempts.getAndIncrement() < 4)
                responseConnection(url, 503, "{}".toByteArray())
            }, backoff = { millis ->
                assertTrue("At most three backoffs", backoffs.getAndIncrement() < 3)
                waiting.send(millis)
                resume.receive()
                resumed.incrementAndGet()
            }).request("GET", "/v1/profile")
        }
        for ((index, expected) in listOf(1_000L, 2_000L, 4_000L).withIndex()) {
            val millis = select<Long> {
                waiting.onReceive { it }
                response.onAwait { throw AssertionError("Request returned before its backoff") }
            }
            assertEquals(expected, millis)
            assertEquals(index + 1, attempts.get())
            resume.send(Unit)
        }
        assertEquals(503, response.await().status)
        assertEquals(4, attempts.get())
        assertEquals(3, backoffs.get())
    }

    @Test fun oversizedResponseStopsReadingAtTheByteCap() {
        val client = ApiClient("https://api.example.test", openConnection = { url ->
            responseConnection(url, 200, ByteArray(65_537) { 'x'.code.toByte() })
        })
        val failure = assertThrows(IllegalArgumentException::class.java) {
            runBlocking { client.request("GET", "/v1/profile") }
        }
        assertEquals("Response body exceeds 64 KiB", failure.message)
    }

    private fun responseConnection(url: URL, status: Int, body: ByteArray): HttpURLConnection =
        object : HttpURLConnection(url) {
            override fun connect() {}
            override fun disconnect() {}
            override fun usingProxy(): Boolean = false
            override fun getResponseCode(): Int = status
            override fun getInputStream(): ByteArrayInputStream = object : ByteArrayInputStream(body) {
                override fun read(bytes: ByteArray, offset: Int, length: Int): Int {
                    assertTrue("Bounded reader must stop before requesting zero bytes", length > 0)
                    return super.read(bytes, offset, length)
                }
            }
            override fun getErrorStream(): ByteArrayInputStream = inputStream
        }
}

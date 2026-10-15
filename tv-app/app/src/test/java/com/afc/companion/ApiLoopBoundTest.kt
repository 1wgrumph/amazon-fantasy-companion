package com.afc.companion

import com.afc.companion.net.ApiClient
import java.io.FilterInputStream
import java.io.InputStream
import java.net.HttpURLConnection
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.async
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.selects.select
import org.junit.Assert.*
import org.junit.Test

// Resource group: none shared. LocalApi owns an OS-assigned port and its executor.
class ApiLoopBoundTest {
    @Test fun transientRetriesStopAtTheAttemptCap() = runBlocking {
        LocalApi(listOf(503 to "{}")).use { server ->
            val waits = mutableListOf<Long>()
            val client = ApiClient(server.baseUrl, openConnection = { url ->
                assertTrue("At most one request plus three retries", server.requests.size < 4)
                connect(url)
            }, backoff = {
                assertTrue("At most three backoffs", waits.size < 3)
                waits.add(it)
            })
            assertEquals(503, client.request("GET", "/v1/profile").status)
            assertEquals(listOf(1_000L, 2_000L, 4_000L), waits)
            assertEquals(4, server.requests.size)
        }
    }

    @Test fun suspendedBackoffMustResumeBeforeTheNextAttempt() = runBlocking {
        LocalApi(listOf(503 to "{}", 200 to "{}")).use { server ->
            val waiting = Channel<Long>(Channel.UNLIMITED)
            val resume = Channel<Unit>()
            val resumed = AtomicBoolean(false)
            val response = async {
                ApiClient(server.baseUrl, openConnection = { url ->
                    assertTrue("No retry until the suspended backoff resumes", server.requests.isEmpty() || resumed.get())
                    connect(url)
                }, backoff = { millis ->
                    waiting.send(millis)
                    resume.receive()
                    resumed.set(true)
                }).request("GET", "/v1/profile")
            }
            val millis = select<Long> {
                waiting.onReceive { it }
                response.onAwait { throw AssertionError("Request returned before its backoff") }
            }
            assertEquals(1_000L, millis)
            assertEquals(1, server.requests.size)
            resume.send(Unit)
            assertEquals(200, response.await().status)
            assertEquals(2, server.requests.size)
        }
    }

    @Test fun oversizedResponseStopsReadingAtTheByteCap() {
        LocalApi(listOf(200 to "x".repeat(65_537))).use { server ->
            val client = ApiClient(server.baseUrl, openConnection = { url ->
                val real = connect(url)
                object : HttpURLConnection(url) {
                    override fun connect() = real.connect()
                    override fun disconnect() = real.disconnect()
                    override fun usingProxy(): Boolean = real.usingProxy()
                    override fun getResponseCode(): Int = real.responseCode
                    override fun getInputStream(): InputStream = object : FilterInputStream(real.inputStream) {
                        override fun read(bytes: ByteArray, offset: Int, length: Int): Int {
                            assertTrue("Bounded reader must stop before requesting zero bytes", length > 0)
                            return super.read(bytes, offset, length)
                        }
                    }
                }
            })
            assertThrows(IllegalArgumentException::class.java) {
                runBlocking { client.request("GET", "/v1/profile") }
            }
            assertEquals(1, server.requests.size)
        }
    }
}

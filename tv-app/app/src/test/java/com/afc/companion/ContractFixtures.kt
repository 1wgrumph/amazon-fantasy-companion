package com.afc.companion

import com.sun.net.httpserver.HttpServer
import java.net.HttpURLConnection
import java.net.InetSocketAddress
import java.net.URL
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import org.json.JSONObject
import org.yaml.snakeyaml.Yaml

// Resource group: none shared. Each server owns a port bound by the OS and its executor.
internal val repo: Path = Path.of(System.getProperty("afc.repoRoot"))
internal val openApi: Map<String, Any> = Yaml().load(Files.readAllBytes(repo.resolve("backend/src/api/openapi.yaml")).toString(Charsets.UTF_8))
@Suppress("UNCHECKED_CAST")
internal fun node(vararg keys: String): Map<String, Any> = keys.fold(openApi) { current, key -> current[key] as Map<String, Any> }
internal fun envelopeFixture(revision: Long = 4): JSONObject = JSONObject()
    .put("schemaVersion", 1).put("id", "profile-fixture").put("revision", revision)
    .put("source", "manual").put("updatedAt", "2026-10-14T12:00:00Z")
    .put("data", JSONObject().put("scoringPreset", "halfPpr"))

internal data class RecordedRequest(val method: String, val path: String, val bearer: String?, val body: String, val atNanos: Long = System.nanoTime())
internal class LocalApi(private val replies: List<Pair<Int, String>>) : AutoCloseable {
    val requests = CopyOnWriteArrayList<RecordedRequest>()
    private val executor = Executors.newCachedThreadPool()
    private val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
    val baseUrl: String = "http://127.0.0.1:${server.address.port}"
    init {
        server.executor = executor
        server.createContext("/") { exchange ->
            try {
                val index = requests.size
                requests.add(RecordedRequest(exchange.requestMethod, exchange.requestURI.toString(),
                    exchange.requestHeaders.getFirst("Authorization"), exchange.requestBody.bufferedReader().readText()))
                val (status, body) = replies[index.coerceAtMost(replies.lastIndex)]
                val bytes = body.toByteArray(Charsets.UTF_8)
                exchange.responseHeaders.set("Content-Type", "application/json")
                exchange.sendResponseHeaders(status, bytes.size.toLong())
                exchange.responseBody.use { it.write(bytes) }
            } finally { exchange.close() }
        }
        server.start()
    }
    override fun close() {
        server.stop(0)
        executor.shutdownNow()
        check(executor.awaitTermination(30, TimeUnit.SECONDS)) { "Test-owned HTTP executor did not stop" }
    }
}
internal fun connect(url: URL): HttpURLConnection = url.openConnection() as HttpURLConnection

// Observe thread use while delegating every operation to the real JDK HTTP connection.
internal class ObservedConnection(private val real: HttpURLConnection, private val threads: MutableList<Long>) : HttpURLConnection(real.url) {
    private fun observe() { threads.add(Thread.currentThread().id) }
    override fun connect() { observe(); real.connect() }
    override fun disconnect() = real.disconnect()
    override fun usingProxy(): Boolean = real.usingProxy()
    override fun getResponseCode(): Int { observe(); return real.responseCode }
    override fun getInputStream(): java.io.InputStream { observe(); return real.inputStream }
    override fun getErrorStream(): java.io.InputStream? { observe(); return real.errorStream }
    override fun getOutputStream(): java.io.OutputStream { observe(); return real.outputStream }
    override fun setRequestMethod(method: String) { real.requestMethod = method }
    override fun getRequestMethod(): String = real.requestMethod
    override fun setRequestProperty(key: String, value: String) = real.setRequestProperty(key, value)
    override fun getHeaderField(name: String): String? = real.getHeaderField(name)
    override fun setConnectTimeout(timeout: Int) { real.connectTimeout = timeout }
    override fun getConnectTimeout(): Int = real.connectTimeout
    override fun setReadTimeout(timeout: Int) { real.readTimeout = timeout }
    override fun getReadTimeout(): Int = real.readTimeout
    override fun setDoOutput(value: Boolean) { real.doOutput = value }
    override fun setInstanceFollowRedirects(value: Boolean) { real.instanceFollowRedirects = value }
}

internal fun sameJson(expected: JSONObject, actual: JSONObject?): Boolean = actual != null &&
    Yaml().load<Any>(expected.toString()) == Yaml().load<Any>(actual.toString())

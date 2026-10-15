package com.afc.companion.profile

import com.afc.companion.net.ScoringPreset
import com.sun.net.httpserver.HttpServer
import java.net.InetSocketAddress
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import org.json.JSONObject

// Resource group: none shared. Each ProfileServer owns an OS-assigned loopback port and its executor.

/** Every control set away from its default, so a dropped or defaulted control is visible. */
internal fun customized(): ProfileState = ProfileState(
    selections = FantasySelections(setOf("league-a"), setOf("team-7"), setOf("player-11", "player-23"), setOf("KC", "BUF")),
    teamLeague = TeamLeague("league-a", "team-7"),
    alertTypes = setOf(AlertType.RedZone, AlertType.CloseGame),
    minGapSeconds = 300,
    quietHours = listOf(TimeWindow(22 * 60, 7 * 60)),
    gameDay = GameDayMode(true, listOf(TimeWindow(13 * 60, 23 * 60))),
    spoilerDelaySeconds = 45,
    presentation = Presentation.PanelOnly,
    voiceEnabled = true,
    excitement = Excitement.Hype,
    providerPref = ProviderPreference(listOf("provider-b", "provider-a"), setOf("provider-b"),
        mapOf("com.example.provider.a" to false, "com.example.provider.c" to true), "market-501"),
    switchingConfirm = false,
    panel = PanelPrefs(false),
    detectionOptIn = true,
    scoringPreset = ScoringPreset.Ppr,
)

/** A stateful GET/PUT /v1/profile peer that outlives each client, standing in for the backend across an app restart. */
internal class ProfileServer(initialData: JSONObject = JSONObject()) : AutoCloseable {
    @Volatile var revision = 4L
        private set
    @Volatile var data: JSONObject = initialData
        private set
    val puts = java.util.concurrent.atomic.AtomicInteger()
    private val executor = Executors.newCachedThreadPool()
    private val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
    val baseUrl = "http://127.0.0.1:${server.address.port}"

    init {
        server.executor = executor
        server.createContext("/v1/profile") { exchange ->
            try {
                val (status, body) = synchronized(this) {
                    when (exchange.requestMethod) {
                        "GET" -> 200 to envelope()
                        "PUT" -> {
                            puts.incrementAndGet()
                            val update = JSONObject(exchange.requestBody.bufferedReader().readText())
                            if (update.optLong("revision", -1) != revision) {
                                409 to JSONObject().put("error", JSONObject().put("code", "conflict").put("message", "stale revision"))
                            } else {
                                data = update.getJSONObject("data"); revision++; 200 to envelope()
                            }
                        }
                        else -> 405 to JSONObject()
                    }
                }
                val bytes = body.toString().toByteArray(Charsets.UTF_8)
                exchange.responseHeaders.set("Content-Type", "application/json")
                exchange.sendResponseHeaders(status, bytes.size.toLong())
                exchange.responseBody.use { it.write(bytes) }
            } finally { exchange.close() }
        }
        server.start()
    }

    private fun envelope(): JSONObject = JSONObject().put("schemaVersion", 1).put("id", "profile-fixture")
        .put("revision", revision).put("source", "manual").put("updatedAt", "2026-10-14T12:00:00Z").put("data", JSONObject(data.toString()))

    override fun close() {
        server.stop(0)
        executor.shutdownNow()
        check(executor.awaitTermination(30, TimeUnit.SECONDS)) { "Test-owned HTTP executor did not stop" }
    }
}

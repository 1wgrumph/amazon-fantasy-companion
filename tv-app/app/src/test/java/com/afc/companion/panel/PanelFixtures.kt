package com.afc.companion.panel

import com.afc.companion.net.PanelState
import com.sun.net.httpserver.HttpServer
import java.net.InetSocketAddress
import java.time.Instant
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import org.json.JSONArray
import org.json.JSONObject

// Resource group: none shared. Each PanelServer owns an OS-assigned loopback port and its executor.
//
// TV-side PanelState wire shape (spec 04.3 data model: row projections carry player ID, points, game status and
// per-value source/freshness; unknown points stay null). P2-B07 emits the same `data` object; a mismatch is a
// pair-reconciliation finding, not a reason to loosen these tests.

internal const val TL = "league-a/team-7"
internal const val AS_OF = "2026-10-15T20:00:00Z"
internal val AS_OF_MS: Long = Instant.parse(AS_OF).toEpochMilli()

internal fun value(v: Any?, reason: String? = null, source: String = "live", asOf: String? = AS_OF): JSONObject =
    JSONObject().put("value", v ?: JSONObject.NULL).put("reason", reason ?: JSONObject.NULL)
        .put("source", source).put("asOf", asOf ?: JSONObject.NULL)

internal fun row(id: String, name: String, points: JSONObject, status: String? = "Q2 08:14"): JSONObject =
    JSONObject().put("playerId", id).put("name", name).put("points", points).put("gameStatus", status ?: JSONObject.NULL)

internal fun panelData(
    rows: List<JSONObject> = listOf(
        row("p-11", "Player Eleven", value(12.3)),
        row("p-23", "Player Twenty-Three", value(-1.5)),
        row("p-31", "Player Thirty-One", value(null, "feed withheld"), null),
    ),
    basis: Any? = "halfPpr",
    total: JSONObject = value(10.8),
    progress: JSONObject = value(0.5),
    teamLeague: String = TL,
): JSONObject = JSONObject().put("teamLeague", teamLeague).put("scoringBasis", basis ?: JSONObject.NULL)
    .put("rows", JSONArray(rows)).put("teamTotal", total).put("progress", progress)

internal fun envelope(data: JSONObject, revision: Long = 7): JSONObject = JSONObject().put("schemaVersion", 1)
    .put("id", "panel-fixture").put("revision", revision).put("source", "live").put("updatedAt", AS_OF).put("data", data)

internal fun state(data: JSONObject = panelData(), revision: Long = 7): PanelState =
    requireNotNull(PanelState.from(envelope(data, revision))) { "fixture envelope must satisfy CONTRACT-AFC-P2-ENVELOPE" }

/** A decoded snapshot built directly, so controller tests do not depend on the decoder. */
internal fun snap(
    revision: Long = 7,
    rows: List<PanelRow> = listOf(prow("p-11", 12.3), prow("p-23", -1.5), prow("p-31", 4.0)),
    total: Double? = 14.8,
    teamLeague: String = TL,
): PanelSnapshot = PanelSnapshot(teamLeague, revision, ScoringBasis.HalfPpr, rows,
    PanelValue(total, if (total == null) "feed withheld" else null, "live", AS_OF_MS), PanelValue(0.5, null, "live", AS_OF_MS))

internal fun prow(id: String, points: Double?, status: String? = "Q2 08:14"): PanelRow =
    PanelRow(id, "Player $id", PanelValue(points, if (points == null) "feed withheld" else null, "live", AS_OF_MS), status)

/** A GET /v1/panel peer that records each query it receives. */
internal class PanelServer(private val body: JSONObject) : AutoCloseable {
    val queries = CopyOnWriteArrayList<String?>()
    private val executor = Executors.newCachedThreadPool()
    private val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
    val baseUrl = "http://127.0.0.1:${server.address.port}"

    init {
        server.executor = executor
        server.createContext("/v1/panel") { exchange ->
            try {
                queries.add(exchange.requestURI.rawQuery)
                val bytes = body.toString().toByteArray(Charsets.UTF_8)
                exchange.responseHeaders.set("Content-Type", "application/json")
                exchange.sendResponseHeaders(200, bytes.size.toLong())
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

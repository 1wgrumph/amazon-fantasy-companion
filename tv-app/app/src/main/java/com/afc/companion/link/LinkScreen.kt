package com.afc.companion.link

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text
import com.afc.companion.net.ApiClient
import com.afc.companion.net.DeviceCode
import com.afc.companion.net.LinkState
import com.afc.companion.net.LinkStatus
import com.afc.companion.ui.theme.TvButton as Button
import com.afc.companion.ui.theme.tvSafeZonePadding
import io.nayuki.qrcodegen.QrCode
import java.io.IOException
import java.net.URLEncoder
import kotlinx.coroutines.delay
import org.json.JSONObject

/** AFC-PR-038 TV side: presentation of device-code and link-poll responses. Never carries the session token. */
class LinkScreen(private val linkPage: String = "the link page") {
    /** Phone link page with the code pre-filled; the TV shows it as a QR code. */
    fun qrPayload(code: String) = "$linkPage?code=${URLEncoder.encode(code, Charsets.UTF_8.name())}"

    fun present(response: JSONObject): LinkPresentation? {
        if (response.has("code")) {
            val code = DeviceCode.from(response) ?: return null
            return LinkPresentation(LinkStatus.CodePending.wire, code.code,
                "On your phone, open $linkPage and enter this code before ${code.expires}", false)
        }
        val state = LinkState.from(response) ?: return null
        return when (state.state) {
            LinkStatus.Unlinked -> LinkPresentation(state.state.wire, null, "This TV is not linked. Select Get code to link it.", false)
            LinkStatus.CodePending -> LinkPresentation(state.state.wire, null, "Waiting for the code to be confirmed", false)
            LinkStatus.Linked -> LinkPresentation(state.state.wire, null, "Linked", true)
            LinkStatus.Expired -> LinkPresentation(state.state.wire, null, "The code expired. Select Get code for a new one.", false)
        }
    }
}

data class LinkPresentation(val state: String, val code: String?, val message: String, val showProfile: Boolean)

/** Issues a code, then polls its handle until linked or expired. IOException and contract errors reach the caller. */
class LinkFlow(
    private val client: ApiClient,
    private val screen: LinkScreen,
    private val pollIntervalMs: Long = POLL_INTERVAL_MS,
    private val sleep: suspend (Long) -> Unit = { delay(it) },
) {
    suspend fun run(show: (LinkPresentation) -> Unit, onLinked: (String) -> Unit) {
        val issued = client.issueLinkCode()
        val code = issued.value ?: return show(failure(issued.status))
        show(screen.present(JSONObject().put("code", code.code).put("expires", code.expires).put("handle", code.handle))!!)
        while (true) {
            sleep(pollIntervalMs)
            val polled = client.pollLink(code.handle)
            val state = polled.value ?: return show(failure(polled.status))
            when (state.state) {
                LinkStatus.CodePending -> continue
                LinkStatus.Linked -> {
                    val token = state.sessionToken ?: return show(failure(polled.status))
                    onLinked(token)
                    return show(screen.present(JSONObject().put("state", state.state.wire))!!)
                }
                else -> return show(screen.present(JSONObject().put("state", state.state.wire))!!)
            }
        }
    }

    companion object {
        const val POLL_INTERVAL_MS = 5_000L
        fun failure(status: Int) = LinkPresentation("error", null, "Linking failed (HTTP $status). Select Get code to try again.", false)
    }
}

@Composable
fun LinkView(client: ApiClient, onLinked: (String) -> Unit, modifier: Modifier = Modifier) {
    var attempt by remember { mutableIntStateOf(0) }
    var shown by remember { mutableStateOf<LinkPresentation?>(null) }
    val screen = remember(client) { LinkScreen("${client.baseUrl.trimEnd('/')}/link") }
    LaunchedEffect(attempt) {
        shown = null
        try {
            LinkFlow(client, screen).run({ shown = it }, onLinked)
        } catch (e: IOException) {
            shown = LinkPresentation("networkError", null, "Network error. Check the connection, then select Get code.", false)
        } catch (e: IllegalArgumentException) {
            shown = LinkPresentation("error", null, "The backend sent an unexpected response.", false)
        }
    }
    Column(modifier.tvSafeZonePadding().padding(8.dp), verticalArrangement = Arrangement.spacedBy(24.dp)) {
        Text("Link this TV", style = MaterialTheme.typography.headlineMedium)
        val current = shown
        if (current == null) {
            Text("Requesting a code…", style = MaterialTheme.typography.bodyLarge)
        } else {
            Row(horizontalArrangement = Arrangement.spacedBy(32.dp), verticalAlignment = Alignment.CenterVertically) {
                current.code?.let { LinkQr(screen.qrPayload(it)) }
                Column(verticalArrangement = Arrangement.spacedBy(24.dp)) {
                    current.code?.let { Text(it, color = MaterialTheme.colorScheme.primary, style = MaterialTheme.typography.displayMedium) }
                    Text(current.message, color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodyLarge)
                }
            }
            if (current.state != LinkStatus.CodePending.wire && !current.showProfile) {
                Button(onClick = { attempt++ }) { Text("Get code") }
            }
        }
    }
}

/** Dark-on-white QR with the standard 4-module quiet zone, snapped to whole pixels so modules do not blur. */
@Composable
private fun LinkQr(payload: String) {
    val qr = remember(payload) { QrCode.encodeText(payload, QrCode.Ecc.MEDIUM) }
    Canvas(Modifier.size(220.dp).background(Color.White).semantics { contentDescription = "QR code to link this TV" }) {
        val cell = kotlin.math.floor(size.minDimension / (qr.size + 8))
        val origin = kotlin.math.floor((size.minDimension - cell * qr.size) / 2)
        for (y in 0 until qr.size) for (x in 0 until qr.size) {
            if (qr.getModule(x, y)) drawRect(Color.Black, Offset(origin + x * cell, origin + y * cell), Size(cell, cell))
        }
    }
}

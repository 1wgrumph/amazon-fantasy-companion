package com.afc.companion.alerts

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import com.afc.companion.net.Alert
import com.afc.companion.watch.WatchActivity
import com.afc.companion.ui.theme.TvPalette
import org.json.JSONObject
import java.net.URLEncoder
import java.security.MessageDigest

/**
 * NOTIFIER: one alert as a heads-up notification on a high-importance channel, with Watch (a
 * [PendingIntent] into [WatchActivity], P2-A04's launcher target) and Dismiss (acknowledged
 * locally by [AlertService]) actions. The text comes from [AlertPresenter]; an alert without
 * triggering context posts nothing.
 */
class AlertNotifier(private val context: Context) {
    private val manager: NotificationManager = context.getSystemService(NotificationManager::class.java)

    fun show(alert: Alert) {
        val text = AlertPresenter.text(alert) ?: return
        if (Build.VERSION.SDK_INT >= 33 &&
            ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) return
        ensureChannel()
        val alertId = alert.envelope.id
        val flags = PendingIntent.FLAG_UPDATE_CURRENT or if (Build.VERSION.SDK_INT >= 23) PendingIntent.FLAG_IMMUTABLE else 0
        // Intent data carries full alert identity: PendingIntent identity ignores extras, so the
        // data URI (plus a strong request code) keeps distinct alerts' actions from merging.
        val watch = Intent(context, WatchActivity::class.java)
            .setData(Uri.parse(actionData(alertId, "watch")))
            .putExtra(EXTRA_ALERT_ID, alertId)
            .putExtra(EXTRA_EVENT_ID, watchEventId(alert))
        val dismiss = Intent(context, AlertService::class.java)
            .setAction(AlertService.ACTION_DISMISS)
            .setData(Uri.parse(actionData(alertId, "dismiss")))
            .putExtra(EXTRA_ALERT_ID, alertId)
        val body = listOfNotNull(text.context.ifEmpty { null }, text.access, text.commentary).joinToString("\n")
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setColor(TvPalette.alertArgb)
            .setContentTitle(text.headline)
            .setContentText(text.context)
            .setStyle(NotificationCompat.BigTextStyle().bigText(body))
            .setCategory(NotificationCompat.CATEGORY_EVENT)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .addAction(android.R.drawable.ic_media_play, "Watch", PendingIntent.getActivity(context, requestCode(alertId, 1), watch, flags))
            .addAction(android.R.drawable.ic_menu_close_clear_cancel, "Dismiss", PendingIntent.getService(context, requestCode(alertId, 2), dismiss, flags))
            .build()
        // The tag carries full alert identity, so an int-id collision can never replace another alert.
        manager.notify(notificationTag(alertId), notificationId(alertId), notification)
    }

    fun cancel(alertId: String) = manager.cancel(notificationTag(alertId), notificationId(alertId))

    private fun ensureChannel() {
        if (Build.VERSION.SDK_INT < 26) return
        if (manager.getNotificationChannel(CHANNEL_ID) != null) return
        manager.createNotificationChannel(
            NotificationChannel(CHANNEL_ID, "Game alerts", NotificationManager.IMPORTANCE_HIGH)
                .apply { description = "Fantasy game alerts with Watch and Dismiss actions" },
        )
    }

    companion object {
        const val CHANNEL_ID = "afc-alerts"
        const val EXTRA_ALERT_ID = "com.afc.companion.alerts.ALERT_ID"
        const val EXTRA_EVENT_ID = "com.afc.companion.alerts.EVENT_ID"

        /** The server carries the event ID in triggerContext; the data-level key is a legacy fallback. */
        internal fun watchEventId(alert: Alert): String? =
            ((alert.envelope.data.opt("triggerContext") as? JSONObject)?.opt("eventId") as? String)?.validEventId()
                ?: (alert.envelope.data.opt("eventId") as? String)?.validEventId()

        private fun String.validEventId(): String? = takeIf { it.isNotBlank() && it.length in 1..256 }

        internal fun notificationTag(alertId: String): String = "alert:$alertId"

        internal fun notificationId(alertId: String): Int = stableInt("alert:$alertId")

        internal fun requestCode(alertId: String, action: Int): Int = stableInt("alert:$alertId:$action")

        internal fun actionData(alertId: String, action: String): String =
            "afc://alerts/$action/${URLEncoder.encode(alertId, "UTF-8")}"

        // SHA-256 prefix, not String.hashCode: ids such as "Aa"/"BB" collide under hashCode.
        private fun stableInt(value: String): Int {
            val digest = MessageDigest.getInstance("SHA-256").digest(value.toByteArray(Charsets.UTF_8))
            return (digest[0].toInt() and 0xFF shl 24) or (digest[1].toInt() and 0xFF shl 16) or
                (digest[2].toInt() and 0xFF shl 8) or (digest[3].toInt() and 0xFF)
        }
    }
}

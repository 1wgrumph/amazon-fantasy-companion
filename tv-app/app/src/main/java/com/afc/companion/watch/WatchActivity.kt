package com.afc.companion.watch

import android.app.Activity
import android.app.AlertDialog
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.ColorDrawable
import android.graphics.drawable.GradientDrawable
import android.graphics.drawable.StateListDrawable
import android.os.Bundle
import android.view.ViewGroup
import android.widget.TextView
import com.afc.companion.BuildConfig
import com.afc.companion.Shell
import com.afc.companion.alerts.AlertInbox
import com.afc.companion.alerts.AlertNotifier
import com.afc.companion.net.SessionStore
import com.afc.companion.panel.panelModeFor
import com.afc.companion.profile.ProfileStore
import com.afc.companion.ui.theme.TvFocusStyle
import com.afc.companion.ui.theme.TvSafeZone
import kotlin.coroutines.resume
import kotlinx.coroutines.CancellableContinuation
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import kotlinx.coroutines.suspendCancellableCoroutine

/** The notification's Watch target: one [WatchLauncher.watchAlert] attempt for the alert, then finish. */
class WatchActivity : Activity() {
    private val prompt = SwitchPrompt()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val eventId = intent.getStringExtra(AlertNotifier.EXTRA_EVENT_ID)
        val client = Shell().client(BuildConfig.AFC_API_BASE_URL, SessionStore(this)::token)
        // A recreated activity never starts a second attempt (AFC-PR-031).
        if (savedInstanceState != null || eventId == null || client == null) {
            finish()
            return
        }
        val route = AlertInbox.find(intent.getStringExtra(AlertNotifier.EXTRA_ALERT_ID))?.route
        // Not tied to this noHistory activity: the outcome report must outlive it once the provider starts.
        CoroutineScope(SupervisorJob() + Dispatchers.Main).launch {
            val switchingConfirm = ProfileStore(client).load()?.switchingConfirm ?: true
            WatchLauncher(this@WatchActivity)
                .watchAlert(eventId, route, client, switchingConfirm, panelModeFor(null), ::confirmSwitch)
            finish()
        }
    }

    override fun onDestroy() {
        prompt.cancel()
        super.onDestroy()
    }

    private suspend fun confirmSwitch(): Boolean = prompt.ask { answer ->
        val dialog = AlertDialog.Builder(this)
            .setMessage("Switch to the provider app to watch?")
            .setPositiveButton("Watch") { _, _ -> answer(true) }
            .setNegativeButton("Cancel") { _, _ -> answer(false) }
            .setOnCancelListener { answer(false) }
            .show()
        val metrics = resources.displayMetrics
        val (horizontal, vertical) = TvSafeZone.insets(metrics.widthPixels / metrics.density, metrics.heightPixels / metrics.density)
        dialog.window?.apply {
            setBackgroundDrawable(ColorDrawable(Color.rgb(16, 20, 24)))
            setLayout((metrics.widthPixels - 2 * horizontal * metrics.density).toInt(), ViewGroup.LayoutParams.WRAP_CONTENT)
            decorView.setPadding(24, (vertical * metrics.density).toInt(), 24, (vertical * metrics.density).toInt())
        }
        dialog.findViewById<TextView>(android.R.id.message)?.apply {
            setTextColor(Color.rgb(229, 233, 237))
            textSize = 18f
            typeface = Typeface.DEFAULT
        }
        for (which in listOf(AlertDialog.BUTTON_POSITIVE, AlertDialog.BUTTON_NEGATIVE)) {
            dialog.getButton(which).apply {
                setTextColor(Color.rgb(229, 233, 237))
                textSize = 16f
                typeface = Typeface.DEFAULT_BOLD
                background = StateListDrawable().apply {
                    for (focused in listOf(true, false)) {
                        addState(if (focused) intArrayOf(android.R.attr.state_focused) else intArrayOf(), GradientDrawable().apply {
                            setColor(Color.rgb(26, 32, 39))
                            cornerRadius = 8 * metrics.density
                            setStroke((TvFocusStyle.borderWidthDp * metrics.density).toInt(),
                                if (focused) TvFocusStyle.focusedBorderArgb else TvFocusStyle.unfocusedBorderArgb)
                        })
                    }
                }
                setOnFocusChangeListener { view, focused ->
                    view.scaleX = if (focused) TvFocusStyle.scale else 1f
                    view.scaleY = if (focused) TvFocusStyle.scale else 1f
                }
            }
        }
        dialog::dismiss
    }
}

/**
 * One switching confirmation, main thread only. [cancel] (the activity is destroyed) closes a pending
 * dialog and declines, so neither the dialog window nor the waiting coroutine outlives the activity;
 * a later [ask] declines without showing anything.
 */
internal class SwitchPrompt {
    private var pending: CancellableContinuation<Boolean>? = null
    private var close: (() -> Unit)? = null
    private var cancelled = false

    /** [show] displays the question, calls its argument with the answer and returns how to close it. */
    suspend fun ask(show: (answer: (Boolean) -> Unit) -> () -> Unit): Boolean {
        if (cancelled) return false
        return suspendCancellableCoroutine { waiting ->
            pending = waiting
            val closer = show { yes -> resolve(waiting, yes) }
            if (pending === waiting) close = closer
        }
    }

    fun cancel() {
        cancelled = true
        val waiting = pending ?: return
        close?.invoke()
        resolve(waiting, false)
    }

    private fun resolve(waiting: CancellableContinuation<Boolean>, yes: Boolean) {
        if (pending !== waiting) return
        pending = null
        close = null
        if (waiting.isActive) waiting.resume(yes)
    }
}

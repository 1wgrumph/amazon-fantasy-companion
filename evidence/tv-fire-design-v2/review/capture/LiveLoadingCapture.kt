package com.afc.companion.visual
import android.content.Intent
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.ui.Modifier
import androidx.test.core.app.ActivityScenario
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.UiDevice
import com.afc.companion.ui.theme.*
import java.io.File
import org.junit.Assert.assertTrue
import org.junit.Test

/** Default Android frame clock, outside Compose test-clock control. Synthetic UI only. */
class LiveLoadingCapture {
    @Test fun captureLiveMotion() {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val intent = Intent(instrumentation.targetContext, ComponentActivity::class.java)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        ActivityScenario.launch<ComponentActivity>(intent).use { scenario ->
            scenario.onActivity { activity ->
                activity.setContent { AfcTheme {
                    androidx.compose.foundation.layout.Box(Modifier.fillMaxSize().afcBackground()) {
                        AfcLoadingIndicator("Loading profile…")
                    }
                } }
            }
            Thread.sleep(1000)
            val device = UiDevice.getInstance(instrumentation)
            for (i in 1..3) {
                assertTrue(device.takeScreenshot(File(instrumentation.targetContext.cacheDir, "review-v2-live-$i.png")))
                Thread.sleep(350)
            }
        }
    }
}

package com.afc.spike.sp4;

import android.app.Activity;
import android.app.PictureInPictureParams;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.Bundle;
import android.provider.Settings;
import android.util.Log;
import android.util.Rational;
import android.view.Gravity;
import android.widget.FrameLayout;
import android.widget.TextView;

public class MainActivity extends Activity {
    static final String TAG = "SP4SPIKE";

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.BLACK);
        TextView panel = new TextView(this);
        panel.setBackgroundColor(Color.rgb(20, 60, 120));
        panel.setTextColor(Color.WHITE);
        panel.setTextSize(24);
        panel.setGravity(Gravity.CENTER);
        panel.setText("SP4 PANEL\n(fixture text)");
        FrameLayout.LayoutParams p = new FrameLayout.LayoutParams(480, FrameLayout.LayoutParams.MATCH_PARENT, Gravity.END);
        root.addView(panel, p);
        setContentView(root);
        Log.i(TAG, "onCreate pipFeature=" + getPackageManager().hasSystemFeature(PackageManager.FEATURE_PICTURE_IN_PICTURE)
            + " canDrawOverlays=" + Settings.canDrawOverlays(this)
            + " multiWindow=" + isInMultiWindowMode() + " pip=" + isInPictureInPictureMode());
        apply(getIntent());
    }

    @Override public void onNewIntent(Intent intent) { super.onNewIntent(intent); apply(intent); }

    private void apply(Intent intent) {
        String mode = intent == null ? null : intent.getStringExtra("mode");
        Log.i(TAG, "apply mode=" + mode);
        if ("pip".equals(mode)) {
            try {
                boolean ok = enterPictureInPictureMode(new PictureInPictureParams.Builder()
                    .setAspectRatio(new Rational(16, 9)).build());
                Log.i(TAG, "enterPictureInPictureMode returned " + ok);
            } catch (Throwable t) {
                Log.i(TAG, "enterPictureInPictureMode threw " + t.getClass().getSimpleName() + ": " + t.getMessage());
            }
        } else if ("overlay".equals(mode)) {
            startService(new Intent(this, PanelService.class));
            Log.i(TAG, "started PanelService canDrawOverlays=" + Settings.canDrawOverlays(this));
        }
    }

    @Override public void onPictureInPictureModeChanged(boolean inPip) {
        super.onPictureInPictureModeChanged(inPip);
        Log.i(TAG, "onPictureInPictureModeChanged inPip=" + inPip);
    }

    @Override public void onMultiWindowModeChanged(boolean inMw) {
        super.onMultiWindowModeChanged(inMw);
        Log.i(TAG, "onMultiWindowModeChanged inMw=" + inMw);
    }
}

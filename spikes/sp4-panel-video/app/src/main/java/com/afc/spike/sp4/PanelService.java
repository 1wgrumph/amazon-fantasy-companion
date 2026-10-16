package com.afc.spike.sp4;

import android.app.Service;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.os.IBinder;
import android.provider.Settings;
import android.util.Log;
import android.view.Gravity;
import android.view.WindowManager;
import android.widget.TextView;

public class PanelService extends Service {
    private TextView view;

    @Override public int onStartCommand(Intent intent, int flags, int id) {
        boolean allowed = Settings.canDrawOverlays(this);
        Log.i(MainActivity.TAG, "PanelService canDrawOverlays=" + allowed);
        try {
            view = new TextView(this);
            view.setBackgroundColor(Color.rgb(120, 40, 20));
            view.setTextColor(Color.WHITE);
            view.setTextSize(24);
            view.setGravity(Gravity.CENTER);
            view.setText("SP4 OVERLAY PANEL");
            WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                480, WindowManager.LayoutParams.MATCH_PARENT,
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE, PixelFormat.OPAQUE);
            lp.gravity = Gravity.END;
            getSystemService(WindowManager.class).addView(view, lp);
            Log.i(MainActivity.TAG, "PanelService addView TYPE_APPLICATION_OVERLAY succeeded");
        } catch (Throwable t) {
            Log.i(MainActivity.TAG, "PanelService addView threw " + t.getClass().getSimpleName() + ": " + t.getMessage());
        }
        return START_STICKY;
    }

    @Override public void onDestroy() {
        if (view != null) try { getSystemService(WindowManager.class).removeView(view); } catch (Throwable t) { Log.i(MainActivity.TAG, "removeView " + t.getMessage()); }
        Log.i(MainActivity.TAG, "PanelService destroyed");
    }

    @Override public IBinder onBind(Intent intent) { return null; }
}

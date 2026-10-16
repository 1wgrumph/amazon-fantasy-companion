package com.afc.spike.sp2;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.widget.TextView;

public class MainActivity extends Activity {
    static final String TAG = "SP2SPIKE";

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        String via = getIntent() != null ? getIntent().getStringExtra("via") : null;
        Log.i(TAG, "activity launched via=" + via);
        TextView t = new TextView(this);
        t.setBackgroundColor(Color.rgb(20, 60, 120));
        t.setTextColor(Color.WHITE);
        t.setTextSize(28);
        t.setGravity(Gravity.CENTER);
        t.setText("SP2 SPIKE ACTIVITY\nvia=" + (via == null ? "direct" : via));
        setContentView(t);
        // Starting the activity also arms the service, so the spike needs one launch only.
        startForegroundService(new Intent(this, NotifyService.class).setAction(NotifyService.ACTION_POST));
    }

    @Override protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        Log.i(TAG, "activity onNewIntent via=" + intent.getStringExtra("via"));
    }
}

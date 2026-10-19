package com.afc.sp7fixture;

import android.app.Activity;
import android.content.ComponentName;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;

// Disposable own-package fixture: disables ONLY itself via the normal app API.
public final class MainActivity extends Activity {
    private static final String TAG = "Sp7Fixture";

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        TextView out = new TextView(this);
        out.setText("sp7fixture: self-disable pending");
        setContentView(out);
        String result;
        try {
            // Own package only; never another package.
            if (!getPackageName().equals("com.afc.sp7fixture")) throw new IllegalStateException("not own package");
            getPackageManager().setApplicationEnabledSetting(
                    getPackageName(), PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                    PackageManager.DONT_KILL_APP);
            result = "self-disable call returned";
        } catch (Exception e) {
            result = "self-disable denied: " + e.getClass().getSimpleName();
        }
        Log.i(TAG, result);
        out.setText("sp7fixture: " + result);
    }
}

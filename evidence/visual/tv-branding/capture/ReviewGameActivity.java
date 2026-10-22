package com.afc.companion.review;
import android.app.Activity;
import android.os.Bundle;
import android.view.KeyEvent;
import android.widget.TextView;
import android.graphics.Color;
public class ReviewGameActivity extends Activity {
    private TextView label;
    private int keys;
    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        label = new TextView(this);
        label.setText("SYNTHETIC GAME\nSynthetic stand-in app for the overlay capture\nRemote keys received: 0");
        label.setTextColor(Color.WHITE); label.setTextSize(30); label.setPadding(90,90,90,90);
        label.setBackgroundColor(Color.rgb(17,65,54)); setContentView(label);
    }
    @Override public boolean onKeyDown(int code, KeyEvent event) {
        if (code == KeyEvent.KEYCODE_DPAD_CENTER || code == KeyEvent.KEYCODE_DPAD_DOWN) {
            keys++; label.setText("SYNTHETIC GAME\nSynthetic stand-in app for the overlay capture\nRemote keys received: " + keys); return true;
        }
        return super.onKeyDown(code,event);
    }
}

package com.afc.companion.panel;
import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.view.KeyEvent;
import android.widget.TextView;
import android.graphics.Color;
import java.io.File;
import java.io.FileWriter;
public class CornerGameActivity extends Activity {
    private TextView label;
    private int downs, ups, other;
    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        label = new TextView(this);
        label.setTextSize(28); label.setPadding(100,180,100,100);
        setContentView(label); paint(getIntent());
    }
    @Override public void onNewIntent(Intent intent) { super.onNewIntent(intent); paint(intent); }
    private void paint(Intent intent) {
        boolean dark = intent.getBooleanExtra("dark", false);
        label.setBackgroundColor(dark ? Color.rgb(12,24,38) : Color.rgb(240,246,251));
        label.setTextColor(dark ? Color.WHITE : Color.rgb(15,30,45));
        label.setText("SYNTHETIC GAME — CORNER CARD REGRESSION\nFictional fixture, no provider app\nMenu downs: " + downs + "   Menu ups: " + ups + "   Other remote keys: " + other);
    }
    @Override public boolean dispatchKeyEvent(KeyEvent e) {
        if (e.getKeyCode() == KeyEvent.KEYCODE_MENU) {
            if (e.getAction() == KeyEvent.ACTION_DOWN) downs++; else if (e.getAction() == KeyEvent.ACTION_UP) ups++;
            try (FileWriter f = new FileWriter(new File(getExternalFilesDir(null), "menu-events.txt"), true)) {
                f.write("action=" + e.getAction() + " repeat=" + e.getRepeatCount() + " flags=" + e.getFlags() + " eventTime=" + e.getEventTime() + " held=" + (e.getEventTime()-e.getDownTime()) + "\n");
            } catch (Exception ex) { throw new RuntimeException(ex); }
            paint(getIntent()); return true;
        }
        if (e.getAction() == KeyEvent.ACTION_DOWN && (e.getKeyCode()==KeyEvent.KEYCODE_DPAD_CENTER || e.getKeyCode()==KeyEvent.KEYCODE_DPAD_DOWN)) {
            other++; paint(getIntent()); return true;
        }
        return super.dispatchKeyEvent(e);
    }
}

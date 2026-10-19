package com.afc.sp7probe;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.util.List;

public final class MainActivity extends Activity {
    private static final String TAG = "Sp7Probe";

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setGravity(Gravity.TOP);
        int pad = (int) (16 * getResources().getDisplayMetrics().density);
        root.setPadding(pad, pad, pad, pad);

        TextView title = new TextView(this);
        title.setText("SP7 detection probe (offline prep; X07 NOT_RUN on device)");
        root.addView(title);

        CheckBox optIn = new CheckBox(this);
        optIn.setText("Enable package queries (default OFF: zero queries)");
        optIn.setChecked(false);
        root.addView(optIn);

        TextView out = new TextView(this);
        out.setText("NOT_QUERIED");
        root.addView(out);

        Button run = new Button(this);
        run.setText("Run probe");
        run.setOnClickListener(v -> {
            boolean enabled = optIn.isChecked();
            List<ProbeLogic.Result> results =
                    ProbeLogic.probeAll(enabled, new AndroidPackageQuery(this));
            StringBuilder sb = new StringBuilder();
            for (ProbeLogic.Result r : results) {
                sb.append(r.packageName).append(' ').append(r.status).append('\n');
                Log.i(TAG, r.packageName + " " + r.status);
            }
            out.setText(sb.toString().trim());
        });
        root.addView(run);
        setContentView(root);
    }
}

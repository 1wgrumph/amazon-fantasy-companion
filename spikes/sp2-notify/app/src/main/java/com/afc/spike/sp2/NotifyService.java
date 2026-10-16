package com.afc.spike.sp2;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.util.Log;
import android.widget.Toast;

/** Posts the AFC-PR-015 heads-up alert shape (framework APIs only, no dependencies). */
public class NotifyService extends Service {
    static final String TAG = "SP2SPIKE";
    static final String ACTION_POST = "com.afc.spike.sp2.POST";
    static final String ACTION_POST_FSI = "com.afc.spike.sp2.POST_FSI";
    static final String ACTION_POST_DELAYED = "com.afc.spike.sp2.POST_DELAYED";
    static final String ACTION_DISMISS = "com.afc.spike.sp2.DISMISS";
    static final String ACTION_TOAST = "com.afc.spike.sp2.TOAST";
    // v2: channel settings are immutable after creation, so the sound/vibrate retry needs a new id.
    static final String CHANNEL_ID = "sp2-alerts-v2";
    static final int FGS_ID = 2001;
    static final int ALERT_ID = 2002;

    @Override public IBinder onBind(Intent intent) { return null; }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        ensureChannel();
        startForeground(FGS_ID, new Notification.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setPriority(Notification.PRIORITY_LOW)
            .setContentTitle("SP2 spike service running").build());
        String action = intent != null ? intent.getAction() : null;
        Log.i(TAG, "service action=" + action
            + " sdk=" + Build.VERSION.SDK_INT
            + " postNotifGranted=" + (Build.VERSION.SDK_INT < 33
                || checkSelfPermission("android.permission.POST_NOTIFICATIONS") == PackageManager.PERMISSION_GRANTED));
        if (ACTION_DISMISS.equals(action)) {
            getSystemService(NotificationManager.class).cancel(ALERT_ID);
            Log.i(TAG, "DISMISS pressed: alert cancelled");
            Toast.makeText(this, "SP2 Dismiss pressed", Toast.LENGTH_SHORT).show();
        } else if (ACTION_TOAST.equals(action)) {
            Toast.makeText(this, "SP2 toast fallback: Watch/Dismiss unavailable", Toast.LENGTH_LONG).show();
            Log.i(TAG, "TOAST posted");
        } else if (ACTION_POST_DELAYED.equals(action)) {
            // Delay lets the operator foreground Prime Video before the alert posts.
            long delay = intent.getLongExtra("delay_ms", 8000);
            Log.i(TAG, "POST scheduled in " + delay + "ms");
            new Handler(Looper.getMainLooper()).postDelayed(this::postAlert, delay);
        } else if (ACTION_POST_FSI.equals(action)) {
            postAlertFsi();
        } else {
            postAlert();
        }
        return START_STICKY;
    }

    private void postAlert() {
        int piFlags = PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE;
        PendingIntent watch = PendingIntent.getActivity(this, 1,
            new Intent(this, MainActivity.class).putExtra("via", "WATCH")
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK), piFlags);
        PendingIntent dismiss = PendingIntent.getService(this, 2,
            new Intent(this, NotifyService.class).setAction(ACTION_DISMISS), piFlags);
        Notification alert = new Notification.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            // Fire TV heads-up guide requires PRIORITY_HIGH on top of IMPORTANCE_HIGH.
            .setPriority(Notification.PRIORITY_HIGH)
            // Android peeks a heads-up only for IMPORTANCE_HIGH + sound/vibrate; give it both.
            .setDefaults(Notification.DEFAULT_SOUND | Notification.DEFAULT_VIBRATE)
            .setContentTitle("SP2 test alert: player in the red zone")
            .setContentText("Fixture alert with Watch and Dismiss")
            .setCategory(Notification.CATEGORY_EVENT)
            .setAutoCancel(true)
            .setContentIntent(watch)
            .addAction(new Notification.Action.Builder(android.R.drawable.ic_media_play, "Watch", watch).build())
            .addAction(new Notification.Action.Builder(android.R.drawable.ic_menu_close_clear_cancel, "Dismiss", dismiss).build())
            .build();
        getSystemService(NotificationManager.class).notify(ALERT_ID, alert);
        Log.i(TAG, "ALERT posted id=" + ALERT_ID);
    }

    private void postAlertFsi() {
        int piFlags = PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE;
        PendingIntent watch = PendingIntent.getActivity(this, 1,
            new Intent(this, MainActivity.class).putExtra("via", "WATCH")
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK), piFlags);
        PendingIntent dismiss = PendingIntent.getService(this, 2,
            new Intent(this, NotifyService.class).setAction(ACTION_DISMISS), piFlags);
        PendingIntent fsi = PendingIntent.getActivity(this, 3,
            new Intent(this, MainActivity.class).putExtra("via", "FSI")
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK), piFlags);
        Notification alert = new Notification.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setPriority(Notification.PRIORITY_HIGH)
            .setDefaults(Notification.DEFAULT_SOUND | Notification.DEFAULT_VIBRATE)
            .setContentTitle("SP2 FSI test alert: player in the red zone")
            .setContentText("Fixture FSI alert with Watch and Dismiss")
            .setCategory(Notification.CATEGORY_EVENT)
            .setAutoCancel(true)
            .setContentIntent(watch)
            .setFullScreenIntent(fsi, true)
            .addAction(new Notification.Action.Builder(android.R.drawable.ic_media_play, "Watch", watch).build())
            .addAction(new Notification.Action.Builder(android.R.drawable.ic_menu_close_clear_cancel, "Dismiss", dismiss).build())
            .build();
        getSystemService(NotificationManager.class).notify(ALERT_ID, alert);
        Log.i(TAG, "ALERT_FSI posted id=" + ALERT_ID);
    }

    private void ensureChannel() {
        NotificationManager m = getSystemService(NotificationManager.class);
        if (m.getNotificationChannel(CHANNEL_ID) == null) {
            NotificationChannel ch = new NotificationChannel(
                CHANNEL_ID, "SP2 game alerts", NotificationManager.IMPORTANCE_HIGH);
            ch.setSound(android.media.RingtoneManager.getDefaultUri(
                android.media.RingtoneManager.TYPE_NOTIFICATION), null);
            ch.setVibrationPattern(new long[]{0, 250});
            m.createNotificationChannel(ch);
        }
    }
}

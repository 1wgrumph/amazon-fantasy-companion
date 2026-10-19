package com.afc.sp7probe;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;

public final class AndroidPackageQuery implements PackageQuery {
    private final PackageManager pm;

    public AndroidPackageQuery(Context context) {
        this.pm = context.getPackageManager();
    }

    @Override public Info query(String packageName) throws Exception {
        try {
            ApplicationInfo ai = pm.getApplicationInfo(packageName, 0);
            pm.getPackageInfo(packageName, 0);
            return new Info(true, ai.enabled);
        } catch (PackageManager.NameNotFoundException e) {
            return new Info(false, false);
        }
    }
}

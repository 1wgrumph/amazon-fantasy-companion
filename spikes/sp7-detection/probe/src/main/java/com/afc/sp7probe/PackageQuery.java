package com.afc.sp7probe;

// Tiny seam so host self-checks can count/verify query calls without Android.
public interface PackageQuery {
    Info query(String packageName) throws Exception;

    final class Info {
        public final boolean present;
        public final boolean enabled;

        public Info(boolean present, boolean enabled) {
            this.present = present;
            this.enabled = enabled;
        }
    }
}

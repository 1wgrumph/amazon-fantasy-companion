package com.afc.sp7probe;

import java.util.ArrayList;
import java.util.List;

public final class ProbeLogic {
    public enum Status { INSTALLED_ENABLED, INSTALLED_DISABLED, ABSENT, UNKNOWN, NOT_QUERIED }

    public static final String PRIME = "com.amazon.firebat";
    public static final String NETFLIX = "com.netflix.ninja";
    public static final String ABSENT_CONTROL = "com.example.absent.afcprobe";
    public static final String OWNED_FIXTURE = "com.afc.sp7fixture";
    public static final List<String> ALLOWLIST = List.of(PRIME, NETFLIX, ABSENT_CONTROL, OWNED_FIXTURE);

    public static final class Result {
        public final String packageName;
        public final Status status;

        public Result(String packageName, Status status) {
            this.packageName = packageName;
            this.status = status;
        }

        @Override public String toString() { return packageName + " " + status; }
    }

    private ProbeLogic() {}

    public static Result probeOne(String packageName, boolean optIn, PackageQuery query) {
        if (!optIn) return new Result(packageName, Status.NOT_QUERIED);
        if (packageName == null || !ALLOWLIST.contains(packageName)) {
            throw new IllegalArgumentException("package not in fixed allowlist");
        }
        if (query == null) return new Result(packageName, Status.UNKNOWN);
        try {
            PackageQuery.Info info = query.query(packageName);
            if (info == null) return new Result(packageName, Status.UNKNOWN);
            if (!info.present) return new Result(packageName, Status.ABSENT);
            return new Result(packageName, info.enabled ? Status.INSTALLED_ENABLED : Status.INSTALLED_DISABLED);
        } catch (Exception e) {
            return new Result(packageName, Status.UNKNOWN);
        }
    }

    public static List<Result> probeAll(boolean optIn, PackageQuery query) {
        List<Result> out = new ArrayList<>();
        for (String pkg : ALLOWLIST) out.add(probeOne(pkg, optIn, query));
        return out;
    }

    // Synthetic helper guard: self-disable may target only the caller's own package.
    public static void requireSelfPackage(String target, String ownPackage) {
        if (target == null || ownPackage == null || !target.equals(ownPackage)) {
            throw new IllegalArgumentException("self-disable target must be own package");
        }
    }
}

package com.afc.sp7probe;

import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

public final class ProbeSelfCheck {
    public static void main(String[] args) {
        // OFF: zero queries
        AtomicInteger calls = new AtomicInteger();
        PackageQuery counting = pkg -> { calls.incrementAndGet(); return new PackageQuery.Info(true, true); };
        List<ProbeLogic.Result> off = ProbeLogic.probeAll(false, counting);
        check(calls.get() == 0, "OFF must make zero queries, got " + calls.get());
        check(off.stream().allMatch(r -> r.status == ProbeLogic.Status.NOT_QUERIED), "OFF all NOT_QUERIED");

        // ON allowlist paths
        PackageQuery fake = pkg -> {
            if (ProbeLogic.PRIME.equals(pkg)) return new PackageQuery.Info(true, true);
            if (ProbeLogic.NETFLIX.equals(pkg)) return new PackageQuery.Info(true, false);
            return new PackageQuery.Info(false, false);
        };
        List<ProbeLogic.Result> on = ProbeLogic.probeAll(true, fake);
        check(on.get(0).status == ProbeLogic.Status.INSTALLED_ENABLED, "prime enabled");
        check(on.get(1).status == ProbeLogic.Status.INSTALLED_DISABLED, "netflix disabled");
        check(on.get(2).status == ProbeLogic.Status.ABSENT, "absent control ABSENT");

        // arbitrary rejection before query
        AtomicInteger calls2 = new AtomicInteger();
        PackageQuery counting2 = pkg -> { calls2.incrementAndGet(); return new PackageQuery.Info(true, true); };
        boolean rejected = false;
        try { ProbeLogic.probeOne("com.evil.arbitrary", true, counting2); }
        catch (IllegalArgumentException e) { rejected = true; }
        check(rejected, "arbitrary package rejected");
        check(calls2.get() == 0, "rejection before any query");

        // errors / null -> UNKNOWN, never entitlement
        ProbeLogic.Result err = ProbeLogic.probeOne(ProbeLogic.PRIME, true, pkg -> { throw new RuntimeException("boom"); });
        check(err.status == ProbeLogic.Status.UNKNOWN, "error -> UNKNOWN");
        ProbeLogic.Result nul = ProbeLogic.probeOne(ProbeLogic.PRIME, true, pkg -> null);
        check(nul.status == ProbeLogic.Status.UNKNOWN, "null -> UNKNOWN");
        ProbeLogic.Result noCtx = ProbeLogic.probeOne(ProbeLogic.PRIME, true, null);
        check(noCtx.status == ProbeLogic.Status.UNKNOWN, "null query -> UNKNOWN");

        // self-disable guard: only own package
        ProbeLogic.requireSelfPackage("com.afc.sp7fixture", "com.afc.sp7fixture");
        boolean guard = false;
        try { ProbeLogic.requireSelfPackage(ProbeLogic.NETFLIX, "com.afc.sp7fixture"); }
        catch (IllegalArgumentException e) { guard = true; }
        check(guard, "self-disable rejects provider package");

        System.out.println("ProbeSelfCheck PASS (8 checks)");
    }

    private static void check(boolean cond, String msg) {
        if (!cond) throw new AssertionError(msg);
    }
}

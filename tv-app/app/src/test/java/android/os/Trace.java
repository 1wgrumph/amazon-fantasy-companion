package android.os;

/** Host Compose tests do not emit Android performance traces. */
public final class Trace {
    private Trace() {}
    public static void beginSection(String name) {}
    public static void endSection() {}
}

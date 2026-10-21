allprojects {
    tasks.register("resolveUtpConfigurations") {
        doLast {
            val utp = configurations.filter { it.name.startsWith("unified-test-platform") && it.isCanBeResolved }
            check(utp.isNotEmpty()) { "no unified-test-platform configurations found; UTP resolve check is vacuous" }
            utp.forEach { println("UTP-RESOLVE ${it.name}: ${it.files.size} artifacts verified") }
        }
    }
}

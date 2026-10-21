allprojects {
    tasks.register("resolveUtpConfigurations") {
        doLast {
            configurations.filter { it.name.startsWith("unified-test-platform") && it.isCanBeResolved }
                .forEach { println("UTP-RESOLVE ${it.name}: ${it.files.size} artifacts verified") }
        }
    }
}

buildscript {
    repositories { google(); mavenCentral() }
    configurations.all {
        resolutionStrategy.eachDependency {
            // SD-042: patch the AGP build-host closure; keep the BC family aligned.
            if (requested.group == "org.bouncycastle" &&
                requested.name.matches(Regex("bc(prov|pkix|util)-.*"))) useVersion("1.85")
            if (requested.group == "org.bitbucket.b_c" && requested.name == "jose4j") useVersion("0.9.6")
            if (requested.group == "org.jdom" && requested.name == "jdom2") useVersion("2.0.6.1")
        }
    }
    dependencies {
        classpath(libs.agp)
        classpath(libs.kotlin.gradle.plugin)
        classpath(libs.compose.compiler.gradle.plugin)
    }
}
allprojects {
    configurations.configureEach {
        resolutionStrategy.eachDependency {
            if (requested.group == "org.bouncycastle" &&
                requested.name.matches(Regex("bc(prov|pkix|util)-.*"))) useVersion("1.85")
            if (requested.group == "org.bitbucket.b_c" && requested.name == "jose4j") useVersion("0.9.6")
            if (requested.group == "org.jdom" && requested.name == "jdom2") useVersion("2.0.6.1")
        }
    }
}

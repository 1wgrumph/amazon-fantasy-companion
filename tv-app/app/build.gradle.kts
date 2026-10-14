import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins { id("com.android.application") }

android {
    namespace = "com.afc.companion"
    compileSdk = 34
    buildToolsVersion = "36.0.0"
    defaultConfig {
        applicationId = "com.afc.companion"
        minSdk = 25
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    testOptions.unitTests.all {
        it.systemProperty("afc.repoRoot", rootDir.parentFile.absolutePath)
        it.maxParallelForks = 1
        it.testLogging { events("failed", "passed"); exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL }
    }
}
kotlin { compilerOptions { jvmTarget.set(JvmTarget.JVM_17) } }
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.11.0")
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20260814")
    testImplementation("org.yaml:snakeyaml:2.7")
}

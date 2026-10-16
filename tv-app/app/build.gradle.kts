import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.plugin.compose")
    jacoco
}

// DES-AFC-P2-TV: the base URL is a build property; empty shows "Backend not configured".
val afcApiBaseUrl: String = providers.gradleProperty("afcApiBaseUrl").getOrElse("")
require(afcApiBaseUrl.none { it == '"' || it == '\\' || it.isWhitespace() }) { "afcApiBaseUrl must be a plain URL" }

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
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        buildConfigField("String", "AFC_API_BASE_URL", "\"$afcApiBaseUrl\"")
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
    buildTypes {
        debug { enableUnitTestCoverage = true }
        release {
            isMinifyEnabled = false
            // OA-11 keystore absent: release uses the host debug signer (P2-A01; L05 executes it).
            signingConfig = signingConfigs.getByName("debug")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    packaging { resources { excludes += "/META-INF/{AL2.0,LGPL2.1}" } }
    testOptions.unitTests.all {
        it.systemProperty("afc.repoRoot", rootDir.parentFile.absolutePath)
        it.maxParallelForks = 1
        it.testLogging { events("failed", "passed"); exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL }
    }
}
kotlin { compilerOptions { jvmTarget.set(JvmTarget.JVM_17) } }

// CMD-COVERAGE-TVAPP: repo-owned JaCoCo XML over the debug variant's handwritten classes.
tasks.register<JacocoReport>("afcCoverageReport") {
    dependsOn("testDebugUnitTest")
    val build = layout.buildDirectory
    executionData.setFrom(build.file("outputs/unit_test_code_coverage/debugUnitTest/testDebugUnitTest.exec"))
    sourceDirectories.setFrom(files("src/main/java", "src/main/kotlin"))
    classDirectories.setFrom(build.dir("intermediates/built_in_kotlinc/debug/compileDebugKotlin/classes").map {
        it.asFileTree.matching { exclude("**/BuildConfig.class", "**/ComposableSingletons*", "**/*\$inlined\$*") }
    })
    reports { xml.required.set(true); html.required.set(true); csv.required.set(false) }
}

// CMD-MUTATION-TVAPP: PIT over the debug variant's app classes, JUnit 4 host tests only.
// pl.droidsonroids.pitest 0.2.27 reads the legacy variant API, which AGP 9 exposes only under
// -Pandroid.newDsl=false (plus -Pandroid.onlyEnableUnitTestForTheTestedBuildType=false, because the
// plugin wires every variant). tools/ci/mutation/tvapp.sh passes both on a disposable copy; every other
// build keeps the AGP 9 DSL and never applies the plugin.
if (providers.gradleProperty("android.newDsl").orNull == "false") {
    apply(plugin = "pl.droidsonroids.pitest")
    configure<pl.droidsonroids.gradle.pitest.PitestPluginExtension> {
        pitestVersion.set(libs.versions.pitest.get())
        targetClasses.set(setOf("com.afc.companion.*"))
        // The mockable-android-jar closure (org.json 20080701 and others) carries HIGH CVEs and is not admitted.
        excludeMockableAndroidJar.set(true)
        addJUnitPlatformLauncher.set(false)
        outputFormats.set(setOf("XML", "HTML"))
        timestampedReports.set(false)
        threads.set(2)
        // Stub-contract tests need android.jar, which excludeMockableAndroidJar keeps off the PIT classpath.
        excludedTestClasses.set(setOf("com.afc.companion.StubContractTest"))
        // Same fixture root the unit tests get (testOptions above).
        jvmArgs.set(listOf("-Dafc.repoRoot=${rootDir.parentFile.absolutePath}"))
    }
    // The plugin reads android.sourceSets.main.java.srcDirs, which AGP 9 leaves empty for Kotlin sources.
    afterEvaluate {
        tasks.withType<pl.droidsonroids.gradle.pitest.PitestTask>().configureEach {
            sourceDirs.setFrom(files("src/main/java", "src/main/kotlin"))
        }
    }
}

dependencies {
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.foundation)
    implementation(libs.tv.material)
    testImplementation(libs.junit)
    testImplementation(libs.org.json)
    testImplementation(libs.snakeyaml)
    androidTestImplementation(platform(libs.compose.bom))
    androidTestImplementation(libs.compose.ui.test.junit4)
    androidTestImplementation(libs.androidx.test.runner)
    androidTestImplementation(libs.androidx.test.ext.junit)
    androidTestImplementation(libs.androidx.test.uiautomator)
    debugImplementation(libs.compose.ui.test.manifest)
}

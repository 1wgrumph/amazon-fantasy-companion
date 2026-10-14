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

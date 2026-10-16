plugins { id("com.android.application") }

android {
    namespace = "com.afc.spike.sp4"
    compileSdk = 34
    buildToolsVersion = "36.0.0"
    defaultConfig {
        applicationId = "com.afc.spike.sp4"
        minSdk = 25
        targetSdk = 34
        versionCode = 1
        versionName = "0.1.0"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

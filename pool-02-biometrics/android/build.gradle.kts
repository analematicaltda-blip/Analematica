plugins { id("com.android.library") }
android {
    namespace = "co.analematica.approval"
    compileSdk = 35
    defaultConfig { minSdk = 31 }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
}

dependencies { api(project(":integrity")) }

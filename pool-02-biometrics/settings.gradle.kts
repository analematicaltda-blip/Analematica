pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositories { google(); mavenCentral() } }
rootProject.name = "sgacd-native-approval"
include(":android")

include(":integrity")
project(":integrity").projectDir = file("../pool-03-integrity/android")

include(":protection")
project(":protection").projectDir = file("../pool-04-anti-phishing/android")

pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositories { google(); mavenCentral() } }
rootProject.name = "sgacd-local-vault"
include(":android")

include(":integrity")
project(":integrity").projectDir = file("../pool-03-integrity/android")

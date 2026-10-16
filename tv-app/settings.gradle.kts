import org.gradle.api.initialization.resolve.RepositoriesMode
import org.gradle.api.artifacts.verification.DependencyVerificationMode

// SD-041: fail closed before external build plugins are admitted.
gradle.startParameter.dependencyVerificationMode = DependencyVerificationMode.STRICT
pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "AmazonFantasyCompanion"
include(":app")

package com.afc.companion

import java.nio.file.Files
import org.junit.Assert.*
import org.junit.Test

class ShellContractTest {
    @Test fun buildDeclaresMinSdk25() {
        assertTrue("AFC-PR-053", Regex("minSdk\\s*=\\s*25\\b").containsMatchIn(Files.readAllBytes(repo.resolve("tv-app/app/build.gradle.kts")).toString(Charsets.UTF_8)))
    }
    @Test fun exposesOnlyLinkProfileAndPanelNavigation() {
        assertEquals("Missing behavior: shell navigation without social surfaces", setOf("Link", "Profile/Settings", "Panel"), Shell().destinations())
    }
    @Test fun noMessagingEndpointsInFrozenContract() {
        assertEquals(setOf("/v1/link", "/v1/link/confirm", "/link", "/v1/profile", "/v1/alerts", "/v1/panel", "/v1/providers", "/v1/routing-outcome", "/v1/installed-apps", "/v1/lineup/manual"), node("paths").keys)
    }
    @Test fun committedTestTokensDoNotMatchCredentialShapes() {
        val assignment = "[\\\"']?\\s*[:=]\\s*[\\\"']?"
        val rules = listOf(
            Regex("\\b(?:AKIA|ASIA)[A-Z0-9]{16}\\b"),
            Regex("\\b(?:access_token|refresh_token|device_token)" + assignment + "[A-Za-z0-9._/+\\-]{32,}", RegexOption.IGNORE_CASE),
            Regex("\\b(?:aws_secret_access_key|yahoo_client_secret)" + assignment + "[A-Za-z0-9._/+\\-]{40,}", RegexOption.IGNORE_CASE),
            Regex("\\bsessionToken" + assignment + "[A-Za-z0-9._/+\\-]{32,}"),
        )
        Files.walk(repo.resolve("tv-app/app/src/test")).use { files ->
            files.filter { Files.isRegularFile(it) }.forEach { path ->
                val source = Files.readAllBytes(path).toString(Charsets.UTF_8)
                assertTrue("CRED-* literal in ${path.fileName}", rules.none { it.containsMatchIn(source) })
            }
        }
    }
}

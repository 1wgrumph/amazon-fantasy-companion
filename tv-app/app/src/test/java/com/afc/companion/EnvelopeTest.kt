package com.afc.companion

import com.afc.companion.net.ApiClient
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized

/** CONTRACT-AFC-P2-ENVELOPE: required fields come from the committed backend contract. */
class EnvelopeTest {
    private val client = ApiClient("http://127.0.0.1")
    @Test fun decodesAllRequiredFieldsWithoutLosingProvenance() = runBlocking {
        val input = envelopeFixture().put("eventTime", "2026-10-14T11:59:00Z")
        val required = node("components", "schemas", "Envelope")["required"] as List<*>
        assertTrue(required.all { input.has(it.toString()) })
        val result = client.envelope(input)
        assertNotNull("Missing behavior: decode the frozen envelope", result)
        result!!
        assertEquals(1, result.schemaVersion); assertEquals("profile-fixture", result.id)
        assertEquals(4L, result.revision); assertEquals("manual", result.source)
        assertEquals(input.getString("updatedAt"), result.updatedAt)
        assertEquals(input.getString("eventTime"), result.eventTime)
        assertTrue(sameJson(input.getJSONObject("data"), result.data))
    }
    @Test fun acceptsEqualRevisionWithoutChangingIdentity() = runBlocking {
        val result = client.envelope(envelopeFixture(), 4)
        assertNotNull("Missing behavior: retry keeps the same entity and revision", result)
        assertEquals("profile-fixture", result!!.id); assertEquals(4L, result.revision); assertNull(result.eventTime)
    }
    @Test fun acceptsNewerRevision() = runBlocking {
        val result = client.envelope(envelopeFixture(5), 4)
        assertNotNull("Missing behavior: accept the newer snapshot", result)
        assertEquals(5L, result!!.revision)
    }
    @Test fun rejectsOlderRevision() = runBlocking { assertNull(client.envelope(envelopeFixture(3), 4)) }
    @Test fun rejectsUnknownSchemaVersion() = runBlocking { assertNull(client.envelope(envelopeFixture().put("schemaVersion", 999))) }
    @Test fun rejectsUnknownSource() = runBlocking { assertNull(client.envelope(envelopeFixture().put("source", "unverified"))) }
    @Test fun rejectsNegativeRevision() = runBlocking { assertNull(client.envelope(envelopeFixture(-1))) }
    @Test fun rejectsWrongFieldTypes() = runBlocking { assertNull(client.envelope(envelopeFixture().put("revision", "4"))) }
    @Test fun rejectsInvalidFreshnessTimestamp() = runBlocking { assertNull(client.envelope(envelopeFixture().put("updatedAt", "yesterday"))) }
}
@RunWith(Parameterized::class)
class EnvelopeRequiredFieldTest(private val field: String) {
    companion object {
        @JvmStatic @Parameterized.Parameters(name = "missing {0}")
        fun fields(): List<Array<Any>> = (node("components", "schemas", "Envelope")["required"] as List<*>).map { arrayOf(it.toString()) }
    }
    @Test fun rejectsIncompleteEnvelopeWithoutPartialUpdate() = runBlocking {
        val body = envelopeFixture(); body.remove(field)
        assertNull(ApiClient("http://127.0.0.1").envelope(body))
    }
}

@RunWith(Parameterized::class)
class EnvelopeSourceTest(private val source: String) {
    companion object {
        @JvmStatic @Parameterized.Parameters(name = "source {0}")
        fun sources(): List<Array<Any>> = (node("components", "schemas", "Envelope", "properties", "source")["enum"] as List<*>).map { arrayOf(it.toString()) }
    }
    @Test fun preservesEveryOpenApiProvenanceSource() = runBlocking {
        val result = ApiClient("http://127.0.0.1").envelope(envelopeFixture().put("source", source))
        assertNotNull("Missing behavior: preserve $source provenance", result)
        assertEquals(source, result!!.source)
    }
}

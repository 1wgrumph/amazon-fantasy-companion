// CONTRACT-AFC-P2-ENVELOPE: required fields come from the committed backend contract (mirrors EnvelopeTest.kt).
import {decodeEnvelope} from '../../src/net/dto';
import {envelopeFixture, node} from '../support/contract';

const required = node('components', 'schemas', 'Envelope').required as string[];
const sources = node('components', 'schemas', 'Envelope', 'properties', 'source').enum as string[];

describe('EnvelopeTest', () => {
  test('decodesAllRequiredFieldsWithoutLosingProvenance', () => {
    const input: Record<string, any> = {...envelopeFixture(), eventTime: '2026-10-14T11:59:00Z'};
    expect(required.every(field => field in input)).toBe(true);
    const result = decodeEnvelope(input);
    expect(result).not.toBeNull();
    expect(result).toEqual({
      schemaVersion: 1,
      id: 'profile-fixture',
      revision: 4,
      source: 'manual',
      updatedAt: input.updatedAt,
      eventTime: input.eventTime,
      data: input.data,
    });
  });

  test('acceptsEqualRevisionWithoutChangingIdentity', () => {
    const result = decodeEnvelope(envelopeFixture(), 4);
    expect(result).not.toBeNull();
    expect(result?.id).toBe('profile-fixture');
    expect(result?.revision).toBe(4);
    expect(result?.eventTime).toBeNull();
  });

  test('acceptsNewerRevision', () => {
    expect(decodeEnvelope(envelopeFixture(5), 4)?.revision).toBe(5);
  });

  test('rejectsOlderRevision', () => {
    expect(decodeEnvelope(envelopeFixture(3), 4)).toBeNull();
  });

  test('rejectsUnknownSchemaVersion', () => {
    expect(decodeEnvelope({...envelopeFixture(), schemaVersion: 999})).toBeNull();
  });

  test('rejectsUnknownSource', () => {
    expect(decodeEnvelope({...envelopeFixture(), source: 'unverified'})).toBeNull();
  });

  test('rejectsNegativeRevision', () => {
    expect(decodeEnvelope(envelopeFixture(-1))).toBeNull();
  });

  test('rejectsWrongFieldTypes', () => {
    expect(decodeEnvelope({...envelopeFixture(), revision: '4'})).toBeNull();
  });

  test('rejectsInvalidFreshnessTimestamp', () => {
    expect(decodeEnvelope({...envelopeFixture(), updatedAt: 'yesterday'})).toBeNull();
  });
});

describe('EnvelopeRequiredFieldTest', () => {
  test.each(required)('rejectsIncompleteEnvelopeWithoutPartialUpdate[missing %s]', field => {
    const body = envelopeFixture();
    delete body[field];
    expect(decodeEnvelope(body)).toBeNull();
  });
});

describe('EnvelopeSourceTest', () => {
  test.each(sources)('preservesEveryOpenApiProvenanceSource[source %s]', source => {
    const result = decodeEnvelope({...envelopeFixture(), source});
    expect(result).not.toBeNull();
    expect(result?.source).toBe(source);
  });
});

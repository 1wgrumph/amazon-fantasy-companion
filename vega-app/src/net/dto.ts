// CONTRACT-AFC-P2-API / CONTRACT-AFC-P2-ENVELOPE decoders. Decoders return null on contract violations.
export type Json = null | boolean | number | string | Json[] | {[key: string]: Json};
export type JsonObject = {[key: string]: Json};

/** Raised when a request or response crosses the CONTRACT-AFC-P2-API boundary out of contract. */
export class ContractError extends Error {}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

const RFC3339 =
  /^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])T([01]\d|2[0-3]):[0-5]\d:([0-5]\d|60)(\.\d{1,9})?(Z|[+-]([01]\d|2[0-3]):[0-5]\d)$/;

export function isTimestamp(value: unknown): value is string {
  return typeof value === 'string' && RFC3339.test(value);
}

function integral(value: unknown): number | null {
  return typeof value === 'number' && Number.isInteger(value) ? value : null;
}

/** CONTRACT-AFC-P2-ENVELOPE. */
export interface Envelope {
  schemaVersion: number;
  id: string;
  revision: number;
  source: string;
  updatedAt: string;
  eventTime: string | null;
  data: JsonObject;
}

const SOURCES = new Set(['live', 'replay', 'yahoo', 'manual']);

/** A revision older than the one held is rejected. */
export function decodeEnvelope(json: unknown, heldRevision?: number): Envelope | null {
  if (!isRecord(json)) return null;
  const schemaVersion = integral(json.schemaVersion);
  if (schemaVersion !== 1) return null;
  const id = typeof json.id === 'string' && json.id.length > 0 ? json.id : null;
  if (id === null) return null;
  const revision = integral(json.revision);
  if (revision === null || revision < 0) return null;
  if (heldRevision !== undefined && revision < heldRevision) return null;
  const source = typeof json.source === 'string' && SOURCES.has(json.source) ? json.source : null;
  if (source === null) return null;
  if (!isTimestamp(json.updatedAt)) return null;
  let eventTime: string | null = null;
  if ('eventTime' in json) {
    if (!isTimestamp(json.eventTime)) return null;
    eventTime = json.eventTime;
  }
  if (!isRecord(json.data)) return null;
  return {
    schemaVersion,
    id,
    revision,
    source,
    updatedAt: json.updatedAt,
    eventTime,
    data: json.data as JsonObject,
  };
}

export type AccessBasis = 'verified' | 'customerConfirmed' | 'unknown';

export interface ProviderRoute {
  provider: string | null;
  channel: string | null;
  route: JsonObject | null;
  accessBasis: AccessBasis;
}

/** Absent or JSON null yields {present: true, value: null}; a wrong-typed value is invalid. */
function optionalString(obj: Record<string, unknown>, key: string): {value: string | null} | null {
  const value = obj[key];
  if (value === undefined || value === null) return {value: null};
  return typeof value === 'string' ? {value} : null;
}

function optionalObject(obj: Record<string, unknown>, key: string): {value: JsonObject | null} | null {
  const value = obj[key];
  if (value === undefined || value === null) return {value: null};
  return isRecord(value) ? {value: value as JsonObject} : null;
}

/** Resolved route and access basis; never inferred from installed apps. */
export function decodeProviderRoute(json: unknown): ProviderRoute | null {
  if (!isRecord(json)) return null;
  const basis = json.accessBasis;
  if (basis !== 'verified' && basis !== 'customerConfirmed' && basis !== 'unknown') return null;
  const provider = optionalString(json, 'provider');
  if (provider === null) return null;
  const channel = optionalString(json, 'channel');
  if (channel === null) return null;
  const route = optionalObject(json, 'route');
  if (route === null) return null;
  return {provider: provider.value, channel: channel.value, route: route.value, accessBasis: basis};
}

export interface Alert {
  envelope: Envelope;
  route: ProviderRoute | null;
}

/** An alert envelope; data.route is optional and absent access shows as unknown. */
export function decodeAlert(envelope: Envelope): Alert | null {
  const raw = (envelope.data as Record<string, unknown>).route;
  if (raw === undefined || raw === null) return {envelope, route: null};
  const route = decodeProviderRoute(raw);
  return route === null ? null : {envelope, route};
}

export type RoutingOutcome =
  | 'gameOpened'
  | 'searchOpened'
  | 'appHomeOpened'
  | 'appAbsent'
  | 'accessUnknown'
  | 'playbackDenied';

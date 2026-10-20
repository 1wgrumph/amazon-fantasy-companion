// Interface scaffolding for P2-V01T (red). Behavior lands in P2-V01; decoders return null until then.
export type Json = null | boolean | number | string | Json[] | {[key: string]: Json};
export type JsonObject = {[key: string]: Json};

/** Raised when a request or response crosses the CONTRACT-AFC-P2-API boundary out of contract. */
export class ContractError extends Error {}

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

export function decodeEnvelope(_json: unknown, _heldRevision?: number): Envelope | null {
  return null;
}

export type AccessBasis = 'verified' | 'customerConfirmed' | 'unknown';

export interface ProviderRoute {
  provider: string | null;
  channel: string | null;
  route: JsonObject | null;
  accessBasis: AccessBasis;
}

export interface Alert {
  envelope: Envelope;
  route: ProviderRoute | null;
}

export type RoutingOutcome =
  | 'gameOpened'
  | 'searchOpened'
  | 'appHomeOpened'
  | 'appAbsent'
  | 'accessUnknown'
  | 'playbackDenied';

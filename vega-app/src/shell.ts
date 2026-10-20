// Interface scaffolding for P2-V01T (red). Behavior lands in P2-V01.
export type Destination = 'Link' | 'ProfileSettings' | 'BackendNotConfigured';

export interface ShellStart {
  destination: Destination | null;
  message: string | null;
}

export function shellDestinations(): ReadonlySet<string> {
  return new Set();
}

/** Start screen for a build-time AFC_API_BASE_URL and whether a session token exists. */
export function shellStart(_baseUrl: string, _hasSession: boolean): ShellStart {
  return {destination: null, message: null};
}

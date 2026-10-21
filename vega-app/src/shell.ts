// SHELL: Link, Profile/Settings and Panel only; no social or messaging surfaces (AFC-PR-057).
import {isUsableBaseUrl} from './net/apiClient';

export type Destination = 'Link' | 'ProfileSettings' | 'BackendNotConfigured';

export interface ShellStart {
  destination: Destination | null;
  message: string | null;
}

export function shellDestinations(): ReadonlySet<string> {
  return new Set(['Link', 'Profile/Settings', 'Panel']);
}

/** Start screen for a build-time AFC_API_BASE_URL and whether a session token exists. */
export function shellStart(baseUrl: string, hasSession: boolean): ShellStart {
  if (!isUsableBaseUrl(baseUrl)) {
    return {destination: 'BackendNotConfigured', message: 'Backend not configured'};
  }
  return {destination: hasSession ? 'ProfileSettings' : 'Link', message: null};
}

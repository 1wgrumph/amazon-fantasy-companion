// NOTIFIER's presentation, alert text and voice gate. Alert payloads are untrusted: the headline
// is ours, player/matchup/commentary are sanitized and bounded, and any displayed field carrying
// an on-field, will-score or access claim is dropped whole rather than edited (AFC-PR-027/-028/-032).
import {isRecord} from '../net/dto';
import type {Alert} from '../net/dto';
import {voiceActive} from '../profile/profile';
import type {Presentation, ProfileState} from '../profile/profile';

export interface AlertText {
  headline: string;
  context: string;
  access: string;
  commentary: string | null;
}

export type AlertAction = 'Watch' | 'Dismiss';

export interface AlertView {
  presentation: Presentation;
  actions: AlertAction[];
  speak: boolean;
}

const MAX_CONTEXT_LENGTH = 80;
const MAX_COMMENTARY_LENGTH = 240;

// Matched against normalized text, where words are separated by single spaces.
const UNSAFE_CLAIM =
  /\b(on the field|on field|will score|going to score|about to score|is scoring|set to score|sure to score|guaranteed|includ(ed|es)|subscribed)\b|(?<!not )\bverified\b/i;

function isUnsafe(value: string): boolean {
  return UNSAFE_CLAIM.test(value.replace(/[^\p{L}\p{N}]+/gu, ' ').trim());
}

function clean(value: unknown, maxLength: number = MAX_CONTEXT_LENGTH): string | null {
  if (typeof value !== 'string') return null;
  const text = value.replace(/[\p{Cc}\s]+/gu, ' ').trim().slice(0, maxLength);
  return text === '' ? null : text;
}

function safe(value: string | null): string | null {
  return value !== null && !isUnsafe(value) ? value : null;
}

/** Joined starter names bounded to one context field; the remainder is counted, not spelled out. */
function boundedNames(names: string[]): string {
  const joined = names.join(', ');
  if (joined.length <= MAX_CONTEXT_LENGTH) return joined;
  for (let shown = names.length - 1; shown >= 1; shown--) {
    const candidate = names.slice(0, shown).join(', ') + `, +${names.length - shown} more`;
    if (candidate.length <= MAX_CONTEXT_LENGTH) return candidate;
  }
  const suffix = `, +${names.length - 1} more`;
  return names[0].slice(0, MAX_CONTEXT_LENGTH - suffix.length) + suffix;
}

/** Null when the alert lacks safe triggering context. */
export function alertText(alert: Alert): AlertText | null {
  const data = alert.envelope.data as Record<string, unknown>;
  const trigger = data.triggerContext;
  if (!isRecord(trigger)) return null;
  // A present matchup must be safe; an absent or null one is simply not shown (never fabricated).
  let matchup: string | null = null;
  if ('matchup' in trigger && trigger.matchup !== null) {
    matchup = safe(clean(trigger.matchup));
    if (matchup === null) return null;
  }
  let player: string;
  if ('starters' in trigger) {
    const starters = trigger.starters;
    if (!Array.isArray(starters)) return null;
    const names: string[] = [];
    for (const starter of starters) {
      if (!isRecord(starter)) return null;
      const name = safe(clean(starter.name));
      if (name === null) return null;
      names.push(name);
    }
    player = names.length === 0 ? '' : boundedNames(names);
  } else {
    if (matchup === null) return null;
    const legacy = safe(clean(trigger.player));
    if (legacy === null) return null;
    player = legacy;
  }
  // A claim may span the player/matchup boundary.
  if (isUnsafe([player, matchup].filter((part): part is string => part !== null).join(' '))) return null;
  const commentary = safe(clean(data.commentary, MAX_COMMENTARY_LENGTH));
  const type = data.alertType;
  const accessBasis = alert.route?.accessBasis ?? 'unknown';
  return {
    headline:
      type === 'RedZone' || type === 'redZone'
        ? 'Red-zone alert'
        : type === 'PlayerScore' || type === 'playerScore'
          ? 'Score update'
          : type === 'CloseGame' || type === 'closeGame'
            ? 'Close game alert'
            : 'Game alert',
    context: matchup === null ? player : `${player} — ${matchup}`,
    access:
      accessBasis === 'verified'
        ? 'Access: verified'
        : accessBasis === 'customerConfirmed'
          ? 'Access: confirmed by you'
          : 'Access: unknown',
    commentary,
  };
}

export function alertView(alert: Alert, profile: ProfileState, voiceRouteVerified = false): AlertView | null {
  if (alertText(alert) === null) return null;
  return {
    presentation: profile.presentation,
    actions: profile.presentation === 'HeadsUp' ? ['Watch', 'Dismiss'] : [],
    speak: voiceActive(profile, voiceRouteVerified),
  };
}

// DES-AFC-P2-ALERTPATH NOTIFIER: presentation (AFC-PR-015, -021), triggering context (AFC-PR-027), no red-zone
// over-claim (AFC-PR-028), unknown access shown as unknown (AFC-PR-032, -033), voice gate (AFC-PR-022).
// Mirrors AlertPresenterTest.kt; alert payloads are untrusted backend data.
import {alertText, alertView, AlertText} from '../../src/alerts/alertPresenter';
import {alert, alertData, allText, MATCHUP, PLAYER, profile, route} from '../support/alerts';

const overClaim = /on the field|on-field|will score|going to score|about to score|is scoring|set to score|sure to score|guaranteed/i;
// An access label may say "not verified"; it may never claim verification, inclusion or a subscription.
const accessClaim = /\binclud(ed|es)\b|\bsubscribed\b|(?<!not )\bverified\b/i;

function text(data = alertData()): AlertText {
  const rendered = alertText(alert(data));
  expect(rendered).not.toBeNull();
  return rendered!;
}

describe('AlertPresenterTest', () => {
  test('headsUpSelectionShowsWatchAndDismiss', () => {
    const view = alertView(alert(), profile('HeadsUp'));
    expect(view).not.toBeNull();
    expect(view?.presentation).toBe('HeadsUp');
    expect(view?.actions).toEqual(['Watch', 'Dismiss']);
  });

  test('panelOnlySelectionShowsNoHeadsUp', () => {
    const view = alertView(alert(), profile('PanelOnly'));
    expect(view).not.toBeNull();
    expect(view?.presentation).toBe('PanelOnly');
    expect(view?.actions).toEqual([]);
  });

  test('textCarriesTheTriggeringPlayerAndMatchup', () => {
    const t = text();
    expect(t.context).toContain(PLAYER);
    expect(t.context).toContain(MATCHUP);
  });

  test('alertWithoutTriggeringContextIsNotRendered', () => {
    expect(alertText(alert(alertData({player: null})))).toBeNull();
    expect(alertText(alert(alertData({matchup: null})))).toBeNull();
    expect(alertText(alert(alertData({player: ' '})))).toBeNull();
  });

  test('redZoneTextMakesNoOnFieldOrWillScoreClaim', () => {
    expect(allText(text(alertData({type: 'redZone'})))).not.toMatch(overClaim);
  });

  test('redZoneCommentaryClaimingAPlayerWillScoreIsNotShown', () => {
    const t = text(alertData({type: 'redZone', commentary: `${PLAYER} is on the field and will score!`}));
    expect(t.context).toContain(PLAYER);
    expect(allText(t)).not.toMatch(overClaim);
  });

  test('unknownAccessReadsUnknownAndPromisesNothing', () => {
    for (const data of [alertData({route: null}), alertData({route: route('unknown')}), alertData({route: route('unknown', null)})]) {
      const access = text(data).access;
      expect(access).toMatch(/\bunknown\b/i);
      expect(access).not.toMatch(accessClaim);
    }
  });

  test('customerConfirmedAccessIsNotShownAsVerified', () => {
    const access = text(alertData({route: route('customerConfirmed')})).access;
    expect(access.trim()).not.toBe('');
    expect(access).not.toMatch(accessClaim);
  });

  test('verifiedAccessIsNotShownAsUnknown', () => {
    const access = text(alertData({route: route('verified')})).access;
    expect(access.trim()).not.toBe('');
    expect(access).not.toMatch(/\bunknown\b/i);
  });

  test('voiceSpeaksOnlyWhenEnabledOverAVerifiedRoute', () => {
    const speaks = alertView(alert(), profile('HeadsUp', true), true);
    expect(speaks).not.toBeNull();
    expect(speaks?.speak).toBe(true);
    const disabled = alertView(alert(), profile('HeadsUp', false), true);
    expect(disabled).not.toBeNull();
    expect(disabled?.speak).toBe(false);
  });

  test('voiceStaysOffWithoutAVerifiedRoute', () => {
    const unverified = alertView(alert(), profile('HeadsUp', true), false);
    expect(unverified).not.toBeNull();
    expect(unverified?.speak).toBe(false);
    const shipped = alertView(alert(), profile('HeadsUp', true));
    expect(shipped).not.toBeNull();
    expect(shipped?.speak).toBe(false);
  });
});

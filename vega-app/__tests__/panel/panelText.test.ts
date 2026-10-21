// AFC-PR-039/-040/-045: values, basis, stale and unavailable labels, and the text-size floor (mirrors PanelTextTest.kt).
import {PanelText, PanelTextSizes, PanelValue} from '../../src/panel/panel';
import {AS_OF_MS} from '../support/panel';

const stale = /stale/i;
const unavailable = /unavailable/i;
const zero = /(^|[^0-9.])-?0(\.0+)?([^0-9.]|$)/;

const v = (x: number | null, asOfMs: number | null = AS_OF_MS, reason: string | null = null): PanelValue => ({
  value: x,
  reason: reason ?? (x === null ? 'feed withheld' : null),
  source: 'live',
  asOfMs,
});

describe('PanelTextTest', () => {
  test('freshValueShowsTheNumberWithoutLabels', () => {
    const text = PanelText.value(v(12.3), AS_OF_MS + 59_999);
    expect(text).toBe('12.3');
    expect(text).not.toMatch(stale);
    expect(text).not.toMatch(unavailable);
  });

  test('valueAtSixtySecondsIsLabeledStaleWithItsAge', () => {
    expect(PanelText.value(v(12.3), AS_OF_MS + 60_000)).toMatch(stale);
    const older = PanelText.value(v(12.3), AS_OF_MS + 75_000);
    expect(older).toMatch(stale);
    expect(older).toContain('75');
    expect(older).toContain('12.3');
  });

  test('unknownValueIsLabeledUnavailableAndNeverZero', () => {
    const text = PanelText.value(v(null), AS_OF_MS);
    expect(text).toMatch(unavailable);
    expect(text).not.toMatch(zero);
  });

  test('realZeroIsShownAsZero', () => {
    const text = PanelText.value(v(0.0), AS_OF_MS);
    expect(text).toMatch(zero);
    expect(text).not.toMatch(unavailable);
  });

  test('valueWithoutTimestampIsNeverShownAsFresh', () => {
    const text = PanelText.value(v(12.3, null), AS_OF_MS);
    expect(stale.test(text) || unavailable.test(text)).toBe(true);
  });

  test('unknownGameStatusIsLabeledUnavailable', () => {
    expect(PanelText.gameStatus('Q2 08:14')).toBe('Q2 08:14');
    expect(PanelText.gameStatus(null)).toMatch(unavailable);
  });

  test('eachScoringBasisHasItsLabel', () => {
    expect(PanelText.basis('yahooLeague')).toBe('Yahoo league scoring');
    expect(PanelText.basis('ppr')).toBe('PPR');
    expect(PanelText.basis('halfPpr')).toBe('Half-PPR');
  });

  // Sizes are px at the VVD's 1080p output; the screencap measurement belongs to P2-V01's visual review.
  test('textSizesMeetTheCouchFloor', () => {
    expect(PanelTextSizes.bodyPx).toBeGreaterThanOrEqual(24);
    expect(PanelTextSizes.scorePx).toBeGreaterThanOrEqual(32);
  });
});

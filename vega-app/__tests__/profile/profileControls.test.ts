// Every profile control is offered; an unsupported platform route hides its control with a stated limit (mirrors ProfileControlsTest.kt).
import {effectiveInstalled, PROFILE_CONTROLS, profileControls, voiceActive} from '../../src/profile/profile';
import {customized} from '../support/profile';

describe('ProfileControlsTest', () => {
  test('everyControlIsOfferedWhenRoutesAreSupported', () => {
    const controls = profileControls({detectionSupported: true, voiceRouteVerified: true});
    expect(new Set(controls.visible)).toEqual(new Set(PROFILE_CONTROLS));
    expect(controls.visible.length).toBe(new Set(controls.visible).size);
    expect(controls.limits).toEqual({});
  });

  // Vega detection route is Linking.canOpenURL; when unsupported the control is hidden with a stated limit (P2-X07 rule).
  test('unsupportedDetectionHidesItsControlWithStatedLimit', () => {
    const controls = profileControls({detectionSupported: false, voiceRouteVerified: true});
    expect(controls.visible).not.toContain('DetectionOptIn');
    expect(controls.limits.DetectionOptIn?.trim()).toBeTruthy();
    expect(new Set(controls.visible)).toEqual(new Set(PROFILE_CONTROLS.filter(c => c !== 'DetectionOptIn')));
  });

  test('unverifiedVoiceRouteHidesVoiceWithStatedLimit', () => {
    const controls = profileControls({detectionSupported: true, voiceRouteVerified: false});
    expect(controls.visible).not.toContain('Voice');
    expect(controls.limits.Voice?.trim()).toBeTruthy();
    expect(new Set(controls.visible)).toEqual(new Set(PROFILE_CONTROLS.filter(c => c !== 'Voice')));
  });

  // AFC-PR-022: voice speaks only while enabled over a verified route.
  test('voiceGateNeedsBothEnablementAndVerifiedRoute', () => {
    expect(voiceActive({...customized(), voiceEnabled: true}, true)).toBe(true);
    expect(voiceActive({...customized(), voiceEnabled: true}, false)).toBe(false);
    expect(voiceActive({...customized(), voiceEnabled: false}, true)).toBe(false);
    expect(voiceActive({...customized(), voiceEnabled: false}, false)).toBe(false);
  });

  // AFC-PR-005: the customer's review wins in both directions; unreviewed apps follow detection.
  test('customerOverrideWinsOverDetection', () => {
    const state = customized();
    expect(effectiveInstalled(state, new Set(['com.example.provider.a', 'com.example.provider.b']))).toEqual(
      new Set(['com.example.provider.b', 'com.example.provider.c']),
    );
    expect(effectiveInstalled(state, new Set())).toEqual(new Set(['com.example.provider.c']));
  });
});

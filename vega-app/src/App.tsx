// Fantasy Companion for Vega OS: Link, Profile/Settings and Panel (AFC-PR-057).
// All behavior lives in the tested modules; this file only wires them to the screen.
import React, {useCallback, useEffect, useRef, useState} from 'react';
import {Linking, Pressable, ScrollView, StyleSheet, Text, TextInput, View} from 'react-native';
import {useTVEventHandler} from '@amazon-devices/react-native-kepler';
import {AlertFeed} from './alerts/alertFeed';
import {AlertNotifier} from './alerts/alertNotifier';
import type {PostedNotification} from './alerts/alertNotifier';
import {alertText} from './alerts/alertPresenter';
import {appTokenStore} from './auth/tokenStore';
import type {TokenStore} from './auth/tokenStore';
import {AFC_API_BASE_URL} from './config';
import {AppDetector} from './detect/appDetector';
import {runLinkFlow} from './link/linkScreen';
import type {LinkPresentation} from './link/linkScreen';
import {ApiClient} from './net/apiClient';
import {isRecord} from './net/dto';
import type {Alert, ProviderRoute} from './net/dto';
import {decodePanel, PanelController, PanelText, PanelTextSizes} from './panel/panel';
import type {PanelSnapshot} from './panel/panel';
import {
  EXCITEMENT_LEVELS,
  PRESENTATIONS,
  PROFILE_CONTROLS,
  SCORING_PRESETS,
  profileControls,
  ProfileStore,
} from './profile/profile';
import type {ProfileState, TimeWindow} from './profile/profile';
import {shellStart} from './shell';
import {WatchLauncher} from './watch/watchLauncher';
import type {LaunchPlatform} from './watch/watchLauncher';

const sleep = (ms: number) => new Promise<void>(resolve => setTimeout(resolve, ms));
const onOff = (value: boolean) => (value ? 'on' : 'off');
const minuteOfDay = (minute: number) =>
  `${String(Math.floor(minute / 60)).padStart(2, '0')}:${String(minute % 60).padStart(2, '0')}`;

/** Vega launch platform over Linking; no current-app observation exists on Vega. */
const vegaPlatform: LaunchPlatform = {
  isInstalled: packageName => Linking.canOpenURL(`pkg://${packageName}`).catch(() => false),
  start: async (packageName, type, value) => {
    try {
      await Linking.openURL(type === 'uri' ? value : `pkg://${packageName}`);
      return true;
    } catch {
      return false;
    }
  },
  currentApp: async () => null,
  leaveApp: () => {},
};

function TvButton({label, onPress, preferred}: {label: string; onPress: () => void; preferred?: boolean}) {
  const [focused, setFocused] = useState(false);
  return (
    <Pressable
      onPress={onPress}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      hasTVPreferredFocus={preferred}
      style={[styles.button, focused && styles.buttonFocused]}>
      <Text style={styles.buttonText}>{label}</Text>
    </Pressable>
  );
}

export function App() {
  const tokenStore = useRef<TokenStore>(appTokenStore());
  const [screen, setScreen] = useState<'boot' | 'notConfigured' | 'link' | 'main'>('boot');
  const [client, setClient] = useState<ApiClient | null>(null);

  useEffect(() => {
    (async () => {
      const token = await tokenStore.current.read().catch(() => null);
      const start = shellStart(AFC_API_BASE_URL, token !== null);
      if (start.destination === 'BackendNotConfigured') {
        setScreen('notConfigured');
        return;
      }
      setClient(new ApiClient(AFC_API_BASE_URL, {token: () => tokenStore.current.read().catch(() => null)}));
      setScreen(start.destination === 'Link' ? 'link' : 'main');
    })();
  }, []);

  if (screen === 'boot') return <Text style={styles.title}>Fantasy Companion</Text>;
  if (screen === 'notConfigured') {
    return (
      <View style={styles.screen}>
        <Text style={styles.title}>Fantasy Companion</Text>
        <Text style={styles.body}>Backend not configured</Text>
      </View>
    );
  }
  if (client === null) return null;
  if (screen === 'link') {
    return <LinkScreen client={client} tokenStore={tokenStore.current} onLinked={() => setScreen('main')} />;
  }
  return <MainScreen client={client} />;
}

function LinkScreen({
  client,
  tokenStore,
  onLinked,
}: {
  client: ApiClient;
  tokenStore: TokenStore;
  onLinked: () => void;
}) {
  const [attempt, setAttempt] = useState(0);
  const [shown, setShown] = useState<LinkPresentation | null>(null);

  useEffect(() => {
    setShown(null);
    runLinkFlow({
      client,
      sleep,
      show: presentation => {
        setShown(presentation);
        if (presentation.showProfile) onLinked();
      },
      store: token => tokenStore.write(token),
    });
  }, [attempt, client, tokenStore, onLinked]);

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Link this TV</Text>
      {shown === null ? (
        <Text style={styles.body}>Requesting a code…</Text>
      ) : (
        <>
          {shown.code !== null && <Text style={styles.code}>{shown.code}</Text>}
          <Text style={styles.body}>{shown.message}</Text>
          {shown.state !== 'codePending' && !shown.showProfile && (
            <TvButton label="Get code" preferred onPress={() => setAttempt(value => value + 1)} />
          )}
        </>
      )}
    </View>
  );
}

function cycle<T>(values: readonly T[], current: T): T {
  return values[(values.indexOf(current) + 1) % values.length];
}

function adjustWindow(windows: TimeWindow[], index: number, start: boolean, delta: number): TimeWindow[] {
  const mod = (minute: number) => ((minute % 1440) + 1440) % 1440;
  return windows.map((window, i) =>
    i === index
      ? start
        ? {...window, startMinute: mod(window.startMinute + delta)}
        : {...window, endMinute: mod(window.endMinute + delta)}
      : window,
  );
}

function NameListEditor({
  label,
  values,
  onToggle,
}: {
  label: string;
  values: string[];
  onToggle: (value: string) => void;
}) {
  const [draft, setDraft] = useState('');
  return (
    <View>
      <Text style={styles.body}>
        {label}: {values.join(', ') || 'none'}
      </Text>
      {values.map(value => (
        <TvButton key={value} label={`Remove ${value} from ${label}`} onPress={() => onToggle(value)} />
      ))}
      <TextInput style={styles.input} value={draft} onChangeText={setDraft} placeholder={label} />
      <TvButton
        label={`Add to ${label}`}
        onPress={() => {
          const value = draft.trim();
          if (value !== '' && !values.includes(value)) onToggle(value);
          setDraft('');
        }}
      />
    </View>
  );
}

function WindowListEditor({
  label,
  windows,
  fallback,
  onChange,
}: {
  label: string;
  windows: TimeWindow[];
  fallback: TimeWindow;
  onChange: (windows: TimeWindow[]) => void;
}) {
  return (
    <View>
      <Text style={styles.body}>
        {label}: {windows.length} windows
      </Text>
      {windows.map((window, index) => (
        <View key={index}>
          <Text style={styles.body}>
            Window {index + 1}: {minuteOfDay(window.startMinute)} to {minuteOfDay(window.endMinute)}
          </Text>
          <TvButton label="Start -30m" onPress={() => onChange(adjustWindow(windows, index, true, -30))} />
          <TvButton label="Start +30m" onPress={() => onChange(adjustWindow(windows, index, true, 30))} />
          <TvButton label="End -30m" onPress={() => onChange(adjustWindow(windows, index, false, -30))} />
          <TvButton label="End +30m" onPress={() => onChange(adjustWindow(windows, index, false, 30))} />
          <TvButton label={`Remove window ${index + 1}`} onPress={() => onChange(windows.filter((_, i) => i !== index))} />
        </View>
      ))}
      <TvButton label={`Add ${label} window`} onPress={() => onChange([...windows, fallback])} />
    </View>
  );
}

function TeamLeagueEditor({
  profile,
  onChange,
}: {
  profile: ProfileState;
  onChange: (teamLeague: ProfileState['teamLeague']) => void;
}) {
  const [league, setLeague] = useState(profile.teamLeague?.league ?? '');
  const [team, setTeam] = useState(profile.teamLeague?.team ?? '');
  return (
    <View>
      <Text style={styles.body}>
        Team/league: {profile.teamLeague !== null ? `${profile.teamLeague.team} in ${profile.teamLeague.league}` : 'none selected'}
      </Text>
      <Text style={styles.body}>League</Text>
      <TextInput style={styles.input} value={league} onChangeText={setLeague} />
      <Text style={styles.body}>Team</Text>
      <TextInput style={styles.input} value={team} onChangeText={setTeam} />
      <TvButton
        label="Set team/league"
        onPress={() => {
          const nextLeague = league.trim();
          const nextTeam = team.trim();
          if (nextLeague !== '' && nextTeam !== '') onChange({league: nextLeague, team: nextTeam});
        }}
      />
      <TvButton label="Clear team/league" onPress={() => onChange(null)} />
    </View>
  );
}

function ProviderPreferenceEditor({
  profile,
  onChange,
}: {
  profile: ProfileState;
  onChange: (providerPref: ProfileState['providerPref']) => void;
}) {
  const pref = profile.providerPref;
  const [market, setMarket] = useState(pref.localMarket ?? '');
  const [overrideDraft, setOverrideDraft] = useState('');
  const cycleOverride = (packageName: string) => {
    const name = packageName.trim();
    if (name === '') return;
    const appOverrides = {...pref.appOverrides};
    // Automatic -> installed -> not installed -> automatic.
    if (!(name in appOverrides)) appOverrides[name] = true;
    else if (appOverrides[name]) appOverrides[name] = false;
    else delete appOverrides[name];
    onChange({...pref, appOverrides});
  };
  return (
    <View>
      <Text style={styles.body}>
        Providers: {pref.order.join(', ') || 'no preference'}; market {pref.localMarket ?? 'unset'};{' '}
        {Object.keys(pref.appOverrides).length} overrides
      </Text>
      {pref.order.map((provider, index) => (
        <View key={provider}>
          <Text style={styles.body}>
            {index + 1}. {provider}
          </Text>
          {index > 0 && (
            <TvButton
              label="Move up"
              onPress={() => {
                const order = [...pref.order];
                [order[index - 1], order[index]] = [order[index], order[index - 1]];
                onChange({...pref, order});
              }}
            />
          )}
          <TvButton
            label={`Access confirmed: ${onOff(pref.confirmedAccess.has(provider))}`}
            onPress={() => {
              const confirmedAccess = new Set(pref.confirmedAccess);
              if (confirmedAccess.has(provider)) confirmedAccess.delete(provider);
              else confirmedAccess.add(provider);
              onChange({...pref, confirmedAccess});
            }}
          />
          <TvButton
            label="Remove"
            onPress={() => {
              const confirmedAccess = new Set(pref.confirmedAccess);
              confirmedAccess.delete(provider);
              onChange({...pref, order: pref.order.filter(entry => entry !== provider), confirmedAccess});
            }}
          />
        </View>
      ))}
      <NameListEditor
        label="New provider"
        values={[]}
        onToggle={value => {
          if (!pref.order.includes(value)) onChange({...pref, order: [...pref.order, value]});
        }}
      />
      <Text style={styles.body}>Detected-app overrides (automatic / installed / not installed)</Text>
      {Object.entries(pref.appOverrides)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([packageName, installed]) => (
          <TvButton
            key={packageName}
            label={`${packageName}: ${installed ? 'installed' : 'not installed'} (select to change)`}
            onPress={() => cycleOverride(packageName)}
          />
        ))}
      <TextInput style={styles.input} value={overrideDraft} onChangeText={setOverrideDraft} placeholder="Package name" />
      <TvButton
        label="Add app override"
        onPress={() => {
          cycleOverride(overrideDraft);
          setOverrideDraft('');
        }}
      />
      <Text style={styles.body}>Local market</Text>
      <TextInput style={styles.input} value={market} onChangeText={setMarket} />
      <TvButton
        label="Set market"
        onPress={() => onChange({...pref, localMarket: market.trim() === '' ? null : market.trim()})}
      />
      <TvButton label="Clear market" onPress={() => onChange({...pref, localMarket: null})} />
    </View>
  );
}

/** The event ID an outcome can be reported for, from triggerContext or the data-level fallback. */
function watchEventId(alert: Alert): string | null {
  const data = alert.envelope.data as Record<string, unknown>;
  const trigger = isRecord(data.triggerContext) ? data.triggerContext : null;
  const candidate = trigger?.eventId ?? data.eventId;
  return typeof candidate === 'string' && candidate.trim() !== '' && candidate.length <= 256 ? candidate : null;
}

function MainScreen({client}: {client: ApiClient}) {
  const profileStore = useRef(new ProfileStore(client));
  const feed = useRef(new AlertFeed(client));
  const controller = useRef<PanelController | null>(null);
  const armedWatch = useRef<string | null>(null);
  const [profile, setProfile] = useState<ProfileState | null>(null);
  const [message, setMessage] = useState('Loading profile…');
  const [snapshot, setSnapshot] = useState<PanelSnapshot | null>(null);
  const [panelTick, setPanelTick] = useState(0);
  const [banner, setBanner] = useState<{alert: Alert; notification: PostedNotification} | null>(null);
  const [watchMessage, setWatchMessage] = useState<string | null>(null);

  const applyProfile = useCallback((loaded: ProfileState) => {
    setProfile(loaded);
    const combos = [...loaded.selections.leagues].flatMap(league =>
      [...loaded.selections.teams].map(team => `${league}/${team}`),
    );
    const initial = loaded.teamLeague !== null ? `${loaded.teamLeague.league}/${loaded.teamLeague.team}` : (combos[0] ?? '');
    const teamLeagues = [...new Set([initial, ...combos])].filter(value => value !== '');
    controller.current = new PanelController(teamLeagues, initial, loaded.panel.visible);
    setSnapshot(null);
    setPanelTick(value => value + 1);
  }, []);

  const load = useCallback(async () => {
    const loaded = await profileStore.current.load();
    if (loaded === null) {
      setMessage('Profile unavailable');
      return;
    }
    applyProfile(loaded);
    setMessage('');
  }, [applyProfile]);

  useEffect(() => {
    load();
  }, [load]);

  // Panel refresh: on show and every panel_refresh (30 s) while visible, per the controller.
  useEffect(() => {
    let inFlight = false;
    let stopped = false;
    const timer = setInterval(async () => {
      const current = controller.current;
      if (stopped || current === null || !current.visible) return;
      // Held values age even when the network is pending or unavailable.
      if (current.snapshot !== null) setPanelTick(value => value + 1);
      if (inFlight || !current.shouldFetch(Date.now())) return;
      inFlight = true;
      try {
        const result = await client.getPanel(current.teamLeague !== '' ? current.teamLeague : undefined);
        if (stopped || controller.current !== current) return;
        const decoded = result.value !== null ? decodePanel(result.value) : null;
        if (decoded !== null) {
          current.onFetched(decoded, Date.now());
          setSnapshot(current.snapshot);
          setPanelTick(value => value + 1);
        }
      } catch {
        // A failed fetch leaves the held snapshot and its stale labels in place.
      } finally {
        inFlight = false;
      }
    }, 1_000);
    return () => {
      stopped = true;
      clearInterval(timer);
    };
  }, [client]);

  // Alert long poll; delivery on Vega is the in-app banner (no verified notification route).
  useEffect(() => {
    let stopped = false;
    const notifier = new AlertNotifier({
      post: notification => {
        const alert = feed.current.queue.find(entry => entry.envelope.id === notification.id);
        if (alert !== undefined) setBanner({alert, notification});
      },
    });
    (async () => {
      while (!stopped) {
        const delivered = await feed.current.poll();
        delivered.forEach(alert => notifier.show(alert));
        await sleep(1_000);
      }
    })();
    return () => {
      stopped = true;
    };
  }, []);

  useTVEventHandler(event => {
    if (event.eventKeyAction === 1 || controller.current === null) return;
    if (controller.current.onKey(event.eventType, Date.now())) {
      setSnapshot(controller.current.snapshot);
      setPanelTick(value => value + 1);
    }
  });

  const save = async () => {
    if (profile === null) return;
    const saved = await profileStore.current.save(profile);
    if (saved === null) {
      setMessage('Save failed; the profile changed elsewhere or is unavailable');
      return;
    }
    applyProfile(saved);
    setMessage('Saved');
    if (saved.detectionOptIn) {
      const detector = new AppDetector(
        packageName => Linking.canOpenURL(`pkg://${packageName}`).catch(() => false),
        () => saved.detectionOptIn,
      );
      await detector.report(client, Object.keys(saved.providerPref.appOverrides)).catch(() => null);
    }
  };

  const watch = async (alert: Alert) => {
    if (profile === null) return;
    const eventId = watchEventId(alert);
    if (eventId === null) return;
    if (profile.switchingConfirm && armedWatch.current !== alert.envelope.id) {
      armedWatch.current = alert.envelope.id;
      setWatchMessage('Press Watch again to switch apps.');
      return;
    }
    armedWatch.current = null;
    const route: ProviderRoute = alert.route ?? {provider: null, channel: null, route: null, accessBasis: 'unknown'};
    const outcome = await new WatchLauncher(vegaPlatform).watch(
      eventId,
      route,
      client,
      false,
      'fullScreen',
      async () => true,
    );
    setWatchMessage(
      outcome === 'appAbsent'
        ? 'Watch: the provider app is not installed.'
        : outcome === 'playbackDenied'
          ? 'Watch: the provider app refused the launch.'
          : 'Watch: could not confirm the game is playing.',
    );
  };

  if (profile === null) {
    return (
      <View style={styles.screen}>
        <Text style={styles.title}>Profile/Settings</Text>
        <Text style={styles.body}>{message}</Text>
        <TvButton label="Retry" preferred onPress={load} />
      </View>
    );
  }

  const controls = profileControls({detectionSupported: true, voiceRouteVerified: false});
  const set = (next: ProfileState) => setProfile(next);
  const bannerText = banner !== null ? alertText(banner.alert) : null;
  void panelTick;

  return (
    <ScrollView style={styles.screen}>
      <Text style={styles.title}>Profile/Settings</Text>
      {message !== '' && <Text style={styles.body}>{message}</Text>}
      {banner !== null && bannerText !== null && profile.presentation === 'HeadsUp' && (
        <View style={styles.banner}>
          <Text style={styles.body}>{bannerText.headline}</Text>
          <Text style={styles.body}>{bannerText.context}</Text>
          <Text style={styles.body}>{bannerText.access}</Text>
          {bannerText.commentary !== null && <Text style={styles.body}>{bannerText.commentary}</Text>}
          {watchEventId(banner.alert) !== null && <TvButton label="Watch" onPress={() => watch(banner.alert)} />}
          <TvButton
            label="Dismiss"
            onPress={() => {
              feed.current.dismiss(banner.alert.envelope.id);
              setBanner(null);
            }}
          />
        </View>
      )}
      {watchMessage !== null && <Text style={styles.body}>{watchMessage}</Text>}
      {PROFILE_CONTROLS.map(control => {
        const limit = controls.limits[control];
        if (limit !== undefined) {
          return (
            <Text key={control} style={styles.body}>
              {control}: {limit}
            </Text>
          );
        }
        switch (control) {
          case 'ScoringPreset':
            return (
              <TvButton
                key={control}
                label={`Scoring preset: ${profile.scoringPreset} (select to switch)`}
                onPress={() => set({...profile, scoringPreset: cycle(SCORING_PRESETS, profile.scoringPreset)})}
              />
            );
          case 'Presentation':
            return (
              <TvButton
                key={control}
                label={`Presentation: ${profile.presentation}`}
                onPress={() => set({...profile, presentation: cycle(PRESENTATIONS, profile.presentation)})}
              />
            );
          case 'Excitement':
            return (
              <TvButton
                key={control}
                label={`Excitement: ${profile.excitement}`}
                onPress={() => set({...profile, excitement: cycle(EXCITEMENT_LEVELS, profile.excitement)})}
              />
            );
          case 'Frequency':
            return (
              <TvButton
                key={control}
                label={`Alert frequency: at most one alert per ${profile.minGapSeconds} s per game`}
                onPress={() => set({...profile, minGapSeconds: cycle([0, 60, 120, 300, 600], profile.minGapSeconds)})}
              />
            );
          case 'SpoilerDelay':
            return (
              <TvButton
                key={control}
                label={`Spoiler delay: ${profile.spoilerDelaySeconds} s`}
                onPress={() =>
                  set({...profile, spoilerDelaySeconds: cycle([0, 30, 45, 60, 120], profile.spoilerDelaySeconds)})
                }
              />
            );
          case 'SwitchingConfirmation':
            return (
              <TvButton
                key={control}
                label={`Confirm before switching: ${onOff(profile.switchingConfirm)}`}
                onPress={() => set({...profile, switchingConfirm: !profile.switchingConfirm})}
              />
            );
          case 'PanelVisibility':
            return (
              <TvButton
                key={control}
                label={`Panel visible: ${onOff(profile.panel.visible)}`}
                onPress={() => set({...profile, panel: {visible: !profile.panel.visible}})}
              />
            );
          case 'DetectionOptIn':
            return (
              <TvButton
                key={control}
                label={`Installed-app detection: ${onOff(profile.detectionOptIn)}`}
                onPress={() => set({...profile, detectionOptIn: !profile.detectionOptIn})}
              />
            );
          case 'Voice':
            return (
              <TvButton
                key={control}
                label={`Voice alerts: ${onOff(profile.voiceEnabled)}`}
                onPress={() => set({...profile, voiceEnabled: !profile.voiceEnabled})}
              />
            );
          case 'GameDay':
            return (
              <View key={control}>
                <TvButton
                  label={`Game-day mode: ${onOff(profile.gameDay.enabled)} (${profile.gameDay.periods.length} periods)`}
                  onPress={() => set({...profile, gameDay: {...profile.gameDay, enabled: !profile.gameDay.enabled}})}
                />
                <WindowListEditor
                  label="Game-day periods"
                  windows={profile.gameDay.periods}
                  fallback={{startMinute: 13 * 60, endMinute: 23 * 60}}
                  onChange={periods => set({...profile, gameDay: {...profile.gameDay, periods}})}
                />
              </View>
            );
          case 'Selections':
            return (
              <View key={control}>
                {(
                  [
                    ['Leagues', 'leagues'],
                    ['Teams', 'teams'],
                    ['Players', 'players'],
                    ['Favorite teams', 'favoriteTeams'],
                  ] as const
                ).map(([label, field]) => (
                  <NameListEditor
                    key={field}
                    label={label}
                    values={[...profile.selections[field]]}
                    onToggle={value => {
                      const next = new Set(profile.selections[field]);
                      if (next.has(value)) next.delete(value);
                      else next.add(value);
                      set({...profile, selections: {...profile.selections, [field]: next}});
                    }}
                  />
                ))}
              </View>
            );
          case 'TeamLeague':
            return (
              <TeamLeagueEditor
                key={control}
                profile={profile}
                onChange={teamLeague => set({...profile, teamLeague})}
              />
            );
          case 'AlertTypes':
            return (
              <View key={control}>
                <Text style={styles.body}>Alert types: {[...profile.alertTypes].join(', ') || 'none'}</Text>
                {(['RedZone', 'PlayerScore', 'CloseGame'] as const).map(type => (
                  <TvButton
                    key={type}
                    label={`${type}: ${onOff(profile.alertTypes.has(type))}`}
                    onPress={() => {
                      const next = new Set(profile.alertTypes);
                      if (next.has(type)) next.delete(type);
                      else next.add(type);
                      set({...profile, alertTypes: next});
                    }}
                  />
                ))}
              </View>
            );
          case 'QuietHours':
            return (
              <WindowListEditor
                key={control}
                label="Quiet hours"
                windows={profile.quietHours}
                fallback={{startMinute: 22 * 60, endMinute: 7 * 60}}
                onChange={quietHours => set({...profile, quietHours})}
              />
            );
          case 'ProviderPreference':
            return (
              <ProviderPreferenceEditor
                key={control}
                profile={profile}
                onChange={providerPref => set({...profile, providerPref})}
              />
            );
          default:
            return null;
        }
      })}
      <TvButton label="Save profile" onPress={save} />
      <PanelSection controller={controller.current} snapshot={snapshot} />
    </ScrollView>
  );
}

function PanelSection({controller, snapshot}: {controller: PanelController | null; snapshot: PanelSnapshot | null}) {
  if (controller === null || !controller.visible) return null;
  const now = Date.now();
  return (
    <View>
      <Text style={styles.title}>Lineup panel</Text>
      <Text style={styles.body}>Team/league: {controller.teamLeague || 'none'}</Text>
      {snapshot === null ? (
        <Text style={styles.body}>Panel unavailable</Text>
      ) : (
        <>
          <Text style={styles.body}>
            {snapshot.sport != null ? `${snapshot.sport} · ${PanelText.basis(snapshot.basis)}` : PanelText.basis(snapshot.basis)}
          </Text>
          {snapshot.rows.map(row => (
            <Text
              key={row.playerId}
              style={[
                styles.panelRow,
                controller.focused?.kind === 'row' && controller.focused.playerId === row.playerId && styles.panelFocused,
              ]}>
              {row.name}: {PanelText.value(row.points, now)} ({PanelText.gameStatus(row.gameStatus)})
            </Text>
          ))}
          <Text style={[styles.panelScore, controller.focused?.kind === 'total' && styles.panelFocused]}>
            Total: {PanelText.value(snapshot.teamTotal, now)}
          </Text>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {flex: 1, backgroundColor: '#101418', paddingHorizontal: 64, paddingVertical: 32},
  title: {color: '#ffffff', fontSize: 40, marginBottom: 16},
  body: {color: '#e8edf2', fontSize: PanelTextSizes.bodyPx, marginBottom: 12},
  code: {color: '#ffffff', fontSize: 72, marginBottom: 16},
  button: {
    backgroundColor: '#2a3440',
    borderColor: '#2a3440',
    borderWidth: 3,
    borderRadius: 8,
    paddingHorizontal: 20,
    paddingVertical: 10,
    marginBottom: 10,
    alignSelf: 'flex-start',
  },
  buttonFocused: {borderColor: '#ffb020', backgroundColor: '#3a4656'},
  buttonText: {color: '#ffffff', fontSize: PanelTextSizes.bodyPx},
  input: {
    color: '#ffffff',
    backgroundColor: '#1c232c',
    fontSize: PanelTextSizes.bodyPx,
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginBottom: 10,
    minWidth: 320,
  },
  banner: {backgroundColor: '#243447', borderRadius: 8, padding: 20, marginBottom: 16},
  panelRow: {color: '#e8edf2', fontSize: PanelTextSizes.bodyPx, marginBottom: 8},
  panelScore: {color: '#ffffff', fontSize: PanelTextSizes.scorePx, marginBottom: 8},
  panelFocused: {color: '#ffb020'},
});

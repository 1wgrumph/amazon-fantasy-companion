---
spike: SP-8
slice: P2-X11
verdict: FAILS
device:
  model: AFTKM
  fire_os: Fire OS 8.1.8.5 (RS8185.3891N)
  android_release: "11"
  api_level: 30
started_at: 2026-10-20T12:51:00Z
ended_at: 2026-10-20T13:05:00Z
first_install_at: not applicable (no probe APK installed; read-only probes)
unblocks: []
conditional: C8 (OD-AFC-03 stretch; terminal no-offer disposition recorded)
---

# SP-8 Alexa announcement / tuning route verdict

**Verdict: FAILS** for a supported Alexa route. No documented or
on-device surface lets a third-party Fire OS TV app (a) speak an in-app
alert through Alexa (AFC-PR-022 as an Alexa announcement) or (b) invoke
Alexa-assisted tuning to a resolved game/channel (AFC-PR-036).
**OD-AFC-03 terminal disposition: no-offer.** Both UIDs pass by not
offering voice, per their own condition (an implemented and verified
route). No Alexa offer, toggle, or product code follows from this spike;
either UID would need a verified route and separate authorization.

Test article: the leased stick above (device address, serial, and
account data deliberately not recorded). All probes were read-only
(`pm`/`cmd package`/`dumpsys`/`settings get`); no package was installed,
enabled, disabled, or cleared. Full commands with exit codes:
`evidence/probe-commands.txt`, `evidence/probe2-commands.txt`.

## Routes tried

1. **Alexa announcement from the TV app** — `not_supported`.
   Amazon's Fire TV voice overview lists exactly three voice-enabling
   techniques for Fire TV apps: Video Skills Kit, Media Session API, and
   In-App Voice Scrolling and Selection; none speaks app-generated text
   (https://developer.amazon.com/docs/fire-tv/voice-enable-your-app-and-content.html).
   "Alexa Announcements" is a user-initiated intercom between a customer's
   own Alexa devices, not an app API. On-device, the Alexa packages
   (`com.amazon.tv.alexanotifications`, `com.amazon.tv.alexaalerts`,
   `com.amazon.alexadirectivebrokerservice`,
   `com.amazon.alexamediaplayer.runtime.ftv`) are system packages; no
   exported third-party "speak this text" service or intent was found
   (`evidence/probe-commands.txt`, `evidence/probe2-commands.txt`).
   Does not unblock AFC-PR-022.
2. **Alexa Proactive Events API (skill-side notification)** — `unknown`
   as a product route, `not_supported` as a TV-app route. Proactive
   Events lets an Alexa *skill* send schema-fixed events that surface as
   Alexa notifications, after the customer enables the skill and grants
   notification permission
   (https://developer.amazon.com/en-US/docs/alexa/smapi/proactive-events-api-reference.html).
   It is not an in-app Fire TV API, carries no free-form alert speech,
   and was not implemented or exercised here (no skill, no account
   linking in scope). An unimplemented route is not offered.
   Does not unblock AFC-PR-022 or AFC-PR-036.
3. **Android TextToSpeech (non-Alexa voice)** — `limited`. The stick
   carries two TTS engines answering `android.intent.action.TTS_SERVICE`
   (`com.ivona.tts.oem`, `com.svox.pico`; `evidence/probe-commands.txt`),
   so the standard Android `TextToSpeech` API has an engine to bind to
   (https://developer.android.com/reference/android/speech/tts/TextToSpeech).
   Limits: this is not Alexa; `tts_default_synth` reads `null`; no
   end-to-end speak was exercised (evidence-only spike, no probe APK),
   so audibility over provider playback and audio-focus behavior are
   unverified. Recorded as a candidate for a future, separately
   authorized AFC-PR-022 investigation only. Does not unblock
   AFC-PR-022 today and is irrelevant to AFC-PR-036.
4. **Video Skills Kit (VSK) Alexa tuning** — `not_supported` as
   app-invoked tuning. VSK is the reverse direction: the customer asks
   Alexa, and Alexa sends directives (search, launch, transport,
   channel-change within the app's own catalog-integrated content) to
   the app via Lambda + Alexa Client Library + ADM, with catalog
   integration required
   (https://developer.amazon.com/docs/video-skills-fire-tv-apps/introduction.html).
   No documented API lets the app ask Alexa to tune to another
   provider's game/channel. Does not unblock AFC-PR-036.
5. **Media Session voice transport** — `limited`. Documented and real,
   but it only voice-enables playback transport (pause/resume/skip) of
   the app's own media session after adding an Alexa manifest permission
   (https://developer.amazon.com/docs/fire-tv/mediasession-api-integration.html).
   It neither announces alerts nor tunes. Unblocks neither UID.
6. **VoiceInteractionService / ASSIST** — `not_supported`.
   `cmd package query-services -a android.service.voice.VoiceInteractionService`
   returns "No services found"; `dumpsys voiceinteraction` shows
   "(No active implementation)"; `android.intent.action.ASSIST` resolves
   to the system priv-app `com.amazon.vizzini`
   (`evidence/probe-commands.txt`). A third-party app cannot register as
   or invoke this surface as a tuning/announcement API.
7. **In-app voice scrolling and selection** — `limited`. Alexa phrases
   map to D-pad events, and Amazon manually activates the feature per
   app on the back end
   (https://developer.amazon.com/docs/fire-tv/voice-scrolling-and-selection.html).
   Navigation only; not an announcement or tuning offer. Unblocks
   neither UID.

## Observed result and limits

- Strongest honest outcomes: Alexa announcement `not_supported`;
  Alexa-assisted tuning `not_supported`; non-Alexa TTS `limited`
  (engine present, speech unverified); Proactive Events `unknown`
  (skill-side, unimplemented).
- `unblocks` is empty: AFC-PR-022 and AFC-PR-036 remain satisfied by
  the no-offer branch. The companion app already keeps voice off
  without a verified route; this spike changes no product code.
- Absence of an owner Alexa skill/entitlement was not treated as the
  blocker: routes 1, 4, and 6 fail on documented platform shape and
  on-device surface, not on account state.
- Vega: paused by owner; no Vega work was done and no Vega claim is
  made (RISK-AFC-P2-14). No live X09/X10 flow is claimed.
- Developer feedback: DX-SP8-01 — Amazon's Fire TV "Voice" docs index
  only VSK/MediaSession/scrolling; a third-party developer cannot
  discover from that index whether app-initiated speech exists at all.
  The on-device TTS engines are the only speak-capable surface found,
  and they are undocumented in the Fire TV voice section. Evidence:
  `evidence/probe-commands.txt`.

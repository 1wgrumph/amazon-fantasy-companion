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
conditional: C8
---

# SP-8 Alexa announcement / tuning route verdict

**Verdict: FAILS** for a supported Alexa route. Among the documented
routes and on-device surfaces inspected below, none established support
for a third-party Fire OS TV app to (a) speak an in-app alert through
Alexa (AFC-PR-022 as an Alexa announcement) or (b) invoke Alexa-assisted
tuning to a resolved game/channel (AFC-PR-036); where inspection did not
establish support or its absence, the outcome below is `unknown`.
Conditional C8 is the OD-AFC-03 stretch; its terminal no-offer
disposition is recorded here.
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
   own Alexa devices, not an app API. On-device, `pm list packages`
   listed Alexa packages including
   `com.amazon.tv.alexanotifications`, `com.amazon.tv.alexaalerts`,
   `com.amazon.alexadirectivebrokerservice`, and
   `com.amazon.alexamediaplayer.runtime.ftv`
   (`evidence/probe-commands.txt`). Package details were inspected
   only for `com.amazon.tv.alexanotifications`, whose `dumpsys package`
   output showed system/priv-app receivers and a content provider but
   no exported third-party "speak this text" service or intent
   (`evidence/probe2-commands.txt`). The other listed packages were
   not inspected for exported components: `unknown`.
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
   the app via the cloud-side implementation (Lambda + Alexa Client
   Library + ADM), with catalog integration required; the same cited
   VSK overview also documents an app-only VSK Agent/broadcast-intent
   implementation, which is likewise Alexa-to-app in direction
   (https://developer.amazon.com/docs/video-skills-fire-tv-apps/introduction.html).
   No documented API lets the app ask Alexa to tune to another
   provider's game/channel. Does not unblock AFC-PR-036.
5. **Media Session voice transport** — `limited`. Documented and real,
   but it only voice-enables playback transport (pause/resume/skip) of
   the app's own media session after adding an Alexa manifest permission
   (https://developer.amazon.com/docs/fire-tv/mediasession-api-integration.html).
   It neither announces alerts nor tunes. Unblocks neither UID.
6. **VoiceInteractionService / ASSIST** — `not_supported` as an active
   standard voice-interaction service; `unknown` for third-party use of
   the exported ASSIST activity. The standard Android surface is
   `VoiceInteractionService`
   (https://developer.android.com/reference/android/service/voice/VoiceInteractionService).
   `cmd package query-services -a android.service.voice.VoiceInteractionService`
   returns "No services found"; `dumpsys voiceinteraction` shows
   "(No active implementation)"; `android.intent.action.ASSIST` resolves
   to an exported (`exported=true`) activity in the system priv-app
   `com.amazon.vizzini` (`evidence/probe-commands.txt`). These
   observations establish no active standard service and an exported
   ASSIST activity only; whether a third-party app may invoke that
   activity as a tuning/announcement API was not exercised and no
   documented prohibition was established: `unknown`.
7. **In-app voice scrolling and selection** — `limited`. Alexa phrases
   map to D-pad events, and Amazon manually activates the feature per
   app on the back end
   (https://developer.amazon.com/docs/fire-tv/voice-scrolling-and-selection.html).
   Navigation only; not an announcement or tuning offer. Unblocks
   neither UID.

## Observed result and limits

- Strongest honest outcomes: Alexa announcement `not_supported` on
  the documented/inspected surfaces (uninspected Alexa packages and
  ASSIST-activity use `unknown`, routes 1 and 6); Alexa-assisted tuning
  `not_supported` on the documented routes; non-Alexa TTS `limited`
  (engine present, speech unverified); Proactive Events `unknown`
  (skill-side, unimplemented).
- `unblocks` is empty: AFC-PR-022 and AFC-PR-036 remain satisfied by
  the no-offer branch. The companion app already keeps voice off
  without a verified route; this spike changes no product code.
- Absence of an owner Alexa skill/entitlement was not treated as the
  blocker: routes 1 and 4 rest on the documented platform shape cited
  there, and route 6 on the probed absence of an active standard
  service (`evidence/probe-commands.txt`), not on account state; the
  `unknown` items in routes 1 and 6 were not resolved either way.
- Vega: paused by owner; no Vega work was done and no Vega claim is
  made (RISK-AFC-P2-14). No live X09/X10 flow is claimed.
- Developer feedback: DX-SP8-01 — Amazon's Fire TV "Voice" docs index
  only VSK/MediaSession/scrolling; a third-party developer cannot
  discover from that index whether app-initiated speech exists at all.
  The on-device TTS engines are the only speak-capable surface found,
  and they are undocumented in the Fire TV voice section. Evidence:
  `evidence/probe-commands.txt`.

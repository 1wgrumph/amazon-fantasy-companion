# P2-A04 device run (2026-10-20)

APK `ad9b0435…0ea880`, AFTKM Fire OS 8.1.8.5. Registry and X03 PR 1 verdict
on main applied as-is: only Prime Video has a `fire_os` route
(`https://watch.amazon.com/search`, `searchOpened`); the other four
providers are `REGISTRY_ROUTE_GAP`, and with
`currentAttemptObservation: none` no started launch may report more than
`accessUnknown`.

Executed: installed/absent inventory (`pm path`), leanback resolution for
Prime Video, and a cold intent-level re-probe of the registered Prime
Video search URI (foreground readback `IgnitionActivity`; first frame
black while loading, second frame the search screen,
`evidence/visual/PRIVATE-EVIDENCE.md` (Prime Video search screen, provider UI, withheld)). Prime Video was
force-stopped afterwards; nothing was installed, uninstalled, signed in,
or purchased.

Not executed: app-level Watch attempts and the confirm-switch /
outcome-shown / fullscreen-leaves states. They start from an alert card,
which needs a synthetic dev alert; the AWS CLI session is expired and
`aws login` is owner-only (`FIXTURE_AWS_SESSION_EXPIRED`). The
uninstall-a-provider `appAbsent` check was not run: the only installed
provider app is the Prime Video system app. `gameOpened` stays with the
unlanded X03 PR 2 live-TNF window (`X03_PR2_PENDING`); Alexa tuning stays
hidden (`X11_VERDICT_PENDING` for the route).

## 2026-10-20 fixture rerun

AWS session valid again. Only the former
`FIXTURE_AWS_SESSION_EXPIRED` steps (indexes 1 and 4) were rerun;
`REGISTRY_ROUTE_GAP`, `X03_PR2_PENDING` and `X11_VERDICT_PENDING`
stand. APK as found, sha256 `1d80c6822182399794bbe4cec27198a0a31da58e3533ebcb9acf431a2729b988`. From the fixture
alert card: Watch first armed the switching confirmation
(`evidence/visual/P2-A04/fixture-rerun-confirm-switch.png`), the
second OK left AFC fullscreen for Prime Video (dumpsys foreground
metadata only, no provider capture), and on return the panel
reported `Watch: could not confirm the game is playing.`
(`fixture-rerun-watch-outcome.png`), i.e. one truthful
`accessUnknown` outcome: **PASS** for both steps (Prime Video
route only; no `gameOpened` claim). Receipt:
`device-receipt-fixture-rerun.json`.

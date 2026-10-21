# Private evidence

Committed images show the Amazon Fantasy Companion UI only. The captures
below contain provider UI, title art, advertisements, broadcast or team
logos, or a third-party site. Their bytes are not in this repository.

Each original is stored at `<private-evidence>/<group>/<file>`. `<group>`
is the directory name under `evidence/visual/` in the former path, and
`<file>` is that path's basename.

Capture time is the probe clock in the spike log when that log names the
file. Otherwise it is the author date of the commit that added the file
(`git log --follow --diff-filter=A --format=%aI`). No per-capture clock
was invented. Probe times come from the `== Probe:` header in
`spikes/sp3-provider-links/device-log.txt`. Git author dates are
`57a8dacc9ed1ed432488c2a3c04fb77b1387d4be` (SP-2 first sweep),
`75c83ca4ecc4a8925c1e212095cdd06e6a5d3431` (SP-2 repair 9),
`380bfd841db94d148a146b62fc4a3521ca4f678b` (SP-4), and
`21dc8bb98fee12a9f8d4b185dc2f4f253b6768b3` (P2-A04; the device receipt
date is 2026-10-20). SP-2 `attempts.txt` and SP-4 `commands.txt` record
the session day and do not record a per-capture clock.

| Former path | Private copy | sha256 | Capture time | Description |
| --- | --- | --- | --- | --- |
| `evidence/visual/P2-A04/prime-video-search.png` | `<private-evidence>/P2-A04/prime-video-search.png` | `47c82cd5f78331359613ba9802b83ef318ed55b60d60b17fd4c7ca44f3ce2f99` | `2026-10-20T08:26:48-05:00` | Prime Video search screen (provider UI, withheld) |
| `evidence/visual/sp2-notify/attempt2-prime-home.png` | `<private-evidence>/sp2-notify/attempt2-prime-home.png` | `efe248b84ca015d1e812b9f3788d9a847312cbe60a84b5e96fb3ad5075963044` | `2026-10-16T14:51:10-05:00` | Fire TV home after the Prime Video launch attempt (provider UI, withheld) |
| `evidence/visual/sp2-notify/attempt3-prime-after-select.png` | `<private-evidence>/sp2-notify/attempt3-prime-after-select.png` | `c8e22045307a4f2c840c11366f2ad420e541242cf6f80277229544598aca4d8b` | `2026-10-16T14:51:10-05:00` | Prime Video screen after title select (provider UI, withheld) |
| `evidence/visual/sp2-notify/attempt3-prime-home.png` | `<private-evidence>/sp2-notify/attempt3-prime-home.png` | `2b3233be64bba432b330d355e7b775d415a5bc46026106ec3d286eacf93d8d1f` | `2026-10-16T14:51:10-05:00` | Prime Video title screen before playback (provider UI, withheld) |
| `evidence/visual/sp2-notify/attempt5-dpad-up.png` | `<private-evidence>/sp2-notify/attempt5-dpad-up.png` | `8c5a7b442643b3b807bfbf18346baeb8efcf5b97df967a81c8b83e0f8129cc00` | `2026-10-16T14:51:10-05:00` | Prime Video player after DPAD_UP (provider UI, withheld) |
| `evidence/visual/sp2-notify/attempt6-dismiss-target.png` | `<private-evidence>/sp2-notify/attempt6-dismiss-target.png` | `f29cbd60d304628f3269139ffd9dd53b4733174f6803b3f457833fbe3c2dd6e5` | `2026-10-16T14:51:10-05:00` | Fire TV home when the dismiss target was pressed (provider UI, withheld) |
| `evidence/visual/sp2-notify/attempt6-home.png` | `<private-evidence>/sp2-notify/attempt6-home.png` | `d5e8fb9ea352cc704253dd6edaf219518200e2a6e69e326300524c99b9fac722` | `2026-10-16T14:51:10-05:00` | Fire TV home (provider UI, withheld) |
| `evidence/visual/sp2-notify/attempt6-notif-key.png` | `<private-evidence>/sp2-notify/attempt6-notif-key.png` | `eb9230888043fea4f435790a9d48fff1e1518240608ac6a6b6010eeff6cec4b4` | `2026-10-16T14:51:10-05:00` | Fire TV home after KEYCODE_NOTIFICATION (provider UI, withheld) |
| `evidence/visual/sp2-notify/attempt7-home-headsup.png` | `<private-evidence>/sp2-notify/attempt7-home-headsup.png` | `145bb53e867b2f54181c1b0d18ba88ea8b210742ef55bdd198563c3eb336944f` | `2026-10-16T14:51:10-05:00` | Fire TV home during a heads-up post (provider UI, withheld) |
| `evidence/visual/sp2-notify/repair9-fsi-dpad-up.png` | `<private-evidence>/sp2-notify/repair9-fsi-dpad-up.png` | `837b6a636dcd83569775d999b834d50b38218bedea4f0918a3381ed566c9a418` | `2026-10-16T15:41:41-05:00` | Prime Video player controls after DPAD_UP (provider UI, withheld) |
| `evidence/visual/sp3-provider-links/local-broadcast-home.png` | `<private-evidence>/sp3-provider-links/local-broadcast-home.png` | `4fc5bbaa6e13e49237430c42920647b44030e2f8c9fbd873eb42e0514c8c69e0` | `2026-10-16T20:08:09Z` | Fire TV home after the local-broadcast launch attempt (provider UI, withheld) |
| `evidence/visual/sp3-provider-links/prime-video-detail-cold.png` | `<private-evidence>/sp3-provider-links/prime-video-detail-cold.png` | `efa2d3f94bb134d429a47e18b03cb2683c77d8b0c94c4541f4183ae26c70fb14` | `2026-10-16T21:06:09Z` | Prime Video title detail screen (provider UI, withheld) |
| `evidence/visual/sp3-provider-links/prime-video-home.png` | `<private-evidence>/sp3-provider-links/prime-video-home.png` | `7629bd89773a519e1af0896fbe3c1dd4cec56bf6f0a040b7548ec92b96873cb5` | `2026-10-16T20:01:32Z` | Prime Video home screen (provider UI, withheld) |
| `evidence/visual/sp3-provider-links/prime-video-search.png` | `<private-evidence>/sp3-provider-links/prime-video-search.png` | `2b2c1732b526af97ac94a1a8564573c08909729fc1f2e8ee959d93ca6bcdd1d8` | `2026-10-16T20:10:00Z` | Prime Video search screen (provider UI, withheld) |
| `evidence/visual/sp3-provider-links/youtube-tv-view-browser.png` | `<private-evidence>/sp3-provider-links/youtube-tv-view-browser.png` | `72a4b0a7575376a5cf6825da1afe2116abdfa5f4e4bf97b0bd806bcc4457b649` | `2026-10-16T20:07:29Z` | YouTube TV site in the browser (provider UI, withheld) |
| `evidence/visual/sp4-panel-video/r1-provider-pip-home.png` | `<private-evidence>/sp4-panel-video/r1-provider-pip-home.png` | `db9ca4d861ea442213f6187cc6f6d2422fb786ebec9e0bd8acd07def16cf47d3` | `2026-10-16T14:30:18-05:00` | Fire TV home after the provider picture-in-picture attempt (provider UI, withheld) |
| `evidence/visual/sp4-panel-video/r1b-return-prime.png` | `<private-evidence>/sp4-panel-video/r1b-return-prime.png` | `5970a49093f2c619947d2f437eb4e502953222eb56448a9435cb7e56b8edf70b` | `2026-10-16T14:30:18-05:00` | Prime Video home screen with team logos (provider UI, withheld) |
| `evidence/visual/sp4-panel-video/r2-spike-pip-entered.png` | `<private-evidence>/sp4-panel-video/r2-spike-pip-entered.png` | `e9a37c6ac640b39a6e4d2d7ced07a3091496e3510558617bd1b508cc8be8a7a2` | `2026-10-16T14:30:18-05:00` | Fire TV home with the spike panel over it (provider UI, withheld) |
| `evidence/visual/sp4-panel-video/r2-spike-pip-over-prime.png` | `<private-evidence>/sp4-panel-video/r2-spike-pip-over-prime.png` | `3e3de2e78148be1da8aa5d27b335993cf51c871b77047e47b3644cc32cafbb53` | `2026-10-16T14:30:18-05:00` | Prime Video title screen with the spike panel over it (provider UI, withheld) |
| `evidence/visual/sp4-panel-video/r6-final-prime.png` | `<private-evidence>/sp4-panel-video/r6-final-prime.png` | `bed3b55f47f380abfea4cdc9476e500944e22e19c300b52b5b01dd02a201162d` | `2026-10-16T14:30:18-05:00` | Prime Video title screen at the end of the panel sweep (provider UI, withheld) |

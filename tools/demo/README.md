# Demo cuts

Repeatable ffmpeg cuts for the filmable shot list in
[the demo plan](../../docs/submission/demo-plan.md) (S1–S7, 156 s).
Narration is burned in as caption text. The audio track is silent.
No provider video and no provider app screen is used. Where the Watch
shot would show one, the build appends the `searchOpened` title card.

`cuts.json` is the composition: shot ids, raw file names, in/out times,
captions, title cards, and the segments of each output.

## Outputs

| Output | File | What it contains |
| --- | --- | --- |
| Main demo | `demo-main.mp4` | S1–S7 in order, 156 s |
| Teaser | `demo-teaser.mp4` | 30 s: problem, replay alert, Watch hand-off, panel, close |
| Alerts | `feature-alerts.mp4` | S3, with the replay label for the whole clip |
| Watch | `feature-watch.mp4` | S4 capture plus the `searchOpened` title card |
| Panel | `feature-panel.mp4` | S5 full-screen panel |
| Linking | `feature-linking.mp4` | Title card only. The filmable list has no linking capture, confirmation is owner-only, and the card shows no code |
| Trimmed raw | `raw-S1.mp4` … `raw-S7.mp4` | Each shot trimmed to its in/out, with its shot id and caption |

S4 is end-aligned. The build keeps the last 22 s of `S4.mp4` (the
hand-off) and then adds the 8 s title card, so the shot stays 30 s.
Other shots are trimmed from the start to their planned duration.
Every output is 1920x1080, 30 fps, H.264, with a silent AAC track.

A raw directory written by `make_synthetic.sh` contains a `SYNTHETIC`
marker. The build then burns `SYNTHETIC — pipeline test` into the
top-right corner of every output. A real capture directory does not
have that marker, so the submission cuts do not carry the label.

## Prove the pipeline without a device

```bash
bash tools/demo/make_synthetic.sh ~/.local/share/afc-tools/demo-cuts/synthetic-2026-10-21/raw
bash tools/demo/build_cuts.sh \
  ~/.local/share/afc-tools/demo-cuts/synthetic-2026-10-21/raw \
  ~/.local/share/afc-tools/demo-cuts/synthetic-2026-10-21
```

`make_synthetic.sh` writes `S1.mp4` through `S7.mp4`, each a 1920x1080
colour plate at that shot's planned duration, with the text
`SYNTHETIC S<n>` in the middle. The build refuses to start if any of
those files is missing or is not 1920x1080. Running the build twice on
the same raw directory produces the same bytes for each output.

## Final X12 capture

Capture on the final APK only, one file per shot, companion UI only.
`adb shell screenrecord` stops at 180 s, and every shot below is shorter
than that, so record each shot as its own file. `--size 1920x1080` is
required; the build rejects any other size. Stop S4 at the companion
hand-off, before any provider screen is visible. The build adds the
title card. Do not record a code, an account, a credential, or a device
address.

| Shot | File | `--time-limit` | Stop |
| --- | --- | --- | --- |
| S1 | `S1.mp4` | 12 | After the companion launches |
| S2 | `S2.mp4` | 22 | After the labeled manual lineup is on screen |
| S3 | `S3.mp4` | 28 | After the replay alert. Keep the replay label in frame |
| S4 | `S4.mp4` | 30 | At the hand-off, before any provider screen. Record at least 22 s |
| S5 | `S5.mp4` | 32 | After the full-screen panel |
| S6 | `S6.mp4` | 18 | After `accessUnknown` is shown |
| S7 | `S7.mp4` | 14 | After the alert-type change and the limits |

Replace `S1` with the shot id. Pull the file into the raw directory and
remove it from the device:

```bash
adb shell screenrecord --size 1920x1080 --time-limit 12 /sdcard/S1.mp4
adb pull /sdcard/S1.mp4 <raw-dir>/S1.mp4
adb shell rm /sdcard/S1.mp4
```

Then one build command:

```bash
bash tools/demo/build_cuts.sh <raw-dir> <out-dir>
```

The output directory must not be the raw directory. The build reads
`tools/demo/cuts.json` beside this script.

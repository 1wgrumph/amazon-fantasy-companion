# P2-X12 demo-cut pipeline proof

Run date 2026-10-20. The directory and this file use the packet names
`synthetic-2026-10-21` and `pipeline-proof-2026-10-21.md`.
Synthetic colour plates only. No device, no adb, and no backend.
Encoder: `ffmpeg version 8.0.1-3ubuntu2+esm5 Copyright (c) 2000-2025 the FFmpeg developers`.

Raw clips and outputs are under
`~/.local/share/afc-tools/demo-cuts/synthetic-2026-10-21/`.
The raw clips are in `raw/`. `make_synthetic.sh` wrote the `SYNTHETIC`
marker there, so every output carries the corner label
`SYNTHETIC — pipeline test`.

The linking feature is a title card. The filmable shot list has no
device-linking capture, and the card shows no code.

## Outputs

| File | Duration (s) | Resolution | sha256 | Second build sha256 |
| --- | --- | --- | --- | --- |
| `demo-main.mp4` | 156.021333 | 1920x1080 | `cc647bea18e85f47cb70e60afddb87bb5074b2b2346d8d4e7df26d60b12f3f40` | `cc647bea18e85f47cb70e60afddb87bb5074b2b2346d8d4e7df26d60b12f3f40` |
| `demo-teaser.mp4` | 30.021333 | 1920x1080 | `87bff3359f8e3ce5abdfd35641b041065a77b60603d8bd1277ae2b3d96cd75bb` | `87bff3359f8e3ce5abdfd35641b041065a77b60603d8bd1277ae2b3d96cd75bb` |
| `feature-alerts.mp4` | 28.021333 | 1920x1080 | `a233c5137e60f35e8ec4cc4b08343515bd2f846b7b2557662fc7c7a1b6442a3e` | `a233c5137e60f35e8ec4cc4b08343515bd2f846b7b2557662fc7c7a1b6442a3e` |
| `feature-watch.mp4` | 30.021333 | 1920x1080 | `ed76a64fbdb9ad58feaaf0cfc34371b86fff7feb8b6bb903816e619e5e389f6e` | `ed76a64fbdb9ad58feaaf0cfc34371b86fff7feb8b6bb903816e619e5e389f6e` |
| `feature-panel.mp4` | 32.021333 | 1920x1080 | `48af7f45a44f9863e77217b7947291aaf0dc96713f5e9eb7182009c425ea0e23` | `48af7f45a44f9863e77217b7947291aaf0dc96713f5e9eb7182009c425ea0e23` |
| `feature-linking.mp4` | 8.021333 | 1920x1080 | `ececee607af05835cdefe0229d0df30bda8606f0da1d56c367eda9fd279ccf6e` | `ececee607af05835cdefe0229d0df30bda8606f0da1d56c367eda9fd279ccf6e` |
| `raw-S1.mp4` | 12.021333 | 1920x1080 | `391b819813d4e9170cc84108266379acc067dfd06fdd1205d6940bc2fc888a5c` | `391b819813d4e9170cc84108266379acc067dfd06fdd1205d6940bc2fc888a5c` |
| `raw-S2.mp4` | 22.021333 | 1920x1080 | `c5e72b96ea03b8139c4cfbe95f4f42a7595b25f24c4a641de0b04546f2bf92d3` | `c5e72b96ea03b8139c4cfbe95f4f42a7595b25f24c4a641de0b04546f2bf92d3` |
| `raw-S3.mp4` | 28.021333 | 1920x1080 | `abcde0558cce3507a25aa9c71dd0b1a68f75945fb61510dcfd040ce0d39651b4` | `abcde0558cce3507a25aa9c71dd0b1a68f75945fb61510dcfd040ce0d39651b4` |
| `raw-S4.mp4` | 22.021333 | 1920x1080 | `4dd9e7a69521338666aa19d4e52c986332b843afe01d873429c1084cb10b74aa` | `4dd9e7a69521338666aa19d4e52c986332b843afe01d873429c1084cb10b74aa` |
| `raw-S5.mp4` | 32.021333 | 1920x1080 | `175ad52a5bee778980e9869223284fb6b3954deb397045b16f4f17433720446b` | `175ad52a5bee778980e9869223284fb6b3954deb397045b16f4f17433720446b` |
| `raw-S6.mp4` | 18.021333 | 1920x1080 | `ab89498dd285043083626c9a32a5aa39f339d134158688e6475714d5bc461da7` | `ab89498dd285043083626c9a32a5aa39f339d134158688e6475714d5bc461da7` |
| `raw-S7.mp4` | 14.021333 | 1920x1080 | `d839f3c061aa87229032aa3d0acde2267107c79677e3f808d49ac5e38284b0a6` | `d839f3c061aa87229032aa3d0acde2267107c79677e3f808d49ac5e38284b0a6` |

The duration column is the container duration. The picture track is the planned length at 30 fps: main 156.000 s (4680 frames), teaser 30.000 s (900 frames), and the other outputs likewise on their planned lengths. The container is 0.021333 s longer because the silent AAC track includes one encoder priming block.

## Determinism

Two consecutive `build_cuts.sh` runs on the same synthetic raw clips produced the same sha256 for every output file.

## Refusals

A raw directory missing `S4.mp4`:

```text
bash tools/demo/build_cuts.sh <raw-dir-missing-S4> <out-dir>
exit 1
missing raw clip: S4.mp4
```

A raw directory whose `S1.mp4` is 1280x720:

```text
bash tools/demo/build_cuts.sh <raw-dir-wrong-size> <out-dir>
exit 1
S1.mp4 is 1280x720, required 1920x1080
```

## Commands

| Command | Exit |
| --- | --- |
| `bash tools/demo/make_synthetic.sh <raw-dir>` | 0 |
| `bash tools/demo/build_cuts.sh <raw-dir> <out-dir>` (build 1) | 0 |
| `bash tools/demo/build_cuts.sh <raw-dir> <out-dir>` (build 2) | 0 |
| missing `S4.mp4` | 1 |
| `S1.mp4` at 1280x720 | 1 |

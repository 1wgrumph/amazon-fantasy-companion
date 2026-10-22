# Third-party notices

## GridMarket specification tools (vendored as tools/spec/)

Source: https://github.com/alphazede/Alphazedehq, skills/spec-authoring/
(see tools/spec/VENDORED.md for the source commit and skill tree id).
Originates from the GridMarket project; provided under the MIT License below.

MIT License

Copyright (c) 2026 William Rumph (GitHub 1wgrumph) and Jordan Hill

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Fire TV starter (tv-app/)

Source: https://github.com/AmazonAppDev/hello-world-fire-tv at commit
50108f4fc4a9dc054be86d851286355df027524a (scanned in P2-X01). tv-app/ keeps the
Compose for TV theme adapted in
tv-app/app/src/main/java/com/afc/companion/ui/theme/Theme.kt; the package is
renamed to com.afc.companion. The starter's launcher icons and adaptive-icon
resources are no longer used (replaced 2026-10-22; see "AZ Fantasy artwork"
below). Provided under the MIT No Attribution license below.

MIT No Attribution

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## AZ Fantasy artwork (tv-app/app/src/main/res/)

The launcher icon (`drawable/ic_launcher_foreground.xml`, `values/ic_launcher_background.xml`,
the five `mipmap-*/ic_launcher.webp` files), the TV banner (`drawable/tv_banner.xml`), the
empty-lineup illustration (`drawable/ic_lineup_empty.xml`) and the sport glyphs
(`drawable/ic_sport_football.xml`, `drawable/ic_sport_basketball.xml`) are original work drawn
for this project on 2026-10-22. They are not third-party material and are covered by the
repository's Apache License 2.0. The banner letters are hand-built polygons
(`evidence/visual/tv-branding/tools/block_letters.py`), not a font, and the legacy webp files
are rendered from the same geometry by `evidence/visual/tv-branding/tools/render_legacy_icons.py`.
No downloaded assets, photos, fonts, league marks or provider marks are used.

## Vega app template (vega-app/)

The app harness files (`index.js`, `metro.config.js`, `app.json`,
`manifest.toml` shape) come from the React Native 0.83 helloWorld template of
the pinned Vega SDK 0.24.12112 (scanned in P2-V01T preparation), renamed to
`com.afc.companion`. The template and the `@amazon-devices/*` packages are
Amazon software used under the Vega SDK license terms that accompany the SDK;
React, React Native and the remaining npm dependencies keep their own
licenses as recorded in `vega-app/package-lock.json` (React Native itself is
MIT, Copyright (c) Meta Platforms, Inc. and affiliates).

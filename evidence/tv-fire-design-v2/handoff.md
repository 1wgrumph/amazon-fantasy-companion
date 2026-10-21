# Bold TV theme and loading red-test handoff

Outcome: PASS (valid red tests), observed 2026-10-21.
Base: f05bf4bf4b6534646d69a4df7b55ae48d8949796; branch: afc/tv-fire-design-v2.
BRAN: unavailable (no native policy); ordinary repository discovery used.

## Verification

Command: `cd tv-app && TMPDIR=~/.cache/afc-gate-tmp ./gradlew :app:testDebugUnitTest`.
Exit 1: 310 tests, 15 failures, zero errors/skips. Every failure is `java.lang.AssertionError`; compilation succeeds. `red.txt` contains the sanitized run and each failing test's classification:

- V2_TOKEN_MISMATCH (4): primary saturation 0.48101267, displayMedium 44/52sp, border width 2dp, card scale 1.02.
- INTENDED_API_MISSING (8): gradient/sport palette and contrast contracts, denseScale, shared loading definition/animation/label.
- LOADING_CALL_SITE_MISSING (3): settings profile, panel profile, panel data.

The initial run had one additional failure from an overbroad font-family assertion on unnamed typography roles. It was removed: the seven requested ramp roles require FontFamily.Default, the whole scale retains its minimum Normal weight guard, and a separate test rejects bundled fonts. No Gradle environment retry was needed.

## Intended API

Existing theme APIs remain AfcTheme, TvFocusStyle, TvColorMath.hsl and TvSafeZone. New palette APIs use Int ARGB values to match existing focus tokens and avoid inline Color method-name mangling in the reflection bridge:

```kotlin
object TvPalette {
    val backgroundGradientArgb: List<Int> // exactly two distinct, opaque stops
    fun sportAccentArgb(sport: Sport): Int
    fun onSportAccentArgb(sport: Sport): Int
}
```

Use the existing `com.afc.companion.profile.Sport.Nfl` and `Sport.Nba` entries. Both accents require saturation >= 0.6 and circular hue distance >= 60 degrees. Primary requires saturation >= 0.6; base and gradient stop luminance must be <= 0.06. Exact hues and hex values remain implementation choices. ThemeContrastTest preserves all existing AA checks and adds text contrast >= 4.5:1 on each sport accent and both gradient stops (inherited text, onBackground, onSurface, onSurfaceVariant, and panel white text).

Retain TvFocusStyle.borderWidthDp >= 4, scale = 1.1, focusedBorderArgb and unfocusedBorderArgb with >= 3:1 contrast after compositing. Add `denseScale: Float = 1f` for dense rows. White focus/fill, neutral colours, corner/elevation and fixed transition-time targets from the earlier staged attempt are no longer asserted by this packet.

The seven type roles require (size/line height sp, weight): displayMedium 32/40 Medium; headlineMedium 28/36 Medium; titleLarge 22/30 Medium; bodyLarge 16/24 Normal; bodyMedium 14/22 Normal; bodySmall 14/20 Normal; labelLarge 14/20 Medium. All seven use FontFamily.Default; no font files are bundled. Letter spacing is left to the platform.

Add this shared definition in `tv-app/app/src/main/java/com/afc/companion/ui/theme/AfcLoadingIndicator.kt`:

```kotlin
@Composable
fun AfcLoadingIndicator(label: String, modifier: Modifier = Modifier)
```

The source contract expects a Box with fillMaxSize and contentAlignment = Alignment.Center, a rememberInfiniteTransition with a delegated animateFloat using infiniteRepeatable, and that animated value consumed by Modifier.rotate or graphicsLayer.rotationZ on a drawn arc. Expose `label` through Text(label) / Text(text = label) or contentDescription = label. This uses already-installed Compose primitives.

Call AfcLoadingIndicator with the existing literal labels at all three loading sites: ProfileSettingsScreen ("Loading profile…"), LineupPanel's !profileLoaded branch ("Loading profile…"), and PanelContent's snapshot == null branch when loading ("Loading panel…"). Keep unavailable/error states distinct from loading. Source-reference tests scope panel calls to those branches and the settings call to its screen function.

## Coverage and boundaries

- The owner's bold colour direction supersedes neutral and v1 cool/desaturated assertions; no restriction to hue 180–300 or saturation <= 0.65 remains.
- The supplied research was read in full. Its type ramp, strong focus and density distinction inform this packet; its colour recommendations are superseded. Research caveats remain: these are AFC targets, not verified system appearance tokens. Research spacing/shape/motion and other consumer restyling remain outside this test-only packet, with the supplied owner acceptance defining its scope.
- The existing 5% safe-zone tests and ProfileDpadFocusTest source are unchanged. Safe-zone JVM tests pass; D-pad instrumentation was not run.
- No product code, build/config files, branding names/assets, device state or unrelated files were changed. Pre-existing Python cache directories remain untouched.
- Source-reference loading checks follow the existing safe-zone test convention because this module has no JVM Compose rule or Robolectric. They establish source contracts, not runtime centring, animation smoothness, accessibility-tree behaviour, or correct font rendering. The implementer/reviewer must verify rendered UI separately.
- No independent review or green implementation is claimed. Changes are staged for the orchestrator; no commit or push.

Hygiene: PASS, exit 0 (118 tests); sanitized output is recorded in hygiene.txt. Its first attempt caught the live evidence writer's blank line at EOF; capture was corrected to buffer the result until completion.

"""Bounded native mutations: restore each accepted repair immediately after its APK is built."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
sdk = Path(os.environ['ANDROID_HOME'])
adb = [str(sdk / 'platform-tools/adb'), '-s', 'emulator-5630']
app = root / 'tv-app/app/src/main/java/com/afc/companion'
mutants = [
    ('short', app / 'access/MenuHoldFilter.kt', 'if (keyCode != KeyEvent.KEYCODE_MENU) return false', 'if (keyCode == KeyEvent.KEYCODE_MENU) return true; return false', 'short down and up delivered'),
    ('overlap', app / 'panel/OverlayModel.kt', 'val top = alert?.let { it.bottom + gap(screenHeight) } ?: safeTop(screenHeight)', 'val top = safeTop(screenHeight)', 'actual card and alert cannot overlap'),
    ('focus', app / 'panel/OverlayService.kt', '::cardParams, null', '::menuParams, null', 'card leaves game focused'),
    ('fallback', app / 'MainActivity.kt', '        overlay.toggle()', '        Unit', 'service-off card and hint'),
    ('contrast', app / 'panel/CornerCardOverlay.kt', 'CornerCardStyle.backgroundAlpha(windowAlpha)', 'CornerCardStyle.BACKGROUND_ALPHA', 'actual compositor contrast'),
]
subprocess.run(adb + ['install', '-r', str(root / 'tv-app/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk')], check=True, stdout=subprocess.PIPE)
selected = set(sys.argv[1:])
if selected:
    mutants = [m for m in mutants if m[0] in selected]
results = json.loads((out / 'repair-mutations.json').read_text()) if (out / 'repair-mutations.json').exists() else []
for name, path, before, after, expected in mutants:
    original = path.read_bytes()
    assert original.decode().count(before) == 1, name
    try:
        path.write_text(original.decode().replace(before, after))
        build = subprocess.run([str(root / 'tv-app/gradlew'), '-p', str(root / 'tv-app'), '-PafcApiBaseUrl=https://review.invalid', ':app:assembleDebug'], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (out / f'mutant-{name}-build.txt').write_bytes(build.stdout)
        assert build.returncode == 0, name
        apk = root / 'tv-app/app/build/outputs/apk/debug/app-debug.apk'
        digest = hashlib.sha256(apk.read_bytes()).hexdigest()
        subprocess.run(adb + ['install', '-r', str(apk)], check=True, stdout=subprocess.PIPE)
    finally:
        path.write_bytes(original)
    run = subprocess.run(['python3', str(out / 'run-native.py'), 'com.afc.companion.panel.CornerCardLifecycleTest'], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out / f'mutant-{name}-native.txt').write_text(run.stdout.rstrip() + '\n')
    killed = run.returncode == 1 and expected in run.stdout
    results = [r for r in results if r["mutant"] != name]
    results.append(dict(mutant=name, apk_sha256=digest, exit=run.returncode, expected_assertion=expected, killed=killed))
    (out / 'repair-mutations.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'{name}: killed={killed}', flush=True)
    assert killed, name

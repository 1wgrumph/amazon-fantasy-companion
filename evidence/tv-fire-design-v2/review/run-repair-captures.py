from pathlib import Path
import os, subprocess, re, time, hashlib, json
root = Path.cwd()
evidence = root / 'evidence/tv-fire-design-v2/review'
out = evidence / 'repair'
out.mkdir(exist_ok=True)
env = os.environ.copy()
env['ANDROID_USER_HOME'] = str(Path.home() / '.local/share/afc-tools/android-user')
adb = str(Path.home() / '.local/share/afc-tools/android-sdk/platform-tools/adb')

def call(*args):
    return subprocess.run([adb, '-s', 'emulator-5584', *args], env=env, capture_output=True, check=True).stdout

# The synthetic shell must use the production navigation inset for the pixel regression.
pattern = r'Column\((Modifier\.padding\([^\n]+\)), verticalArrangement = Arrangement\.spacedBy\(16.dp\)\)'
main = (root / 'tv-app/app/src/main/java/com/afc/companion/MainActivity.kt').read_text()
fixture = (evidence / 'capture/IndependentV2Capture.kt').read_text()
assert re.search(pattern, main).group(1) == re.search(pattern, fixture).group(1)
for _ in range(60):
    if call('shell', 'getprop', 'sys.boot_completed').strip() == b'1':
        break
    time.sleep(1)
else:
    raise RuntimeError('Emulator boot did not complete')
for apk in ['debug/app-debug.apk', 'androidTest/debug/app-debug-androidTest.apk']:
    assert b'Success' in call('install', '-r', str(root / 'tv-app/app/build/outputs/apk' / apk))
result = call('shell', 'am', 'instrument', '-w', '-r', '-e', 'class',
              'com.afc.companion.visual.IndependentV2Capture,com.afc.companion.profile.ProfileDpadFocusTest',
              'com.afc.companion.test/androidx.test.runner.AndroidJUnitRunner').decode()
(out / 'instrumentation.txt').write_text(result.rstrip() + '\n')
names = ['link', 'profile-button', 'profile-field', 'profile-sports', 'profile-nfl-focused',
         'profile-nfl-toggled', 'loading', 'loading-next-frame', 'lineup-nfl', 'lineup-nba',
         'alert', 'panel-profile-loading', 'panel-data-loading', 'panel-empty', 'panel-error',
         'profile-error', 'panel-data-loading-alert', 'profile-nav-focus',
         'panel-loading-dismiss-focus', 'panel-loading-dismissed']
for name in names:
    data = call('exec-out', 'run-as', 'com.afc.companion', 'cat', 'cache/review-v2-' + name + '.png')
    assert data.startswith(b'\x89PNG'), name
    (out / ('emulator-' + name + '.png')).write_bytes(data)
(out / 'SHA256SUMS').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest() + '  ' + f.name + '\n'
                                      for f in sorted(out.glob('*.png'))))
uids = re.findall(r'^package:com\.afc\.companion(?:\.test)? uid:(\d+)$',
                  call('shell', 'pm', 'list', 'packages', '-U', 'com.afc.companion').decode(), re.M)
logs = call('logcat', '-d', '--uid=' + ','.join(uids), '*:W').decode(errors='replace')
logs = re.sub(r'/home/[^/\s]+(?:/[^\s\n]*)?', '<local-path>', logs)
logs = re.sub(r'\b(?:192\.168\.\d+\.\d+|10\.(?:\d{1,3}\.){2}\d{1,3})(?::\d+)?', '<device>', logs)
(out / 'app-logcat.txt').write_text(logs.rstrip() + '\n')
assert 'OK (19 tests)' in result, 'See instrumentation.txt for actual failures'
print('OK (19 tests); 20 captures; navigation fixture matches production inset')

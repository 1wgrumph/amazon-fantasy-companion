"""Exercise the candidate's source-contract tests against valid but wrongly wired source copies.
Only review evidence is written; product sources are never modified.
"""
from pathlib import Path
import os
import shutil
import subprocess

repo = Path(__file__).resolve().parents[3]
out = repo / 'evidence/tv-corner-card/review'
mirror = out / 'mutation-root'
paths = ['AndroidManifest.xml', 'res/xml/menu_hold_service.xml', 'res/values/strings.xml']
paths += ['java/com/afc/companion/' + p for p in ['MainActivity.kt', 'panel/OverlayService.kt', 'panel/CornerCardOverlay.kt', 'panel/LineupPanel.kt', 'access/MenuHoldService.kt']]
for path in paths:
    dest = mirror / 'tv-app/app/src/main' / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(repo / 'tv-app/app/src/main' / path, dest)
service = mirror / 'tv-app/app/src/main/java/com/afc/companion/panel/OverlayService.kt'
source = service.read_text()
old = 'mode == OverlayMode.Card || mode == OverlayMode.Menu, ::cardParams, null'
assert source.count(old) == 1
service.write_text(source.replace(old, 'mode == OverlayMode.Card || mode == OverlayMode.Menu, ::menuParams, null'))
main = mirror / 'tv-app/app/src/main/java/com/afc/companion/MainActivity.kt'
source = main.read_text()
assert source.count('        overlay.toggle()') == 1
main.write_text(source.replace('        overlay.toggle()', '        if (false) { overlay.toggle() }'))
init = out / 'mutation.init.gradle'
init.write_text('allprojects { afterEvaluate { tasks.withType(Test).configureEach { systemProperty "afc.repoRoot", rootProject.file("../evidence/tv-corner-card/review/mutation-root").absolutePath } } }\n')
cmd = [str(repo / 'tv-app/gradlew'), '-p', str(repo/'tv-app'), '-I', str(init), '-PafcApiBaseUrl=https://review.invalid', ':app:testDebugUnitTest', '--tests', 'com.afc.companion.panel.CornerCardIntegrationContractTest', '--tests', 'com.afc.companion.panel.OverlayIntegrationContractTest']
with (out/'mutation-tests.txt').open('w') as log:
    log.write('Source-only mutations: card render uses focusable menu params; in-app toggle hidden behind if(false).\n'); log.flush()
    r = subprocess.run(cmd, cwd=repo, env=os.environ, stdout=log, stderr=subprocess.STDOUT)
    log.write(f'\nEXIT: {r.returncode}\n')
print(f'Source-contract mutation probe exit {r.returncode}; see mutation-tests.txt')

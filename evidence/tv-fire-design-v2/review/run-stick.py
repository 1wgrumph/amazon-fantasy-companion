import os, pathlib, subprocess, json, datetime, re, hashlib
root=pathlib.Path.cwd()
out=root/'evidence/tv-fire-design-v2/review'
coord=root.parent/'amazon-fantasy-companion-m03-m05-recovery/docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/recovery-m03-m05/coordinator-parallel-20261020'
lease=coord/'stick-lease.json'
restore=pathlib.Path.home()/'.local/share/afc-tools/private-evidence/nba-watcher-20261021/afc-f05bf4b.apk'
expected='0a9bc06b019252278719c2a3bae557ae2d00d6b04f487eae81c692cf53342d78'
assert hashlib.sha256(restore.read_bytes()).hexdigest()==expected, 'Restore APK host hash mismatch'
assert (coord/'stick-lease-nba-watcher-released.json').exists(), 'No release receipt'
now=datetime.datetime.now(datetime.timezone.utc)
assert now.hour<22 or now.hour==22 and now.minute<40, 'Too late for safe restoration'
try:
 fd=os.open(lease,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
except FileExistsError:
 print('ENVIRONMENT_GAP: stick lease held by another session; no device calls made')
 raise SystemExit(2)
with os.fdopen(fd,'w') as f: json.dump({'holder':'v2-review','acquired_utc':now.isoformat(),'expires_at':'2026-10-21T22:50:00Z'},f)
env=os.environ.copy(); env['ANDROID_USER_HOME']=str(pathlib.Path.home()/'.local/share/afc-tools/android-user')
settings=(pathlib.Path.home()/'alphazede/Hackathons/AGENTS.md').read_text()
address=re.search(r'adb connect ([0-9.]+:[0-9]+)',settings).group(1)
adb=str(pathlib.Path.home()/'.local/share/afc-tools/android-sdk/platform-tools/adb')
log=[]
def call(*args,timeout=60,check=True):
 p=subprocess.run(['flock','/tmp/afc-m03-m05-fire-tv.lock',adb,'-s',address,*args],env=env,capture_output=True,timeout=timeout)
 if check and p.returncode: raise RuntimeError('ADB '+args[0]+' exit '+str(p.returncode)+': '+(p.stdout+p.stderr).decode(errors='replace').replace(address,'<device>'))
 return p.stdout
try:
 call('get-state')
 log.append('Exclusive v2-review lease acquired; every ADB call serialized through flock.')
 for apk in ('debug/app-debug.apk','androidTest/debug/app-debug-androidTest.apk'):
  result=call('install','-r',str(root/'tv-app/app/build/outputs/apk'/apk)).decode()
  assert 'Success' in result,result
 log.append('Candidate and independent capture APK installed with -r; no uninstall or data clear.')
 # Synthetic in-process peers only; the fixtures never save or launch a provider.
 result=call('shell','am','instrument','-w','-r','-e','class','com.afc.companion.visual.IndependentV2Capture,com.afc.companion.profile.ProfileDpadFocusTest','com.afc.companion.test/androidx.test.runner.AndroidJUnitRunner',timeout=300).decode(errors='replace')
 result=result.replace(address,'<device>')
 (out/'stick-instrumentation.txt').write_text(result.rstrip()+'\n')
 captures=['link','profile-button','profile-field','profile-sports','profile-nfl-focused','profile-nfl-toggled','loading','loading-next-frame','lineup-nfl','lineup-nba','alert','panel-profile-loading','panel-data-loading','panel-empty','panel-error','profile-error']
 for name in captures:
  data=call('exec-out','run-as','com.afc.companion','cat','cache/review-v2-'+name+'.png',check=False)
  if data.startswith(b'\x89PNG'):
   (out/('stick-'+name+'.png')).write_bytes(data)
 log.append('Instrumentation: '+('OK' if 'OK (14 tests)' in result else 'SEE INSTRUMENTATION RESULT'))
 pid=call('shell','pidof','com.afc.companion',check=False).decode().strip()
 if pid:
  errors=call('logcat','-d','--pid='+pid,'-s','AndroidRuntime:E','System.err:W','AFC:E',check=False).decode(errors='replace')
  (out/'stick-app-errors.txt').write_text(errors.replace(address,'<device>').rstrip()+'\n')
finally:
 result=call('install','-r',str(restore)).decode()
 assert 'Success' in result,result
 apk_path=call('shell','pm','path','com.afc.companion').decode().strip().removeprefix('package:')
 digest=hashlib.sha256(call('exec-out','cat',apk_path)).hexdigest()
 assert digest==expected, 'Restored on-device APK hash mismatch: '+digest
 log.append('Watcher APK restored with install -r; on-device APK SHA256 '+digest+' matches required pin.')
 call('shell','input','keyevent','KEYCODE_HOME')
 lease.unlink()
 log.append('Home key sent; lease released after restoration and hash verification.')
 (out/'stick-run.txt').write_text('\n'.join(log)+'\n')
 print('\n'.join(log))

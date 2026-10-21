from pathlib import Path
import os,subprocess,hashlib,json
root=Path.cwd();out=root/'evidence/tv-fire-design-v2/review'
env=os.environ.copy();env['ANDROID_USER_HOME']=str(Path.home()/'.local/share/afc-tools/android-user')
adb=str(Path.home()/'.local/share/afc-tools/android-sdk/platform-tools/adb')
def call(*args): return subprocess.run([adb,'-s','emulator-5584',*args],env=env,capture_output=True,check=True).stdout
assert b'Success' in call('install','-r',str(root/'tv-app/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk'))
original=call('shell','settings','get','global','animator_duration_scale').decode().strip()
summary={}
try:
 for scale in ['1','0']:
  call('shell','settings','put','global','animator_duration_scale',scale)
  run=call('shell','am','instrument','-w','-r','-e','class','com.afc.companion.visual.LiveLoadingCapture','com.afc.companion.test/androidx.test.runner.AndroidJUnitRunner').decode()
  (out/('emulator-motion-scale-'+scale+'.txt')).write_text(run.rstrip()+'\n')
  hashes=[]
  for i in range(1,4):
   data=call('exec-out','run-as','com.afc.companion','cat','cache/review-v2-live-'+str(i)+'.png')
   assert data.startswith(b'\x89PNG')
   (out/('emulator-motion-scale-'+scale+'-'+str(i)+'.png')).write_bytes(data)
   hashes.append(hashlib.sha256(data).hexdigest())
  summary[scale]={'instrumentation_pass':'OK (1 test)' in run,'frame_hashes':hashes,'distinct_frames':len(set(hashes))}
finally:
 call('shell','settings','put','global','animator_duration_scale',original)
 (out/'emulator-motion-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))

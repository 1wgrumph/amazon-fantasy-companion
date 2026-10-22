"""Run a selected device test, mapping Android's textual failure result to a process exit code."""
import os
from pathlib import Path
import subprocess
import sys

sdk = Path(os.environ["ANDROID_HOME"])
result = subprocess.run([str(sdk / "platform-tools/adb"), "-s", "emulator-5630", "shell", "am", "instrument", "-w", "-r", "-e", "class", sys.argv[1], "com.afc.companion.test/androidx.test.runner.AndroidJUnitRunner"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=300)
print(result.stdout.rstrip())
sys.exit(0 if result.returncode == 0 and "OK (" in result.stdout and "FAILURES!!!" not in result.stdout else 1)

import sys
from pathlib import Path
from PIL import Image
capture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / 'emulator-profile-nav-focus.png'
image = Image.open(capture).convert('RGB')
points = [(x, y) for y in range(150, 280) for x in range(390)
          if image.getpixel((x, y)) == (255, 210, 63)]
left = min(x for x, _ in points)
safe_left = image.width * 0.05
print(f'Focused navigation solid gold left edge: {left}px; required safe-zone boundary: {safe_left}px')
assert left >= safe_left, 'V2-R03: focused navigation exceeds the five-percent safe zone'

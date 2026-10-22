"""Check effective card opacity from the captured synthetic bright-game composition."""
import json
from pathlib import Path
from PIL import Image

with Image.open(Path(__file__).parent / 'corner-repair/repair-04-card-bright.png') as frame:
    background = frame.convert('RGB').getpixel((1805, 100))
video = (240, 246, 251)  # CornerGameActivity's bright fixture
surface = (27, 30, 75)  # reviewed theme surface
opacity = [(v - b) / (v - s) for v, b, s in zip(video, background, surface)]
assert all(0.60 <= alpha <= 0.75 for alpha in opacity), (background, opacity)
print(json.dumps({'background_rgb': background, 'video_rgb': video, 'surface_rgb': surface, 'effective_opacity_per_channel': opacity}, indent=2))

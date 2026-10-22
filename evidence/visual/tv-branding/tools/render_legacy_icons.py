#!/usr/bin/env python3
"""Render the five legacy mipmap ic_launcher.webp files from the launcher glyph geometry.

The shapes repeat res/drawable/ic_launcher_foreground.xml (108-unit viewport) on the
ic_launcher_background colour. The legacy icon shows the central 72 units, the area
the adaptive mask keeps. Usage: render_legacy_icons.py <tv-app/app/src/main/res>
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

SIZES = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
SS = 8  # supersampling factor


def render(px):
    big = px * SS
    scale = big / 72  # pixels per viewport unit; viewport 18..90 maps to the canvas

    def p(x, y):
        return ((x - 18) * scale, (y - 18) * scale)

    def box(x0, y0, x1, y1):
        return [*p(x0, y0), *p(x1, y1)]

    image = Image.new('RGBA', (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    margin = big * 0.04
    draw.rounded_rectangle([margin, margin, big - margin, big - margin], radius=big * 0.18, fill='#1B1E4B')
    # Screen outline: stroke 5 centred on the 28..80 x 38..70 rectangle, corner radius 4.
    draw.rounded_rectangle(box(25.5, 35.5, 82.5, 72.5), radius=6.5 * scale, fill='#F4F2FF')
    draw.rounded_rectangle(box(30.5, 40.5, 77.5, 67.5), radius=1.5 * scale, fill='#1B1E4B')
    draw.rounded_rectangle(box(44, 76, 64, 79), radius=1.5 * scale, fill='#F4F2FF')
    draw.rounded_rectangle(box(62, 42, 76, 66), radius=3 * scale, fill='#FFD23F')
    for y in (47, 53, 59):
        draw.rectangle(box(65, y, 73, y + 3), fill='#2A0E3F')
    draw.ellipse(box(31, 41, 41, 51), fill='#FF6FB5')
    return image.resize((px, px), Image.LANCZOS)


if __name__ == '__main__':
    res = Path(sys.argv[1])
    for density, px in SIZES.items():
        render(px).save(res / f'mipmap-{density}' / 'ic_launcher.webp', 'WEBP', lossless=True)
        print(density, px)

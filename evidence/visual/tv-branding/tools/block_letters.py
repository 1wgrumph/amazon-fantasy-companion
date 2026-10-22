#!/usr/bin/env python3
"""Original AZ Fantasy block letterforms as vector path data (no font files).

Each glyph is one or more polygons on a grid 10 units tall with 2-unit strokes;
A's counter is a second polygon drawn with evenOdd fill. Usage:
block_letters.py TEXT X Y HEIGHT -> pathData with its top-left at (X, Y).
"""
import sys

GLYPHS = {
    'A': (6, [[(0, 10), (0, 2), (2, 0), (4, 0), (6, 2), (6, 10), (4, 10), (4, 6), (2, 6), (2, 10)],
              [(2, 2.6), (4, 2.6), (4, 4), (2, 4)]]),
    'Z': (6, [[(0, 0), (6, 0), (6, 2), (2.6, 8), (6, 8), (6, 10), (0, 10), (0, 8), (3.4, 2), (0, 2)]]),
    'F': (5, [[(0, 0), (5, 0), (5, 2), (2, 2), (2, 4), (4.4, 4), (4.4, 6), (2, 6), (2, 10), (0, 10)]]),
    'N': (6.4, [[(0, 10), (0, 0), (2, 0), (4.4, 5.6), (4.4, 0), (6.4, 0), (6.4, 10), (4.4, 10), (2, 4.4), (2, 10)]]),
    'T': (6, [[(0, 0), (6, 0), (6, 2), (4, 2), (4, 10), (2, 10), (2, 2), (0, 2)]]),
    'S': (6, [[(0.8, 0), (6, 0), (6, 2), (2, 2), (2, 4), (5.2, 4), (6, 4.8), (6, 9.2), (5.2, 10), (0, 10),
               (0, 8), (4, 8), (4, 6), (0.8, 6), (0, 5.2), (0, 0.8)]]),
    'Y': (6, [[(0, 0), (2, 0), (2, 3.6), (4, 3.6), (4, 0), (6, 0), (6, 5.2), (5.2, 6), (4, 6), (4, 10),
               (2, 10), (2, 6), (0.8, 6), (0, 5.2)]]),
}
GAP = 1.4


def num(value):
    return f'{value:.2f}'.rstrip('0').rstrip('.')


def word(text, x, y, height):
    unit, out = height / 10, []
    for ch in text:
        advance, polygons = GLYPHS[ch]
        for points in polygons:
            out.append('M' + ' L'.join(f'{num(x + px * unit)},{num(y + py * unit)}' for px, py in points) + 'Z')
        x += (advance + GAP) * unit
    return ' '.join(out)


def width(text, height):
    return sum(GLYPHS[c][0] + GAP for c in text) * height / 10 - GAP * height / 10


if __name__ == '__main__':
    text, x, y, h = sys.argv[1], *map(float, sys.argv[2:5])
    print(word(text, x, y, h))
    print('width', num(width(text, h)), file=sys.stderr)

#!/usr/bin/env python3
"""Build the demo cuts with ffmpeg.

cuts.json is the shot list, the captions, the title cards and the
composition of each output. Media work is ffmpeg only. Two builds of the
same raw clips use the same arguments, one thread and bitexact muxing so
the output bytes match.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

WIDTH = 1920
HEIGHT = 1080
FPS = 30
PLAN_S = (12, 22, 28, 30, 32, 18, 14)
MARKER_NAME = 'SYNTHETIC'
MARKER_TEXT = 'synthetic'
CORNER_LABEL = 'SYNTHETIC — pipeline test'
SEARCH_CARD = (
    'Prime Video opens its search screen (searchOpened). '
    'Provider video is not shown, to respect copyright.'
)
FONT = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
FONT_BOLD = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
LINE_LIMIT = 72
SEGMENT_KEYS = {'shot', 'in_s', 'out_s', 'card', 'card_duration_s'}
SHOT_KEYS = {
    'id', 'file', 'planned_duration_s', 'in_s', 'out_s', 'align',
    'caption', 'labels', 'title_card', 'synthetic_color',
}
CARD_KEYS = {'id', 'duration_s', 'color', 'lines', 'note'}
OUTPUT_KEYS = {'id', 'group', 'file', 'segments'}
TOP_KEYS = {'shot_list', 'resolution', 'frame_rate', 'audio', 'shots', 'cards', 'outputs'}

ENCODE = [
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
    '-pix_fmt', 'yuv420p', '-r', '30', '-g', '30', '-bf', '0',
    '-threads', '1', '-filter_threads', '1', '-filter_complex_threads', '1',
    '-x264-params',
    'threads=1:sliced-threads=0:sync-lookahead=0:bframes=0:keyint=30:min-keyint=30:scenecut=0',
    '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-ac', '2',
    '-flags', '+bitexact', '-map_metadata', '-1',
    '-movflags', '+faststart', '-video_track_timescale', '30000',
    '-shortest',
]


class CutError(Exception):
    """A refused cut: bad composition, missing media, or ffmpeg failure."""


def load_cuts(path):
    """Read and validate cuts.json. Raises CutError. Does not touch media."""
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CutError(f'cuts.json: {exc.__class__.__name__}') from exc
    if not isinstance(data, dict) or set(data) != TOP_KEYS:
        raise CutError('cuts.json: unexpected top-level fields')
    if data['shot_list'] != 'docs/submission/demo-plan.md':
        raise CutError('cuts.json: shot_list is not the demo plan')
    resolution = data['resolution']
    if resolution != {'width': WIDTH, 'height': HEIGHT}:
        raise CutError('cuts.json: resolution must be 1920x1080')
    if data['frame_rate'] != FPS or data['audio'] != 'silent':
        raise CutError('cuts.json: frame rate must be 30 and audio must be silent')
    shots = data['shots']
    cards = data['cards']
    outputs = data['outputs']
    if not isinstance(shots, list) or not isinstance(cards, list) or not isinstance(outputs, list):
        raise CutError('cuts.json: shots, cards and outputs must be lists')
    if [need_id(shot, 'shot') for shot in shots] != [f'S{n}' for n in range(1, 8)]:
        raise CutError('cuts.json: shots must be S1 through S7 in order')
    card_ids = []
    for card in cards:
        _require(card, CARD_KEYS - {'note'}, CARD_KEYS, 'card')
        card_ids.append(need_id(card, 'card'))
        _need_int(card['duration_s'], f'{card["id"]} duration', 1, 60)
        _need_color(card['color'], card['id'])
        _need_lines(card['lines'], card['id'], 1, 3)
        if 'note' in card and (not isinstance(card['note'], str) or not card['note'].strip()):
            raise CutError(f'{card["id"]}: note must be text')
    if len(card_ids) != len(set(card_ids)):
        raise CutError('cuts.json: duplicate card id')
    by_card = {card['id']: card for card in cards}
    if 'searchOpened' not in by_card or 'linking' not in by_card:
        raise CutError('cuts.json: searchOpened and linking cards are required')
    if ' '.join(by_card['searchOpened']['lines']) != SEARCH_CARD:
        raise CutError('cuts.json: searchOpened card text does not match the decision')
    for index, shot in enumerate(shots):
        _require(shot, SHOT_KEYS, SHOT_KEYS, 'shot')
        if shot['file'] != f'{shot["id"]}.mp4':
            raise CutError(f'{shot["id"]}: file must be {shot["id"]}.mp4')
        planned = _need_int(shot['planned_duration_s'], f'{shot["id"]} planned', 1, 180)
        if planned != PLAN_S[index]:
            raise CutError(f'{shot["id"]}: planned duration is not the demo plan')
        start = _need_int(shot['in_s'], f'{shot["id"]} in', 0, planned)
        end = _need_int(shot['out_s'], f'{shot["id"]} out', 1, planned)
        if not start < end <= planned:
            raise CutError(f'{shot["id"]}: in/out must sit inside the planned duration')
        if shot['align'] not in ('start', 'end'):
            raise CutError(f'{shot["id"]}: align must be start or end')
        _need_lines(shot['caption'], shot['id'], 1, 3)
        if not isinstance(shot['labels'], list) or any(not isinstance(item, str) for item in shot['labels']):
            raise CutError(f'{shot["id"]}: labels must be a list of strings')
        _need_color(shot['synthetic_color'], shot['id'])
        card_id = shot['title_card']
        if card_id is None:
            if end - start != planned or shot['align'] != 'start':
                raise CutError(f'{shot["id"]}: a shot without a card uses its full planned duration')
        else:
            if card_id not in by_card:
                raise CutError(f'{shot["id"]}: unknown title card')
            if (end - start) + by_card[card_id]['duration_s'] != planned:
                raise CutError(f'{shot["id"]}: capture window plus title card must equal the planned duration')
    if [shot['id'] for shot in shots if 'REPLAY' in shot['labels']] != ['S3']:
        raise CutError('cuts.json: S3 is the only replay-labelled shot')
    _check_outputs(outputs, {shot['id']: shot for shot in shots}, by_card)
    return data


def segment_duration(shot_by_id, card_by_id, segment):
    """Seconds of one segment: the shot window plus any title card."""
    total = 0
    if 'shot' in segment:
        shot = shot_by_id[segment['shot']]
        start = segment['in_s'] if 'in_s' in segment else shot['in_s']
        end = segment['out_s'] if 'out_s' in segment else shot['out_s']
        total += end - start
    if 'card' in segment:
        card = card_by_id[segment['card']]
        total += segment['card_duration_s'] if 'card_duration_s' in segment else card['duration_s']
    return total


def output_duration(cuts, output):
    shots = {shot['id']: shot for shot in cuts['shots']}
    cards = {card['id']: card for card in cuts['cards']}
    return sum(segment_duration(shots, cards, segment) for segment in output['segments'])


def _require(value, required, allowed, label):
    if not isinstance(value, dict) or set(value) - allowed or required - set(value):
        raise CutError(f'cuts.json: unexpected or missing {label} fields')


def _check_outputs(outputs, shots, cards):
    groups = {'main': [], 'teaser': [], 'feature': [], 'raw': []}
    names = []
    for output in outputs:
        _require(output, OUTPUT_KEYS, OUTPUT_KEYS, 'output')
        if output['group'] not in groups:
            raise CutError(f'{output.get("id")}: unknown output group')
        _need_mp4(output['file'], output['id'])
        names.append(output['file'])
        if not isinstance(output['segments'], list) or not output['segments']:
            raise CutError(f'{output["id"]}: needs at least one segment')
        for segment in output['segments']:
            _check_segment(output, segment, shots, cards)
        groups[output['group']].append(output)
    if len(names) != len(set(names)):
        raise CutError('cuts.json: duplicate output file name')
    if [item['id'] for item in groups['main']] != ['main']:
        raise CutError('cuts.json: one main output is required')
    if [item['id'] for item in groups['teaser']] != ['teaser']:
        raise CutError('cuts.json: one teaser output is required')
    if [item['id'] for item in groups['feature']] != ['alerts', 'watch', 'panel', 'linking']:
        raise CutError('cuts.json: feature clips must be alerts, watch, panel, linking')
    if [item['id'] for item in groups['raw']] != [f'raw-S{n}' for n in range(1, 8)]:
        raise CutError('cuts.json: trimmed raw clips must be raw-S1 through raw-S7')
    if output_duration({'shots': list(shots.values()), 'cards': list(cards.values())}, groups['main'][0]) != 156:
        raise CutError('cuts.json: main demo must total 156s')
    teaser_s = output_duration(
        {'shots': list(shots.values()), 'cards': list(cards.values())}, groups['teaser'][0])
    if not 25 <= teaser_s <= 35:
        raise CutError('cuts.json: teaser must be 25 to 35s')
    for output in groups['raw']:
        for segment in output['segments']:
            if 'card' in segment:
                raise CutError(f'{output["id"]}: a raw clip has no title card')


def _check_segment(output, segment, shots, cards):
    if not isinstance(segment, dict) or set(segment) - SEGMENT_KEYS or not ({'shot', 'card'} & set(segment)):
        raise CutError(f'{output["id"]}: bad segment')
    if ('in_s' in segment) != ('out_s' in segment):
        raise CutError(f'{output["id"]}: in_s and out_s are set together')
    if 'card_duration_s' in segment and 'card' not in segment:
        raise CutError(f'{output["id"]}: card duration without a card')
    if 'shot' in segment:
        shot = shots.get(segment['shot'])
        if shot is None:
            raise CutError(f'{output["id"]}: unknown shot')
        start = segment['in_s'] if 'in_s' in segment else shot['in_s']
        end = segment['out_s'] if 'out_s' in segment else shot['out_s']
        _need_int(start, f'{output["id"]} in', 0, shot['planned_duration_s'])
        _need_int(end, f'{output["id"]} out', 1, shot['planned_duration_s'])
        if start >= end:
            raise CutError(f'{output["id"]}: empty shot window')
    if 'card' in segment:
        if segment['card'] not in cards:
            raise CutError(f'{output["id"]}: unknown card')
        if 'card_duration_s' in segment:
            _need_int(segment['card_duration_s'], f'{output["id"]} card', 1, 60)


def need_id(value, label):
    ident = value.get('id') if isinstance(value, dict) else None
    if not isinstance(ident, str) or not ident.replace('-', '').isalnum():
        raise CutError(f'cuts.json: bad {label} id')
    return ident


def _need_int(value, label, low, high):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise CutError(f'{label} must be an integer from {low} to {high}')
    return value


def _need_color(value, label):
    if not isinstance(value, str) or len(value) != 8 or not value.startswith('0x'):
        raise CutError(f'{label}: color must be 0xRRGGBB')
    try:
        int(value[2:], 16)
    except ValueError as exc:
        raise CutError(f'{label}: color must be 0xRRGGBB') from exc


def _need_lines(value, label, low, high):
    if not isinstance(value, list) or not low <= len(value) <= high:
        raise CutError(f'{label}: needs {low} to {high} text lines')
    for line in value:
        if not isinstance(line, str) or line != line.strip() or not line or '\n' in line:
            raise CutError(f'{label}: each line is one trimmed row')
        if len(line) > LINE_LIMIT:
            raise CutError(f'{label}: a line is longer than {LINE_LIMIT} characters')


def _need_mp4(name, label):
    if not isinstance(name, str) or '/' in name or '\\' in name or name.startswith('.'):
        raise CutError(f'{label}: file name must stay inside the output directory')
    if not name.endswith('.mp4') or name.count('.') != 1:
        raise CutError(f'{label}: output must be one .mp4 name')


def _env():
    env = os.environ.copy()
    env['SOURCE_DATE_EPOCH'] = '0'
    env['TZ'] = 'UTC'
    env['LC_ALL'] = 'C'
    env['LANG'] = 'C'
    return env


def _run(cmd, key, cwd):
    proc = subprocess.run(
        cmd, cwd=cwd, env=_env(), stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False,
    )
    if proc.returncode != 0:
        tail = proc.stderr.decode('utf-8', 'replace').strip().splitlines()[-20:]
        raise CutError(f'ffmpeg failed for {key}\n' + '\n'.join(tail))


def _probe(path):
    proc = subprocess.run(
        [
            'ffprobe', '-v', 'error', '-of', 'json',
            '-show_entries', 'format=duration:stream=codec_type,width,height,duration',
            str(path),
        ],
        env=_env(), stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if proc.returncode != 0:
        raise CutError(f'unreadable media: {Path(path).name}')
    try:
        payload = json.loads(proc.stdout.decode('utf-8'))
    except json.JSONDecodeError as exc:
        raise CutError(f'unreadable media: {Path(path).name}') from exc
    video = next((s for s in payload.get('streams', []) if s.get('codec_type') == 'video'), None)
    if video is None or 'width' not in video or 'height' not in video:
        raise CutError(f'{Path(path).name} has no video stream')
    raw = video.get('duration') or payload.get('format', {}).get('duration')
    try:
        duration = float(raw)
    except (TypeError, ValueError) as exc:
        raise CutError(f'{Path(path).name} has no duration') from exc
    audio = any(s.get('codec_type') == 'audio' for s in payload.get('streams', []))
    return {'width': video['width'], 'height': video['height'], 'duration': duration, 'audio': audio}


def _num(value):
    return f'{value:.3f}'.rstrip('0').rstrip('.') or '0'


def _drawtext(font, textfile, size, color, x, y, boxed):
    parts = [
        f'fontfile={font}', f'textfile={textfile}', f'fontsize={size}',
        f'fontcolor={color}', f'x={x}', f'y={y}',
    ]
    if boxed:
        parts.extend(['box=1', 'boxcolor=black@0.65', 'boxborderw=16'])
    return 'drawtext=' + ':'.join(parts)


def _write_text(work, name, text):
    (work / name).write_bytes(text.encode('utf-8'))
    return name


def _overlay_filters(work, key, lines, top, corner, font, size, centered):
    filters = []
    if lines and not centered:
        box_h = 36 + len(lines) * 52
        filters.append(f'drawbox=x=0:y=ih-{box_h}:w=iw:h={box_h}:color=black@0.55:t=fill')
        for index, line in enumerate(lines):
            name = _write_text(work, f'{key}-cap-{index}.txt', line)
            # drawtext knows h/w, not ih/iw. Parentheses keep the minus in the expression.
            filters.append(_drawtext(
                FONT, name, 40, 'white', '64', f'(h-{box_h - 18 - index * 52})', False))
    if centered and lines:
        block = len(lines) * 64
        for index, line in enumerate(lines):
            name = _write_text(work, f'{key}-card-{index}.txt', line)
            filters.append(_drawtext(
                font, name, size, 'white', '(w-text_w)/2', f'(h-{block})/2+{index * 64}', False))
    for index, line in enumerate(top):
        name = _write_text(work, f'{key}-top-{index}.txt', line)
        filters.append(_drawtext(FONT_BOLD, name, 36, 'white', '48', str(36 + index * 56), True))
    if corner:
        name = _write_text(work, f'{key}-corner.txt', corner)
        filters.append(_drawtext(FONT_BOLD, name, 32, 'yellow', 'w-text_w-48', '36', True))
    return filters


def _encode_base(graph, video_input, frames, dest, key, cwd):
    cmd = [
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
        '-fflags', '+bitexact',
        *video_input,
        '-f', 'lavfi', '-t', str(frames // FPS), '-i', 'anullsrc=r=48000:cl=stereo',
        '-filter_complex', graph,
        '-map', '[v]', '-map', '1:a',
        '-frames:v', str(frames),
        *ENCODE,
        str(dest),
    ]
    _run(cmd, key, cwd)


def _window(shot, segment, file_duration):
    start = segment['in_s'] if 'in_s' in segment else shot['in_s']
    end = segment['out_s'] if 'out_s' in segment else shot['out_s']
    length = end - start
    # End alignment keeps the hand-off, which is the end of the recording.
    if shot['align'] == 'end':
        if file_duration + 0.001 < length:
            raise CutError(f'{shot["file"]} is {file_duration:.3f}s, shorter than the {length}s cut')
        return file_duration - length, length
    if file_duration + 0.001 < end:
        raise CutError(f'{shot["file"]} is {file_duration:.3f}s, shorter than the {end}s cut')
    return float(start), float(length)


def _render_shot(work, key, src, shot, segment, mode, synthetic, info):
    start, length = _window(shot, segment, info['duration'])
    frames = int(length) * FPS
    top = [shot['id']] if mode == 'raw' else []
    top.extend(shot['labels'])
    corner = CORNER_LABEL if synthetic else ''
    filters = [
        f'trim=start={_num(start)}:end={_num(start + length)}',
        'setpts=PTS-STARTPTS', f'fps={FPS}', 'format=yuv420p',
        *_overlay_filters(work, key, shot['caption'], top, corner, FONT, 40, False),
    ]
    dest = work / f'{key}.mp4'
    _encode_base('[0:v]' + ','.join(filters) + '[v]', ['-i', str(src)], frames, dest, key, work)
    _expect(dest, length, key)
    return dest


def _render_card(work, key, card, duration, synthetic):
    frames = duration * FPS
    corner = CORNER_LABEL if synthetic else ''
    filters = ['format=yuv420p', *_overlay_filters(
        work, key, card['lines'], [], corner, FONT_BOLD, 46, True)]
    dest = work / f'{key}.mp4'
    color = f'color=c={card["color"]}:s={WIDTH}x{HEIGHT}:r={FPS}:d={duration}'
    _encode_base(
        '[0:v]' + ','.join(filters) + '[v]',
        ['-f', 'lavfi', '-i', color], frames, dest, key, work,
    )
    _expect(dest, duration, key)
    return dest


def _expect(path, seconds, key):
    info = _probe(path)
    if (info['width'], info['height']) != (WIDTH, HEIGHT) or not info['audio']:
        raise CutError(f'{key} is not {WIDTH}x{HEIGHT} with an audio track')
    if abs(info['duration'] - seconds) > 0.05:
        raise CutError(f'{key} is {info["duration"]:.3f}s, expected {seconds}s')


def _concat(work, parts, dest, key, seconds):
    lines = ['ffconcat version 1.0']
    lines.extend(f"file '{part.name}'" for part in parts)
    list_path = work / f'{key}.ffconcat'
    list_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    staged = work / f'{key}-out.mp4'
    _run(
        [
            'ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y',
            '-fflags', '+bitexact', '-f', 'concat', '-safe', '0', '-i', list_path.name,
            '-c', 'copy', '-flags', '+bitexact', '-map_metadata', '-1',
            '-movflags', '+faststart', '-video_track_timescale', '30000',
            str(staged),
        ],
        key, work,
    )
    _expect(staged, seconds, key)
    os.replace(staged, dest)


def _synthetic_enabled(raw_dir):
    marker = raw_dir / MARKER_NAME
    if not marker.is_file():
        return False
    return marker.read_text(encoding='utf-8').strip() == MARKER_TEXT


def _require_raw(cuts, raw_dir):
    shots = {shot['id']: shot for shot in cuts['shots']}
    missing = [shot['file'] for shot in cuts['shots'] if not (raw_dir / shot['file']).is_file()]
    if missing:
        raise CutError('missing raw clip: ' + ', '.join(missing))
    info = {}
    for shot in cuts['shots']:
        path = raw_dir / shot['file']
        probed = _probe(path)
        if (probed['width'], probed['height']) != (WIDTH, HEIGHT):
            raise CutError(f'{shot["file"]} is {probed["width"]}x{probed["height"]}, required {WIDTH}x{HEIGHT}')
        info[shot['id']] = probed
    for output in cuts['outputs']:
        for segment in output['segments']:
            if 'shot' not in segment:
                continue
            shot = shots[segment['shot']]
            _window(shot, segment, info[shot['id']]['duration'])
    return info


def build(raw_dir, out_dir):
    cuts_path = Path(__file__).resolve().parent / 'cuts.json'
    cuts = load_cuts(cuts_path)
    raw_dir = Path(raw_dir).resolve()
    out_dir = Path(out_dir).resolve()
    if not raw_dir.is_dir():
        raise CutError('raw directory is missing')
    if raw_dir == out_dir:
        raise CutError('raw directory and output directory must differ')
    out_dir.mkdir(parents=True, exist_ok=True)
    info = _require_raw(cuts, raw_dir)
    synthetic = _synthetic_enabled(raw_dir)
    work = out_dir / '.work'
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    published = False
    try:
        shots = {shot['id']: shot for shot in cuts['shots']}
        cards = {card['id']: card for card in cuts['cards']}
        cache = {}
        rendered = []
        for output in cuts['outputs']:
            parts = []
            for segment in output['segments']:
                mode = 'raw' if output['group'] == 'raw' else 'program'
                if 'shot' in segment:
                    shot = shots[segment['shot']]
                    start = segment['in_s'] if 'in_s' in segment else shot['in_s']
                    end = segment['out_s'] if 'out_s' in segment else shot['out_s']
                    key = f'shot-{shot["id"]}-{start}-{end}-{mode}'
                    if key not in cache:
                        print(f'encode {key}', file=sys.stderr, flush=True)
                        cache[key] = _render_shot(
                            work, key, raw_dir / shot['file'], shot, segment, mode, synthetic, info[shot['id']])
                    parts.append(cache[key])
                if 'card' in segment:
                    card = cards[segment['card']]
                    duration = segment['card_duration_s'] if 'card_duration_s' in segment else card['duration_s']
                    key = f'card-{card["id"]}-{duration}'
                    if key not in cache:
                        print(f'encode {key}', file=sys.stderr, flush=True)
                        cache[key] = _render_card(work, key, card, duration, synthetic)
                    parts.append(cache[key])
            rendered.append((output, parts))
        for output, parts in rendered:
            seconds = output_duration(cuts, output)
            print(f'join {output["file"]}', file=sys.stderr, flush=True)
            _concat(work, parts, out_dir / output['file'], output['id'], seconds)
        published = True
    finally:
        if published and work.exists():
            shutil.rmtree(work)


def synthetic(dest):
    cuts = load_cuts(Path(__file__).resolve().parent / 'cuts.json')
    dest = Path(dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    if not FONT.is_file():
        raise CutError('required font missing')
    for shot in cuts['shots']:
        length = shot['planned_duration_s']
        frames = length * FPS
        key = f'synthetic-{shot["id"]}'
        print(f'encode {key}', file=sys.stderr, flush=True)
        text = f'SYNTHETIC {shot["id"]}'
        color = f'color=c={shot["synthetic_color"]}:s={WIDTH}x{HEIGHT}:r={FPS}:d={length}'
        graph = (
            '[0:v]format=yuv420p,'
            f'drawtext=fontfile={FONT_BOLD}:text={_filter_text(text)}:'
            'fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2[v]'
        )
        _encode_base(graph, ['-f', 'lavfi', '-i', color], frames, dest / shot['file'], key, dest)
        _expect(dest / shot['file'], length, shot['file'])
    (dest / MARKER_NAME).write_text(MARKER_TEXT + '\n', encoding='utf-8')


def _filter_text(text):
    if any(ch in text for ch in "':\\%,[]"):
        raise CutError('synthetic label has a filter character')
    return "'" + text + "'"


def main(argv):
    try:
        if len(argv) < 2 or argv[1] not in ('build', 'synthetic'):
            raise CutError('usage: build_cuts.sh <raw-dir> <out-dir> | make_synthetic.sh <dir>')
        if not FONT.is_file() or not FONT_BOLD.is_file():
            raise CutError('required font missing')
        if shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None:
            raise CutError('required tool missing: ffmpeg')
        if argv[1] == 'build':
            if len(argv) != 4:
                raise CutError('usage: build_cuts.sh <raw-dir> <out-dir>')
            build(argv[2], argv[3])
        else:
            if len(argv) != 3:
                raise CutError('usage: make_synthetic.sh <dir>')
            synthetic(argv[2])
    except CutError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

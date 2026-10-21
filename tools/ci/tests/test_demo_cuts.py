"""Demo-cut composition: cuts.json schema and the shot-list duration totals."""

import importlib.util
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CUTS = REPO / 'tools' / 'demo' / 'cuts.json'
PLAN = (12, 22, 28, 30, 32, 18, 14)
SEARCH = (
    'Prime Video opens its search screen (searchOpened). '
    'Provider video is not shown, to respect copyright.'
)


def load_pipeline():
    spec = importlib.util.spec_from_file_location(
        'afc_demo_pipeline', REPO / 'tools' / 'demo' / 'pipeline.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def window(shot, segment):
    start = segment['in_s'] if 'in_s' in segment else shot['in_s']
    end = segment['out_s'] if 'out_s' in segment else shot['out_s']
    return end - start


class DemoCuts(unittest.TestCase):
    def setUp(self):
        self.cuts = json.loads(CUTS.read_text(encoding='utf-8'))
        self.shots = {shot['id']: shot for shot in self.cuts['shots']}
        self.cards = {card['id']: card for card in self.cuts['cards']}
        self.outputs = {item['id']: item for item in self.cuts['outputs']}

    def seconds(self, segment):
        total = window(self.shots[segment['shot']], segment) if 'shot' in segment else 0
        if 'card' in segment:
            card = self.cards[segment['card']]
            total += segment.get('card_duration_s', card['duration_s'])
        return total

    def test_schema_matches_the_loader(self):
        module = load_pipeline()
        loaded = module.load_cuts(CUTS)
        self.assertEqual(loaded['frame_rate'], 30)
        self.assertEqual(loaded['audio'], 'silent')
        self.assertEqual(loaded['resolution'], {'width': 1920, 'height': 1080})

    def test_shot_durations_total_156(self):
        ids = [shot['id'] for shot in self.cuts['shots']]
        files = [shot['file'] for shot in self.cuts['shots']]
        planned = [shot['planned_duration_s'] for shot in self.cuts['shots']]
        self.assertEqual(ids, [f'S{n}' for n in range(1, 8)])
        self.assertEqual(files, [f'S{n}.mp4' for n in range(1, 8)])
        self.assertEqual(tuple(planned), PLAN)
        self.assertEqual(sum(planned), 156)

    def test_s4_card_fills_the_planned_shot(self):
        shot = self.shots['S4']
        card = self.cards['searchOpened']
        self.assertEqual(shot['align'], 'end')
        self.assertEqual(shot['title_card'], 'searchOpened')
        self.assertEqual((shot['out_s'] - shot['in_s']) + card['duration_s'], 30)
        self.assertEqual(' '.join(card['lines']), SEARCH)
        self.assertEqual(
            [item['id'] for item in self.cuts['shots'] if item['align'] == 'end'],
            ['S4'],
        )

    def test_replay_label_is_only_s3(self):
        labelled = [shot['id'] for shot in self.cuts['shots'] if 'REPLAY' in shot['labels']]
        self.assertEqual(labelled, ['S3'])

    def test_main_is_156_and_teaser_is_30(self):
        main = [self.seconds(segment) for segment in self.outputs['main']['segments']]
        teaser = [self.seconds(segment) for segment in self.outputs['teaser']['segments']]
        self.assertEqual(main, [12, 22, 28, 30, 32, 18, 14])
        self.assertEqual(sum(main), 156)
        self.assertEqual(teaser, [5, 7, 10, 5, 3])
        self.assertEqual(sum(teaser), 30)
        self.assertGreaterEqual(sum(teaser), 25)
        self.assertLessEqual(sum(teaser), 35)
        self.assertLessEqual(sum(main), 170)

    def test_feature_and_raw_outputs(self):
        self.assertEqual(self.outputs['alerts']['file'], 'feature-alerts.mp4')
        self.assertEqual(self.outputs['watch']['file'], 'feature-watch.mp4')
        self.assertEqual(self.outputs['panel']['file'], 'feature-panel.mp4')
        self.assertEqual(self.outputs['linking']['file'], 'feature-linking.mp4')
        self.assertEqual(self.outputs['alerts']['segments'], [{'shot': 'S3'}])
        self.assertEqual(self.outputs['panel']['segments'], [{'shot': 'S5'}])
        self.assertEqual(self.outputs['linking']['segments'], [{'card': 'linking'}])
        self.assertIn('card', self.outputs['watch']['segments'][0])
        self.assertIn('note', self.cards['linking'])
        raw_seconds = {
            1: 12, 2: 22, 3: 28, 4: 22, 5: 32, 6: 18, 7: 14,
        }
        for number, expected in raw_seconds.items():
            raw = self.outputs[f'raw-S{number}']
            self.assertEqual(raw['file'], f'raw-S{number}.mp4')
            self.assertEqual(raw['group'], 'raw')
            self.assertNotIn('card', raw['segments'][0])
            self.assertEqual(self.seconds(raw['segments'][0]), expected)

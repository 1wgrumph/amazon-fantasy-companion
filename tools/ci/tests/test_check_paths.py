"""check_paths tests: AC-AFC-CI-03 (SEIT-AFC-CI-03) and AC-AFC-PATH-01
(SEIT-AFC-PATH-01.H), per DES-AFC-GATE hygiene area.

Fixtures are generated at test time; no literal secret or home path is
committed, so this file passes the scan it tests.
"""

import random
import shutil
import string
import tempfile
import unittest
from pathlib import Path

from gate_support import REPO, call_main, init_repo, load_tool, write

SEP = '/'
BACK = '\\'


def token(rule, alphabet, size):
    return ''.join(random.Random(rule).choices(alphabet, k=size))


def fixtures():
    """rule id -> (fixture line, sensitive text that must never be printed)."""
    hexdigits = '0123456789abcdef'
    b64 = string.ascii_letters + string.digits + '/+'
    lines = {
        'PATH-HOME-POSIX': (f'see {SEP}home{SEP}alice{SEP}notes.txt', f'{SEP}home{SEP}alice{SEP}'),
        'PATH-HOME-MAC': (f'see {SEP}Users{SEP}alice{SEP}notes.txt', f'{SEP}Users{SEP}alice{SEP}'),
        'PATH-HOME-WIN': (f'see C:{BACK}Users{BACK}alice{BACK}notes.txt', f'C:{BACK}Users{BACK}alice{BACK}'),
    }
    secrets = {
        'CRED-AWS-KEY-ID': ('aws_access_key_id = {}', 'AKIA' + token('aws-id', string.ascii_uppercase + string.digits, 16)),
        'CRED-AWS-SECRET': ('aws_secret_access_key = {}', token('aws-secret', b64, 40)),
        'CRED-YAHOO-SECRET': ('YAHOO_CLIENT_SECRET={}', token('yahoo', hexdigits, 40)),
        'CRED-OAUTH-TOKEN': ('{{"access_token": "{}"}}', token('oauth', string.ascii_letters + string.digits + '._-', 48)),
        'CRED-DEVICE-TOKEN': ('device_token: {}', token('device', hexdigits, 64)),
    }
    for rule, (shape, value) in secrets.items():
        lines[rule] = (shape.format(value), value)
    return lines


class AC_AFC_CI_03(unittest.TestCase):
    """Each rule reports file:line:rule-id without the matched text; placeholders
    pass; --files applies the same rules to only the named files."""

    def setUp(self):
        self.tool = load_tool(self, 'check_paths')
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_each_rule_reports_file_line_rule_id_without_matched_text(self):
        for rule, (line, sensitive) in fixtures().items():
            with self.subTest(rule=rule):
                name = f'{rule.lower()}.txt'
                write(self.tmp, {name: f'fixture\n{line}\n'})
                rc, out = call_main(self.tool, ['--files', name], self.tmp)
                self.assertEqual(rc, 1, out)
                self.assertIn(f'{name}:2:{rule}', out.splitlines())
                self.assertNotIn(sensitive, out)

    def test_placeholder_user_segments_pass(self):
        write(self.tmp, {'placeholders.md': '\n'.join([
            f'{SEP}home{SEP}user{SEP}project',
            f'{SEP}Users{SEP}example-user{SEP}project',
            f'C:{BACK}Users{BACK}someone{BACK}project',
        ]) + '\n'})
        rc, out = call_main(self.tool, ['--files', 'placeholders.md'], self.tmp)
        self.assertEqual(rc, 0, out)
        self.assertNotIn('PATH-HOME', out)

    def test_relative_path_with_a_folder_named_home_passes(self):
        write(self.tmp, {'assets.json': f'"web{SEP}src{SEP}components{SEP}home{SEP}hero{SEP}home-dark.png"\n'})
        rc, out = call_main(self.tool, ['--files', 'assets.json'], self.tmp)
        self.assertEqual(rc, 0, out)
        self.assertNotIn('PATH-HOME', out)

    def test_files_option_scans_only_named_files(self):
        line, _ = fixtures()['PATH-HOME-POSIX']
        write(self.tmp, {'dirty.md': f'{line}\n', 'clean.md': 'nothing here\n'})
        rc, out = call_main(self.tool, ['--files', 'clean.md'], self.tmp)
        self.assertEqual(rc, 0, out)
        rc, out = call_main(self.tool, ['--files', 'clean.md', 'dirty.md'], self.tmp)
        self.assertEqual(rc, 1, out)
        self.assertIn('dirty.md:1:PATH-HOME-POSIX', out.splitlines())
        self.assertNotIn('clean.md', out)


class AC_AFC_PATH_01(unittest.TestCase):
    """No PATH-HOME-* finding over this repository's tracked files."""

    def setUp(self):
        self.tool = load_tool(self, 'check_paths')
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_repository_tracked_files_have_no_home_path(self):
        _, out = call_main(self.tool, [], REPO)
        self.assertEqual([l for l in out.splitlines() if ':PATH-HOME-' in l], [])

    def test_seeded_tracked_home_path_reported_and_untracked_ignored(self):
        fx = fixtures()
        repo = init_repo(self.tmp, {'docs/notes.md': 'a\nb\n' + fx['PATH-HOME-MAC'][0] + '\n'})
        write(repo, {'scratch.md': fx['PATH-HOME-POSIX'][0] + '\n'})
        rc, out = call_main(self.tool, [], repo)
        self.assertEqual(rc, 1, out)
        self.assertIn('docs/notes.md:3:PATH-HOME-MAC', out.splitlines())
        self.assertNotIn('scratch.md', out)


if __name__ == '__main__':
    unittest.main()

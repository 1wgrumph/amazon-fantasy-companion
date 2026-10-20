"""check_provider_art tests: withheld provider imagery cannot re-enter the tree.

Fixtures are generated at test time from the check's own denylist, so this
file does not contain a withheld basename or content hash.
"""

import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path

from gate_support import call_main, commit_all, init_repo, load_tool, run_as_script, write


class CheckProviderArt(unittest.TestCase):
    def setUp(self):
        self.tool = load_tool(self, 'check_provider_art')
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def repo(self, name, files=None):
        root = self.tmp / name
        root.mkdir()
        return init_repo(root, files)

    def test_records_cover_twenty_unique_paths_and_hashes(self):
        paths = [path for path, _digest in self.tool.RECORDS]
        digests = [digest for _path, digest in self.tool.RECORDS]
        names = [path.rsplit('/', 1)[-1] for path in paths]
        self.assertEqual(len(self.tool.RECORDS), 20)
        self.assertEqual(len(set(paths)), 20)
        self.assertEqual(len(set(digests)), 20)
        self.assertEqual(self.tool.HASHES, frozenset(digests))
        self.assertEqual(self.tool.BASENAMES, frozenset(names))
        self.assertEqual(len(names) - len(set(names)), 1)

    def test_usage_error_exits_2(self):
        rc, out = call_main(self.tool, ['--files'], self.tmp)
        self.assertEqual(rc, 2, out)
        self.assertIn('usage: check_provider_art.py', out)

    def test_clean_tree_passes(self):
        root = self.repo('clean', {'notes/readme.txt': 'companion ui only\n'})
        rc, out = call_main(self.tool, [], root)
        self.assertEqual(rc, 0, out)
        self.assertEqual(out, '')

    def test_main_entrypoint_passes_on_a_clean_tree(self):
        root = self.repo('entry', {'notes/readme.txt': 'ok\n'})
        self.assertEqual(run_as_script('check_provider_art', [], root), 0)

    def test_forbidden_basename_fails_and_names_the_file(self):
        base = sorted(self.tool.BASENAMES)[0]
        sentinel = 'SENTINEL-BODY-not-printed'
        root = self.repo('name', {f'incoming/{base}': sentinel + '\n'})
        rc, out = call_main(self.tool, [], root)
        self.assertEqual(rc, 1, out)
        self.assertIn(f'incoming/{base}:PROVIDER-ART-NAME', out.splitlines())
        self.assertNotIn(sentinel, out)

    def test_same_bytes_under_another_name_fail(self):
        payload = b'withheld-bytes\n'
        digest = hashlib.sha256(payload).hexdigest()
        self.tool.HASHES = frozenset(set(self.tool.HASHES) | {digest})
        self.addCleanup(setattr, self.tool, 'HASHES', frozenset(
            item[1] for item in self.tool.RECORDS))
        root = self.repo('hash', {})
        (root / 'renamed.bin').write_bytes(payload)
        commit_all(root, 'add renamed bytes')
        rc, out = call_main(self.tool, [], root)
        self.assertEqual(rc, 1, out)
        self.assertIn('renamed.bin:PROVIDER-ART-HASH', out.splitlines())
        self.assertNotIn(digest, out)

    def test_null_bytes_do_not_hide_a_content_hash(self):
        payload = b'withheld\0bytes'
        digest = hashlib.sha256(payload).hexdigest()
        original = self.tool.HASHES
        self.tool.HASHES = frozenset(set(original) | {digest})
        self.addCleanup(setattr, self.tool, 'HASHES', original)
        root = self.repo('binary', {})
        (root / 'frame.bin').write_bytes(payload)
        commit_all(root, 'add binary')
        rc, out = call_main(self.tool, [], root)
        self.assertEqual(rc, 1, out)
        self.assertIn('frame.bin:PROVIDER-ART-HASH', out.splitlines())

    def test_text_mention_of_a_basename_or_hash_fails(self):
        base = sorted(self.tool.BASENAMES)[0]
        digest = sorted(self.tool.HASHES)[0]
        root = self.repo('text', {
            'notes/again.md': f'see {base} and {digest}\n',
        })
        rc, out = call_main(self.tool, [], root)
        self.assertEqual(rc, 1, out)
        self.assertIn('notes/again.md:1:PROVIDER-ART-TEXT', out.splitlines())
        self.assertNotIn(base, out)
        self.assertNotIn(digest, out)

    def test_manifest_path_may_record_the_name_and_hash(self):
        manifest = next(path for path in self.tool.TEXT_ALLOW if path.endswith('PRIVATE-EVIDENCE.md'))
        base = sorted(self.tool.BASENAMES)[0]
        digest = sorted(self.tool.HASHES)[0]
        root = self.repo('manifest', {
            manifest: f'{base}\n{digest}\n',
            'notes/leak.md': f'{base}\n',
        })
        rc, out = call_main(self.tool, [], root)
        self.assertEqual(rc, 1, out)
        self.assertIn('notes/leak.md:1:PROVIDER-ART-TEXT', out.splitlines())
        self.assertNotIn('PRIVATE-EVIDENCE.md', out)

    def test_missing_tracked_file_fails_closed(self):
        root = self.repo('missing', {'keep.txt': 'present\n'})
        (root / 'keep.txt').unlink()
        rc, out = call_main(self.tool, [], root)
        self.assertEqual(rc, 1, out)
        self.assertIn('check_provider_art: unreadable input or git failure', out)

    def test_outside_a_git_repository_fails_closed(self):
        rc, out = call_main(self.tool, [], self.tmp)
        self.assertEqual(rc, 1, out)
        self.assertIn('check_provider_art: unreadable input or git failure', out)

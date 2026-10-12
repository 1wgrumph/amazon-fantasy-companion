"""check_docs tests: the docs area of AC-AFC-CI-04 (SEIT-AFC-CI-04.U), per
DES-AFC-GATE: Vnv area headings and relative Markdown links."""

import re
import shutil
import tempfile
import unittest
from pathlib import Path

from gate_support import call_main, commit_all, init_repo, load_tool, run_as_script, write

HEADINGS = ('Scope', 'Tools', 'Review Focus', 'Findings target')
AREA = 'docs/vnv/demo/AGENTS.md'


def area_file(headings=HEADINGS):
    body = ['# Demo review guidance', '']
    for heading in headings:
        body += [f'## {heading}', '', f'{heading} text. See the [index](../AGENTS.md).', '']
    return '\n'.join(body)


def tree(**overrides):
    files = {
        'docs/vnv/AGENTS.md': '# Vnv index\n\n- [demo](demo/AGENTS.md)\n',
        AREA: area_file(),
        'README.md': '\n'.join([
            '# Readme',
            '',
            '[demo area](docs/vnv/demo/AGENTS.md)',
            '[scope section](docs/vnv/demo/AGENTS.md#scope)',
            '[external](https://example.invalid/not-fetched)',
            '[anchor](#readme)',
            '',
        ]),
    }
    files.update(overrides)
    return files


class AC_AFC_CI_04_Docs(unittest.TestCase):

    def setUp(self):
        self.tool = load_tool(self, 'check_docs')
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_complete_area_and_resolving_links_pass(self):
        repo = init_repo(self.tmp, tree())
        rc, out = call_main(self.tool, [], repo)
        self.assertEqual(rc, 0, out)
        self.assertNotIn('DOC-', out)

    def test_area_missing_any_required_heading_exits_1(self):
        for missing in HEADINGS:
            with self.subTest(missing=missing):
                repo = Path(tempfile.mkdtemp(dir=self.tmp))
                init_repo(repo, tree(**{AREA: area_file([h for h in HEADINGS if h != missing])}))
                rc, out = call_main(self.tool, [], repo)
                self.assertEqual(rc, 1, out)
                self.assertTrue(any(re.fullmatch(r'docs/vnv/demo/AGENTS\.md:\d+:DOC-[A-Z0-9-]+', l)
                                    for l in out.splitlines()), out)

    def test_relative_link_to_missing_path_exits_1(self):
        repo = init_repo(self.tmp, tree())
        write(repo, {'GUIDE.md': '# Guide\n\n[gone](docs/does-not-exist.md)\n'})
        commit_all(repo)
        rc, out = call_main(self.tool, [], repo)
        self.assertEqual(rc, 1, out)
        self.assertTrue(any(re.fullmatch(r'GUIDE\.md:3:DOC-[A-Z0-9-]+', l) for l in out.splitlines()), out)

    def test_any_argument_is_a_usage_error_exit_2(self):
        rc, out = call_main(self.tool, ['--unexpected'], init_repo(self.tmp, tree()))
        self.assertEqual(rc, 2, out)
        self.assertIn('usage: check_docs.py', out)

    def test_unreadable_markdown_or_git_failure_exits_1(self):
        (self.tmp / 'repo').mkdir()
        repo = init_repo(self.tmp / 'repo', tree(**{'BAD.md': ''}))
        (repo / 'BAD.md').write_bytes(b'# bad \xff\xfe\n')
        outside = self.tmp / 'not-a-repo'
        outside.mkdir()
        for cwd in (repo, outside):
            with self.subTest(cwd=cwd.name):
                rc, out = call_main(self.tool, [], cwd)
                self.assertEqual(rc, 1, out)
                self.assertIn('check_docs: unreadable input or git failure', out)

    def test_script_entrypoint_exits_with_main_status(self):
        repo = init_repo(self.tmp, tree())
        self.assertEqual(run_as_script('check_docs', [], repo), 0)
        self.assertEqual(run_as_script('check_docs', ['extra'], repo), 2)


if __name__ == '__main__':
    unittest.main()

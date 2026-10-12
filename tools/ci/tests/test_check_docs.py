"""check_docs tests: the docs area of AC-AFC-CI-04 (SEIT-AFC-CI-04.U), per
DES-AFC-GATE: Vnv area headings and relative Markdown links."""

import re
import shutil
import tempfile
import unittest
from pathlib import Path

from gate_support import call_main, commit_all, init_repo, load_tool, write

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


if __name__ == '__main__':
    unittest.main()

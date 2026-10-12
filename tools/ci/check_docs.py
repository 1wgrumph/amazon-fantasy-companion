#!/usr/bin/env python3
"""Check tracked Markdown links and the VnV area guidance headings."""

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

HEADINGS = ('Scope', 'Tools', 'Review Focus', 'Findings target')
LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[\"\'][^\n]*?[\"\'])?\s*\)|^\s*\[[^\]\n]+\]:\s*(<[^>]+>|\S+)', re.M)


def prose(text):
    # Preserve line numbers while ignoring examples inside code blocks and spans.
    text = re.sub(r'^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*\1\s*$',
                  lambda m: '\n' * m.group().count('\n'), text, flags=re.M | re.S)
    return re.sub(r'(`+)[^\n]*?\1', lambda m: ' ' * len(m.group()), text)


def main(argv):
    if argv:
        print('usage: check_docs.py')
        return 2
    try:
        files = subprocess.check_output(['git', 'ls-files', '-z']).decode().split('\0')
        failed = False
        for name in files:
            if not name.endswith('.md'):
                continue
            path = Path(name)
            text = prose(path.read_text(encoding='utf-8'))
            if path.match('docs/vnv/*/AGENTS.md'):
                headings = re.findall(r'^##\s+(.+?)\s*$', text, re.M)
                for required in HEADINGS:
                    if required not in headings:
                        print(f'{name}:1:DOC-HEADING')
                        failed = True
            for match in LINK.finditer(text):
                target = (match.group(1) or match.group(2)).strip('<>')
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path or url.path.startswith('/'):
                    continue
                if not (path.parent / unquote(url.path)).exists():
                    number = text.count('\n', 0, match.start()) + 1
                    print(f'{name}:{number}:DOC-LINK')
                    failed = True
        return int(failed)
    except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError):
        print('check_docs: unreadable input or git failure')
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]))

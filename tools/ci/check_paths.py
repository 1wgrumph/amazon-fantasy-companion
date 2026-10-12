#!/usr/bin/env python3
"""Report private home paths and credential shapes without echoing their values."""

import argparse
import re
import subprocess
from pathlib import Path

PLACEHOLDERS = {'user', 'example-user', 'someone'}
HOME_RULES = {
    'PATH-HOME-POSIX': re.compile(r'(?<![\w./\\-])/' + r'home/([\w.-]+)/'),
    'PATH-HOME-MAC': re.compile(r'(?<![\w./\\-])/' + r'Users/([\w .-]+)/'),
    'PATH-HOME-WIN': re.compile(r'(?<![\w])' + r'[A-Za-z]:\\Users\\([\w .-]+)\\', re.I),
}
ASSIGNMENT = r'''[\"']?\s*[:=]\s*[\"']?'''
RULES = {
    'CRED-AWS-KEY-ID': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'CRED-AWS-SECRET': re.compile(r'\baws_secret_access_key' + ASSIGNMENT + r'[A-Za-z0-9/+]{40}(?![A-Za-z0-9/+])', re.I),
    'CRED-YAHOO-SECRET': re.compile(r'\byahoo_client_secret' + ASSIGNMENT + r'[A-Za-z0-9._/+\-]{40,}(?![A-Za-z0-9._/+\-])', re.I),
    'CRED-OAUTH-TOKEN': re.compile(r'\b(?:access_token|refresh_token)' + ASSIGNMENT + r'[A-Za-z0-9._/+\-]{32,}(?![A-Za-z0-9._/+\-])', re.I),
    'CRED-DEVICE-TOKEN': re.compile(r'\bdevice_token' + ASSIGNMENT + r'[A-Za-z0-9._/+\-]{32,}(?![A-Za-z0-9._/+\-])', re.I),
}


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--files', nargs='+')
    args = parser.parse_args(argv)
    try:
        files = args.files if args.files is not None else subprocess.check_output(
            ['git', 'ls-files', '-z']).decode().split('\0')
        failed = False
        for name in filter(None, files):
            path = Path(name)
            if path.is_dir():
                continue
            data = path.read_bytes()
            if b'\0' in data:
                continue
            for number, line in enumerate(data.decode('utf-8', errors='replace').splitlines(), 1):
                for rule, pattern in HOME_RULES.items():
                    if any(m.group(1).lower() not in PLACEHOLDERS for m in pattern.finditer(line)):
                        print(f'{name}:{number}:{rule}')
                        failed = True
                for rule, pattern in RULES.items():
                    if pattern.search(line):
                        print(f'{name}:{number}:{rule}')
                        failed = True
        return int(failed)
    except (OSError, subprocess.CalledProcessError):
        print('check_paths: unreadable input or git failure')
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]))

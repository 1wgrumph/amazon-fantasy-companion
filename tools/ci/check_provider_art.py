#!/usr/bin/env python3
"""Fail when withheld provider imagery reappears in the git tree.

The twenty captures below are provider UI, title art, ads, team logos, or a
third-party site. Two of them share the basename prime-video-search.png and
are distinguished by directory and content sha256. A tracked path fails when
any component is one of those basenames, or when the file's sha256 is one of
those content hashes. Any other tracked text file fails when it contains a
basename or a content hash. The manifest, this check, and the red run may
record the names and hashes; that allowlist does not cover a re-added file.
"""

import hashlib
import os
import subprocess
from pathlib import Path

# Former repo path, content sha256. Capture facts live in the manifest.
RECORDS = (
    ('evidence/visual/P2-A04/prime-video-search.png',
     '47c82cd5f78331359613ba9802b83ef318ed55b60d60b17fd4c7ca44f3ce2f99'),
    ('evidence/visual/sp2-notify/attempt2-prime-home.png',
     'efe248b84ca015d1e812b9f3788d9a847312cbe60a84b5e96fb3ad5075963044'),
    ('evidence/visual/sp2-notify/attempt3-prime-after-select.png',
     'c8e22045307a4f2c840c11366f2ad420e541242cf6f80277229544598aca4d8b'),
    ('evidence/visual/sp2-notify/attempt3-prime-home.png',
     '2b3233be64bba432b330d355e7b775d415a5bc46026106ec3d286eacf93d8d1f'),
    ('evidence/visual/sp2-notify/attempt5-dpad-up.png',
     '8c5a7b442643b3b807bfbf18346baeb8efcf5b97df967a81c8b83e0f8129cc00'),
    ('evidence/visual/sp2-notify/attempt6-dismiss-target.png',
     'f29cbd60d304628f3269139ffd9dd53b4733174f6803b3f457833fbe3c2dd6e5'),
    ('evidence/visual/sp2-notify/attempt6-home.png',
     'd5e8fb9ea352cc704253dd6edaf219518200e2a6e69e326300524c99b9fac722'),
    ('evidence/visual/sp2-notify/attempt6-notif-key.png',
     'eb9230888043fea4f435790a9d48fff1e1518240608ac6a6b6010eeff6cec4b4'),
    ('evidence/visual/sp2-notify/attempt7-home-headsup.png',
     '145bb53e867b2f54181c1b0d18ba88ea8b210742ef55bdd198563c3eb336944f'),
    ('evidence/visual/sp2-notify/repair9-fsi-dpad-up.png',
     '837b6a636dcd83569775d999b834d50b38218bedea4f0918a3381ed566c9a418'),
    ('evidence/visual/sp3-provider-links/local-broadcast-home.png',
     '4fc5bbaa6e13e49237430c42920647b44030e2f8c9fbd873eb42e0514c8c69e0'),
    ('evidence/visual/sp3-provider-links/prime-video-detail-cold.png',
     'efa2d3f94bb134d429a47e18b03cb2683c77d8b0c94c4541f4183ae26c70fb14'),
    ('evidence/visual/sp3-provider-links/prime-video-home.png',
     '7629bd89773a519e1af0896fbe3c1dd4cec56bf6f0a040b7548ec92b96873cb5'),
    ('evidence/visual/sp3-provider-links/prime-video-search.png',
     '2b2c1732b526af97ac94a1a8564573c08909729fc1f2e8ee959d93ca6bcdd1d8'),
    ('evidence/visual/sp3-provider-links/youtube-tv-view-browser.png',
     '72a4b0a7575376a5cf6825da1afe2116abdfa5f4e4bf97b0bd806bcc4457b649'),
    ('evidence/visual/sp4-panel-video/r1-provider-pip-home.png',
     'db9ca4d861ea442213f6187cc6f6d2422fb786ebec9e0bd8acd07def16cf47d3'),
    ('evidence/visual/sp4-panel-video/r1b-return-prime.png',
     '5970a49093f2c619947d2f437eb4e502953222eb56448a9435cb7e56b8edf70b'),
    ('evidence/visual/sp4-panel-video/r2-spike-pip-entered.png',
     'e9a37c6ac640b39a6e4d2d7ced07a3091496e3510558617bd1b508cc8be8a7a2'),
    ('evidence/visual/sp4-panel-video/r2-spike-pip-over-prime.png',
     '3e3de2e78148be1da8aa5d27b335993cf51c871b77047e47b3644cc32cafbb53'),
    ('evidence/visual/sp4-panel-video/r6-final-prime.png',
     'bed3b55f47f380abfea4cdc9476e500944e22e19c300b52b5b01dd02a201162d'),
)

BASENAMES = frozenset(path.rsplit('/', 1)[-1] for path, _digest in RECORDS)
HASHES = frozenset(digest for _path, digest in RECORDS)
TEXT_ALLOW = frozenset({
    'tools/ci/check_provider_art.py',
    'evidence/visual/PRIVATE-EVIDENCE.md',
    'docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-PROVIDER-ART/red.txt',
})

_GIT_DROP = (
    'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_PREFIX', 'GIT_COMMON_DIR',
    'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_IMPLICIT_WORK_TREE',
    'GIT_GRAFT_FILE', 'GIT_SHALLOW_FILE', 'GIT_INTERNAL_SUPER_PREFIX',
)


def git_env():
    env = {key: value for key, value in os.environ.items() if key not in _GIT_DROP}
    env['GIT_CEILING_DIRECTORIES'] = str(Path.cwd().resolve().parent)
    return env


def main(argv):
    if argv:
        print('usage: check_provider_art.py')
        return 2
    try:
        listed = subprocess.check_output(
            ['git', 'ls-files', '-z'], env=git_env(), stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        print('check_provider_art: unreadable input or git failure')
        return 1
    findings = []
    try:
        for name in filter(None, listed.decode().split('\0')):
            path = Path(name)
            if any(part in BASENAMES for part in path.parts):
                findings.append(f'{name}:PROVIDER-ART-NAME')
            if path.is_dir():
                continue
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() in HASHES:
                findings.append(f'{name}:PROVIDER-ART-HASH')
            if name in TEXT_ALLOW or b'\0' in data:
                continue
            for number, line in enumerate(data.decode('utf-8', errors='replace').splitlines(), 1):
                if any(base in line for base in BASENAMES) or any(digest in line for digest in HASHES):
                    findings.append(f'{name}:{number}:PROVIDER-ART-TEXT')
    except (OSError, UnicodeError):
        print('check_provider_art: unreadable input or git failure')
        return 1
    if findings:
        print('\n'.join(sorted(set(findings))))
        return 1
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]))

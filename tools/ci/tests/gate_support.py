"""Shared helpers for the gate tests (DES-AFC-GATE, CONTRACT-AFC-GATE).

A missing product file is reported as a failed assertion, never as an import
error, so the S09T red run is a valid red (SEIT tdd red_expectation).
"""

import contextlib
import importlib.util
import io
import json
import os
import runpy
import shutil
import sys
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TESTS = Path('tools/ci/tests')
STUB_TEST = 'import unittest\n\n\nclass Stub(unittest.TestCase):\n    def test_ok(self):\n        pass\n'


def load_tool(case, name):
    path = REPO / 'tools' / 'ci' / f'{name}.py'
    case.assertTrue(path.is_file(), f'tools/ci/{name}.py is missing')
    spec = importlib.util.spec_from_file_location(f'afc_gate_{name}', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case.assertTrue(callable(getattr(module, 'main', None)), f'tools/ci/{name}.py has no main(argv)')
    return module


def call_main(module, argv, cwd):
    """Run module.main(argv) in-process in cwd; return (rc, combined output)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.chdir(cwd), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = module.main(list(argv))
        except SystemExit as exc:
            rc = exc.code
    return rc, out.getvalue() + err.getvalue()


def run_as_script(name, argv, cwd):
    """Run tools/ci/<name>.py as __main__ in-process so coverage sees it; return its exit code."""
    path = REPO / 'tools' / 'ci' / f'{name}.py'
    saved = sys.argv
    sys.argv = [str(path), *argv]
    try:
        with contextlib.chdir(cwd), contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(path), run_name='__main__')
    except SystemExit as exc:
        return exc.code
    finally:
        sys.argv = saved
    return None


def git(cwd, *args):
    subprocess.run(['git', '-c', 'user.name=Gate Test', '-c', 'user.email=gate-test@example.invalid',
                    '-c', 'commit.gpgsign=false', *args],
                   cwd=cwd, check=True, capture_output=True, text=True)


def write(root, files):
    for rel, text in files.items():
        path = Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')


def commit_all(root, message='fixture'):
    git(root, 'add', '-A')
    git(root, 'commit', '-q', '--no-verify', '--allow-empty', '-m', message)


def init_repo(root, files=None):
    git(root, 'init', '-q', '-b', 'main')
    write(root, files or {})
    commit_all(root)
    return Path(root)


def copy_repo(root):
    """Copy this repository's tracked files into a new git repo at root.

    tools/ci/tests is replaced by one passing stub test so a hygiene run in the
    copy does not recurse into these tests; linked repository documents are kept.
    Real product trees (backend/, tv-app/) are excluded; tests needing one
    create their own fixture.
    """
    listed = subprocess.run(['git', 'ls-files', '-z'],
                            cwd=REPO, check=True, capture_output=True).stdout.decode()
    for rel in filter(None, listed.split('\0')):
        if (rel.startswith(str(TESTS) + '/') or rel.startswith('backend/')
                or rel.startswith('tv-app/') or not (REPO / rel).is_file()):
            continue
        target = Path(root) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, target)
    write(root, {str(TESTS / 'test_stub.py'): STUB_TEST})
    git(root, 'init', '-q', '-b', 'main')
    commit_all(root)
    return Path(root)


def run_gate(case, cwd, *args, env=None):
    gate = Path(cwd) / 'tools' / 'ci' / 'gate.sh'
    case.assertTrue(gate.is_file(), 'tools/ci/gate.sh is missing')
    case.assertTrue(os.access(gate, os.X_OK), 'tools/ci/gate.sh is not executable')
    env = dict(os.environ if env is None else env)
    # Fixture repositories have their own history and must not use the host CI event.
    if (Path(cwd) != REPO and os.environ.get('GITHUB_EVENT_PATH')
            and env.get('GITHUB_EVENT_PATH') == os.environ['GITHUB_EVENT_PATH']):
        fixture_base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=cwd,
                                               text=True).strip()
        fixture_event = Path(cwd) / '.git' / 'gate-event.json'
        fixture_event.write_text(json.dumps({'before': fixture_base}), encoding='utf-8')
        env['GITHUB_EVENT_PATH'] = str(fixture_event)
    result = subprocess.run(['tools/ci/gate.sh', *args], cwd=cwd, env=env,
                            capture_output=True, text=True, timeout=900)
    return result.returncode, result.stdout + result.stderr


def path_without(tool, farm):
    """Return a PATH of symlinks to every executable on PATH except tool."""
    farm = Path(farm)
    farm.mkdir(parents=True, exist_ok=True)
    for directory in os.environ.get('PATH', '').split(os.pathsep):
        if not os.path.isdir(directory):
            continue
        for entry in os.scandir(directory):
            link = farm / entry.name
            if entry.name != tool and not link.exists() and os.access(entry.path, os.X_OK):
                link.symlink_to(entry.path)
    return str(farm)

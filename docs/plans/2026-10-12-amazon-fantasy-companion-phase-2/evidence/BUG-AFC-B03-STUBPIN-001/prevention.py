"""Prove only lineup pins retired and a realized B02 still trips both guards."""
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path.cwd()
OUT = Path(__file__).parent
UNIT = 'backend/tests/unit/test_pipeline_and_stubs.py'
CONTRACT = 'backend/tests/contract/test_backend_template.py'
BASE = '26656b7'


def pins(source, contract=False):
    tree = ast.parse(source)
    if contract:
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and
                  n.name == 'test_future_backend_modules_have_explicit_unimplemented_public_interfaces')
        return ast.literal_eval(fn.decorator_list[0].args[1])
    return ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign) and
                                any(isinstance(t, ast.Name) and t.id == 'STUBS' for t in n.targets)))


for name, contract in [(UNIT, False), (CONTRACT, True)]:
    before = pins(subprocess.check_output(['git', 'show', f'{BASE}:{name}'], text=True), contract)
    after = pins((ROOT / name).read_text(), contract)
    assert after == [p for p in before if (p if contract else p[0]) != 'lineup']
    assert {'feed_ingest', 'matcher', 'alert_policy', 'provider_resolver', 'panel'} == {
        p if contract else p[0] for p in after}

ids = [UNIT + '::test_stubs_name_their_owning_slice[feed_ingest-lambda_handler-2-P2-B02]',
       CONTRACT + '::test_future_backend_modules_have_explicit_unimplemented_public_interfaces[feed_ingest]']
with tempfile.TemporaryDirectory(prefix='afc-b03-prevention-') as scratch:
    copy = Path(scratch)
    shutil.copytree(ROOT / 'backend', copy / 'backend',
                    ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache', 'mutants'))
    (copy / 'backend/src/feed_ingest/__init__.py').write_text(
        'def lambda_handler(event, context):\n    return None\n')
    command = [str(Path.home() / '.local/share/afc-tools/backend-tests/bin/python3.12'),
               '-m', 'pytest', '-q', '-p', 'no:cacheprovider', *ids]
    run = subprocess.run(command, cwd=copy, capture_output=True, text=True,
                         timeout=1500, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    log = (run.stdout + run.stderr).replace(scratch, '<scratch>')
    (OUT / 'prevention.txt').write_text(log)
    assert run.returncode == 1, (run.returncode, log)
    assert '2 failed' in log and 'ERROR' not in log, log
    result = {'outcome': 'PASS', 'remaining_pins': 'B02 and B04-B07 unchanged in both tests',
              'experiment': 'B02 feed_ingest replaced with a non-stub only in scratch copy',
              'command': 'python3.12 -m pytest -q -p no:cacheprovider ' + ' '.join(ids),
              'experiment_exit_code': run.returncode, 'expected_failures': 2,
              'scratch_removed': True, 'product_checkout_unchanged': True}
(OUT / 'prevention-result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))

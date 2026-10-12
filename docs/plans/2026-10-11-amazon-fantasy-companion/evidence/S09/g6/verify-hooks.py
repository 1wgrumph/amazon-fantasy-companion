import subprocess, tempfile, pathlib, os, json, hashlib
source = pathlib.Path.cwd()
e = pathlib.Path(__file__).parent
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
for suffix in ('NAME', 'EMAIL'):
    env['GIT_COMMITTER_' + suffix] = env['GIT_AUTHOR_' + suffix]
locations = ['GIT_DIR', 'GIT_INDEX_FILE', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_PREFIX', 'GIT_IMPLICIT_WORK_TREE', 'GIT_GRAFT_FILE', 'GIT_SHALLOW_FILE', 'GIT_INTERNAL_SUPER_PREFIX']
for k in locations:
    env.pop(k, None)
records = []
def run(args, cwd, environment=env, stdin=None):
    r = subprocess.run(args, cwd=cwd, env=environment, input=stdin, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (e / 'hook-simulation.log').open('a').write('$ ' + ' '.join(args) + '\n' + r.stdout + '\nexit=' + str(r.returncode) + '\n')
    records.append({'command': args, 'exit_code': r.returncode, 'output_tail': r.stdout[-2500:]})
    assert r.returncode == 0, records[-1]
    return r.stdout
with tempfile.TemporaryDirectory(prefix='afc-s09-g6-hook-') as tmp:
    root = pathlib.Path(tmp)
    clone, remote = root / 'clone', root / 'remote.git'
    run(['git', 'clone', '--no-hardlinks', str(source), str(clone)], root)
    run(['git', 'init', '--bare', str(remote)], root)
    run(['git', 'remote', 'set-url', 'origin', str(remote)], clone)
    run(['git', 'update-ref', 'refs/remotes/origin/main', 'HEAD'], clone)
    (clone / 'tools/ci/gate.sh').write_bytes((source / 'tools/ci/gate.sh').read_bytes())
    run(['git', 'config', 'core.hooksPath', '.githooks'], clone)
    run(['git', 'add', 'tools/ci/gate.sh'], clone)
    index = clone / '.git/index'
    before = hashlib.sha256(index.read_bytes()).hexdigest()
    hookenv = dict(env, GIT_DIR='.git', GIT_INDEX_FILE='.git/index', GIT_PREFIX='')
    run(['bash', '.githooks/pre-commit'], clone, hookenv)
    assert hashlib.sha256(index.read_bytes()).hexdigest() == before, 'pre-commit changed clone index'
    assert run(['git', 'rev-parse', 'HEAD'], clone).strip() == run(['git', 'rev-parse', 'HEAD'], source).strip(), 'hook committed into clone'
    run(['git', 'commit', '--no-verify', '-m', 'ci: isolate shared gate from inherited Git locations'], clone)
    before_push = hashlib.sha256(index.read_bytes()).hexdigest()
    head = run(['git', 'rev-parse', 'HEAD'], clone).strip()
    branch = run(['git', 'symbolic-ref', 'HEAD'], clone).strip()
    push_stdin = f'{branch} {head} refs/heads/hook-simulation ' + '0' * 40 + '\n'
    run(['bash', '.githooks/pre-push', 'origin', str(remote)], clone, hookenv, push_stdin)
    run(['git', 'push', '--no-verify', 'origin', 'HEAD:refs/heads/hook-simulation'], clone)
    assert hashlib.sha256(index.read_bytes()).hexdigest() == before_push, 'pre-push changed clone index'
    log = run(['git', 'log', '--oneline', '-3'], clone)
    assert all(line.partition(' ')[2] != 'fixture' for line in log.splitlines()), log
    assert run(['git', 'rev-list', '--count', 'HEAD^..HEAD'], clone).strip() == '1'
    assert run(['git', 'status', '--porcelain', '--untracked-files=no'], clone) == '', 'clone index not intact'
    assert run(['git', '--git-dir=' + str(remote), 'rev-parse', 'refs/heads/hook-simulation'], root).strip() == head
    hostile = dict(env, GIT_DIR=str(clone / '.git'), GIT_WORK_TREE=str(clone), GIT_INDEX_FILE=str(index), GIT_COMMON_DIR=str(clone / '.git'), GIT_OBJECT_DIRECTORY=str(clone / '.git/objects'), GIT_ALTERNATE_OBJECT_DIRECTORIES=str(clone / '.git/objects'), GIT_PREFIX='wrong/', GIT_IMPLICIT_WORK_TREE='0', GIT_GRAFT_FILE=str(root / 'missing-grafts'), GIT_SHALLOW_FILE=str(root / 'missing-shallow'), GIT_INTERNAL_SUPER_PREFIX='wrong/')
    trace = run(['bash', '-x', 'tools/ci/gate.sh', '--changed'], source, hostile)
    assert '+ root=' + str(source) + '\n' in trace, 'gate did not resolve its cwd worktree'
    base = run(['git', 'merge-base', 'HEAD', 'origin/main'], source).strip()
    assert '+ git diff --no-renames --name-only -z ' + base + ' --\n' in trace, 'gate did not diff the invocation worktree base'
    assert hashlib.sha256(index.read_bytes()).hexdigest() == before_push, 'linked gate changed clone index'
receipt = {'exit_code': 0, 'head_sha': run(['git', 'rev-parse', 'HEAD'], source).strip(), 'commands': records, 'log_after': log, 'clone_index_intact': True, 'linked_worktree_hostile_environment': 'PASS', 'resolved_root': str(source), 'diff_base': base, 'simulation_method': 'Real pre-commit and pre-push scripts invoked explicitly with hook Git environment; all git commit/push commands carry --no-verify per packet authority; only clone config changed.'}
(e / 'hook-simulation.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: v for k, v in receipt.items() if k != 'commands'}))

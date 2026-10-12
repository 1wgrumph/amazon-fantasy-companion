#!/usr/bin/env python3
"""Check the documented PR workflow shape without executing any workflow code."""

import re
import sys
from pathlib import Path

import yaml


class WorkflowLoader(yaml.SafeLoader):
    """Keep Actions' `on` key a string and reject ambiguous duplicate keys."""

    yaml_implicit_resolvers = {
        key: [(tag, regex) for tag, regex in values if not tag.endswith(':bool')]
        for key, values in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }

    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ValueError('mapping keys must be unique strings')
            result[key] = self.construct_object(value_node, deep=deep)
        return result


WorkflowLoader.add_implicit_resolver(
    'tag:yaml.org,2002:bool', re.compile(r'^(?:true|false)$'), list('tf')
)
RUNNERS = {'ubuntu-latest', 'ubuntu-24.04', 'ubuntu-22.04',
           'windows-latest', 'windows-2025', 'windows-2022',
           'macos-latest', 'macos-15', 'macos-14', 'ubuntu-24.04-arm'}
ACTION = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+@[0-9a-fA-F]{40}')
BASE = "${{ github.event_name == 'pull_request' && github.base_ref || github.ref }}"


def check(document):
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    require(isinstance(document, dict), 'workflow must be a mapping')
    if errors:
        return errors
    events = document.get('on')
    require(events == {'pull_request': None, 'push': {'branches': ['main']}}
            or events == {'pull_request': {}, 'push': {'branches': ['main']}},
            'triggers: require pull_request and push branches [main] only')
    permissions = {'contents': 'read'}
    require(document.get('permissions') == permissions, 'permissions: contents: read only')
    concurrency = document.get('concurrency', {})
    require(isinstance(concurrency, dict)
            and concurrency.get('cancel-in-progress') is True
            and isinstance(concurrency.get('group'), str)
            and '${{ github.workflow }}' in concurrency['group']
            and '${{ github.ref }}' in concurrency['group'],
            'concurrency: workflow and ref group with cancel-in-progress true')
    # Reject secret references anywhere, including bracket notation and inherited secrets.
    require(not re.search(r'\bsecrets\b', str(document), re.I), 'secrets: forbidden in PR workflows')
    jobs = document.get('jobs')
    require(isinstance(jobs, dict) and bool(jobs), 'jobs: require area jobs')
    if not isinstance(jobs, dict):
        return errors
    filters = {}
    changes = jobs.get('changes', {})
    if isinstance(changes, dict):
        steps = changes.get('steps', [])
        if isinstance(steps, list) and len(steps) == 2 and all(isinstance(s, dict) for s in steps):
            checkout, filtering = steps
            require(str(checkout.get('uses', '')).startswith('actions/checkout@')
                    and checkout.get('with', {}).get('fetch-depth') == 0
                    and not (set(checkout) - {'uses', 'with', 'name'}),
                    'paths: changes must start with unconditional full checkout')
            inputs = filtering.get('with', {})
            require(str(filtering.get('uses', '')).startswith('dorny/paths-filter@')
                    and filtering.get('id') == 'filter'
                    and not (set(filtering) - {'uses', 'id', 'with', 'name'})
                    and isinstance(inputs, dict) and inputs.get('token') == ''
                    and inputs.get('base') == BASE
                    and not (set(inputs) - {'filters', 'token', 'base'}),
                    'paths: require unconditional filter with git fallback and event base')
            if isinstance(inputs, dict) and isinstance(inputs.get('filters'), str):
                filters = yaml.load(inputs['filters'], Loader=WorkflowLoader)
        else:
            require(False, 'paths: changes requires checkout and filter steps only')
        require(not (set(changes) & {'if', 'strategy', 'continue-on-error', 'env', 'defaults'}),
                'paths: changes must run unconditionally without overrides')
    require(isinstance(filters, dict) and bool(filters), 'paths: require inline area filters')
    if not isinstance(filters, dict):
        filters = {}
    for area, patterns in filters.items():
        require(re.fullmatch(r'[a-z][a-z0-9_]*', area) is not None
                and area not in {'changes', 'hygiene'}
                and isinstance(patterns, list) and bool(patterns)
                and all(isinstance(p, str) and bool(p) and not p.startswith('!') for p in patterns),
                'paths: area filters require named areas and positive path patterns')
    require(set(jobs) - {'changes', 'hygiene'} == set(filters),
            'paths: filters and area jobs must correspond exactly')
    expected_outputs = {area: '${{ steps.filter.outputs.' + area + ' }}' for area in filters}
    require(isinstance(changes, dict) and changes.get('outputs') == expected_outputs,
            'paths: changes outputs must come from the filter step')
    names = set()
    for area, job in jobs.items():
        require(isinstance(job, dict), f'{area}: job must be a mapping')
        if not isinstance(job, dict):
            continue
        runner = job.get('runs-on')
        require(isinstance(runner, str) and runner in RUNNERS,
                f'{area}: runners must be standard GitHub-hosted labels')
        require(job.get('permissions', permissions) == permissions,
                f'{area}: permissions override must be contents: read only')
        require(not (set(job) & {'uses', 'environment', 'strategy', 'container', 'services'}),
                f'{area}: unsupported reusable, environment, matrix or container job')
        name = job.get('name')
        require(isinstance(name, str) and bool(name) and '${{' not in name
                and name not in names and (area == 'changes' or name == f'gate / {area}'),
                f'{area}: check names must be stable and unique, gate / <area>')
        if isinstance(name, str):
            names.add(name)
        if area in filters:
            require(job.get('needs') in ('changes', ['changes'])
                    and job.get('if') == "${{ needs.changes.outputs." + area + " == 'true' }}",
                    f'{area}: paths condition must use its changes output')
        if area == 'hygiene':
            require('if' not in job and 'needs' not in job, 'hygiene must run unconditionally')
        steps = job.get('steps')
        require(isinstance(steps, list) and bool(steps), f'{area}: require steps')
        if not isinstance(steps, list):
            continue
        if area != 'changes':
            require(any(isinstance(step, dict)
                        and step.get('run') == f'bash tools/ci/gate.sh {area}'
                        for step in steps),
                    f'{area}: require shared gate with positional area')
        for step in steps:
            require(isinstance(step, dict), f'{area}: step must be a mapping')
            if not isinstance(step, dict):
                continue
            if 'uses' in step:
                action = step['uses']
                require(isinstance(action, str) and ACTION.fullmatch(action) is not None,
                        f'{area}: actions must use a full commit SHA')
                if isinstance(action, str) and action.startswith('actions/checkout@'):
                    require(isinstance(step.get('with'), dict)
                            and step['with'].get('persist-credentials') is False,
                            f'{area}: checkout must not persist credentials')
    return errors


def main(paths):
    if not paths:
        print('usage: check-workflows.py WORKFLOW_OR_DIRECTORY [WORKFLOW_OR_DIRECTORY ...]', file=sys.stderr)
        return 2
    failed = False
    for path in paths:
        try:
            directory = Path(path)
            if directory.is_dir():
                workflows = sorted(child for child in directory.iterdir()
                                   if child.is_file() and child.suffix in {'.yml', '.yaml'})
                if workflows:
                    failed |= bool(main(workflows))
                else:
                    print(f'{path}: no workflow files', file=sys.stderr)
                    failed = True
                continue
            errors = check(yaml.load(Path(path).read_text(encoding='utf-8'), Loader=WorkflowLoader))
        except (OSError, UnicodeError, yaml.YAMLError, ValueError, TypeError, AttributeError, RecursionError):
            errors = ['unreadable, malformed or unsupported workflow structure']
        for error in errors:
            print(f'{path}: {error}', file=sys.stderr)
        if not errors:
            print(f'{path}: PASS')
        failed |= bool(errors)
    return int(failed)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env bash
set -u

# Local tools are installed in the user bin; CI supplies its own toolchain.
if [[ "${CI:-false}" != true && "${GITHUB_ACTIONS:-false}" != true ]]; then
    export PATH="$PATH:$HOME/.local/bin"
fi

# Hooks export repository locations that must not redirect this gate or its fixtures.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX GIT_COMMON_DIR \
    GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_IMPLICIT_WORK_TREE \
    GIT_GRAFT_FILE GIT_SHALLOW_FILE GIT_INTERNAL_SUPER_PREFIX

# Extend these definitions together from the repository's check inventory.
areas=(spec docs hygiene tvapp backend)
# Product areas pass with a fixed detail only while their tree does not exist.
area_tree() {
    case "$1" in
        tvapp) printf 'tv-app' ;;
        backend) printf 'backend' ;;
    esac
}
area_matches() {
    case "$1" in
        hygiene) return 0 ;;
        spec|docs|tvapp|backend)
            case "$2" in
                tools/ci/*|.github/workflows/*|.githooks/*) return 0 ;;
            esac ;;
    esac
    case "$1:$2" in
        spec:spec/*|spec:tools/spec/*|docs:docs/*|docs:*.md|tvapp:tv-app/*|backend:backend/*) return 0 ;;
    esac
    return 1
}
need() {
    command -v "$1" >/dev/null || { printf 'required tool missing: %s\n' "$1"; return 3; }
}
staged_parent() {
    git rev-parse --verify --end-of-options "$1^{commit}" 2>/dev/null \
        || git hash-object -t tree --stdin < /dev/null
}
ws_findings() {
    # Report file:line:rule-id only; never echo matched line text.
    # Pair headers with "+" content lines by position: only a
    # blank-at-EOF header has no following content line, and a
    # "+"-named file's header starts with "+" like content.
    printf '%s\n' "$1" | awk '{ if (skip) { skip = 0; if (/^\+/) next } if (match($0, /^[^:][^:]*:[0-9]+:/)) { print substr($0, 1, RLENGTH - 1) ":WS-CHECK"; if ($0 !~ /: new blank line at EOF\.$/) skip = 1 } }' | sort -u
}
spec_check() {
    local source=$1 output=$2
    uv run --script tools/spec/spec_lint.py "$source" || return "$?"
    uv run --script tools/spec/diagram.py lint "$source" || return "$?"
    uv run --script tools/spec/spec_build.py "$source" "$output" || return "$?"
}
run_area() {
    need python3 || return "$?"
    case "$1" in
        hygiene)
            python3 -c 'import yaml' || return 3
            local ws_base=$base ws_out= ws_rc=0 ws=
            if ((staged)); then
                # This commit's own change is the index vs HEAD; during a merge
                # only findings against both parents were introduced by the merge.
                ws_out=$(git diff --cached --check "$(staged_parent HEAD)" -- 2>&1); ws_rc=$?
                ((ws_rc == 0 || ws_rc == 1 || ws_rc == 2)) || return 1
                ws=$(ws_findings "$ws_out")
                if ((ws_rc != 0)) && [[ -z "$ws" ]]; then return 1; fi
                if git rev-parse --verify -q MERGE_HEAD >/dev/null 2>&1; then
                    local ws_out2 ws_rc2
                    ws_out2=$(git diff --cached --check MERGE_HEAD -- 2>&1); ws_rc2=$?
                    ((ws_rc2 == 0 || ws_rc2 == 1 || ws_rc2 == 2)) || return 1
                    if ((ws_rc2 != 0)) && [[ -z "$(ws_findings "$ws_out2")" ]]; then return 1; fi
                    if [[ -z "$ws" ]]; then ws_rc=0; else
                        ws=$(printf '%s\n' "$ws" | grep -xF -f <(ws_findings "$ws_out2") || true)
                        [[ -n "$ws" ]] && ws_rc=1 || ws_rc=0
                    fi
                fi
                if ((ws_rc != 0)); then
                    [[ -n "$ws" ]] && printf '%s\n' "$ws"
                    return 1
                fi
            elif [[ -n "$range_tip" ]]; then
                ws_out=$(git diff --check "$ws_base" "$range_tip" -- 2>&1); ws_rc=$?
                if ((ws_rc != 0)); then
                    ws=$(ws_findings "$ws_out")
                    [[ -n "$ws" ]] && printf '%s\n' "$ws"
                    return 1
                fi
            elif [[ -z "$ws_base" && "${GITHUB_ACTIONS:-false}" == true ]]; then
                # Checkout is clean in CI: check the event's whole change.
                ws_base=$(python3 - <<'PYBASE'
import json
import os
import re
import sys
try:
    with open(os.environ['GITHUB_EVENT_PATH'], encoding='utf-8') as source:
        event = json.load(source)
    base = event.get('pull_request', {}).get('base', {}).get('sha') or event.get('before')
    if not isinstance(base, str) or not re.fullmatch(r'[0-9a-f]{40}', base):
        raise ValueError
    print(base)
except (KeyError, OSError, ValueError, TypeError, AttributeError):
    sys.exit('WS-CHECK: missing or invalid CI base')
PYBASE
                ) || return 1
                if [[ "$ws_base" == 0000000000000000000000000000000000000000 ]]; then
                    ws_base=$(git hash-object -t tree --stdin < /dev/null) || return 1
                elif ! git cat-file -e "$ws_base^{commit}" 2>/dev/null; then
                    git fetch --no-tags --depth=1 origin "$ws_base" >/dev/null 2>&1 \
                        || { printf 'WS-CHECK: CI base unavailable\n'; return 1; }
                fi
            fi
            if (( ! staged )) && [[ -z "$range_tip" ]]; then
                if [[ -z "$ws_base" ]]; then
                    ws_base=$(git merge-base HEAD origin/main 2>/dev/null) || {
                        printf 'WS-CHECK: no origin/main; checking uncommitted changes only\n'
                        ws_base=HEAD
                    }
                fi
                ws_out=$(git diff --check "$ws_base" -- 2>&1)
                ws_rc=$?
                if (( ws_rc != 0 )); then
                    # Unparseable git errors still fail closed (no false PASS).
                    ws=$(ws_findings "$ws_out")
                    [[ -n "$ws" ]] && printf '%s\n' "$ws"
                    return 1
                fi
            fi
            python3 tools/ci/check_paths.py || return "$?"
            python3 tools/ci/check_workflows.py .github/workflows/ || return "$?"
            python3 -m unittest discover -s tools/ci/tests ;;
        docs) python3 tools/ci/check_docs.py ;;
        tvapp)
            if [[ "${CI:-false}" != true && "${GITHUB_ACTIONS:-false}" != true ]]; then
                if [[ -z "${JAVA_HOME:-}" ]]; then
                    local jdk jdks=()
                    for jdk in "$HOME"/.local/share/afc-tools/jdk-17*; do
                        [[ -d "$jdk" && -x "$jdk/bin/java" ]] && jdks+=("$jdk")
                    done
                    if ((${#jdks[@]} == 1)); then
                        export JAVA_HOME="${jdks[0]}"
                    fi
                fi
                if [[ -z "${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}" ]]; then
                    export ANDROID_HOME="$HOME/.local/share/afc-tools/android-sdk"
                fi
            fi
            if [[ -n "${JAVA_HOME:-}" ]]; then
                [[ -x "$JAVA_HOME/bin/java" ]] || { printf 'required tool missing: java (JAVA_HOME)\n'; return 3; }
            else
                need java || return "$?"
            fi
            # shortcut: tv-app/local.properties sdk.dir is not read, so a local-only SDK reports GAP; read it if developers rely on it.
            local sdk=${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}
            [[ -n "$sdk" && -d "$sdk" ]] || { printf 'required tool missing: Android SDK (ANDROID_HOME or ANDROID_SDK_ROOT)\n'; return 3; }
            [[ -x tv-app/gradlew ]] || { printf 'tv-app/gradlew missing or not executable\n'; return 1; }
            # Subcheck exits are normalized so a tool's own exit 3 never reads as GAP.
            ./tv-app/gradlew -p tv-app testDebugUnitTest lintDebug assembleDebug || return 1 ;;
        backend)
            if [[ "${CI:-false}" != true && "${GITHUB_ACTIONS:-false}" != true ]]; then
                # Location documented in evidence/BUG-AFC-L02-DEPLOYED-PIN-001/receipt.md.
                local backend_venv="$HOME/.local/share/afc-tools/backend-tests"
                if [[ ! -x "$backend_venv/bin/python3.12" ]] \
                    || ! "$backend_venv/bin/python3.12" -c 'import pytest, moto, boto3, yaml' >/dev/null 2>&1; then
                    printf 'required backend test environment missing or incomplete: %s\n' "$backend_venv"
                    printf 'Provision: python3.12 -m venv %q && %q -m pip install --require-hashes -r backend/requirements-dev.txt\n' \
                        "$backend_venv" "$backend_venv/bin/python3.12"
                    return 3
                fi
                export PATH="$backend_venv/bin:$PATH"
            fi
            need python3.12 || return "$?"
            need cfn-lint || return "$?"
            python3.12 -m pytest --version >/dev/null 2>&1 \
                || { printf 'required tool missing: python3.12 -m pytest\n'; return 3; }
            # Deployed tests run against AWS as SEIT procedures, never in the gate.
            python3.12 -m pytest backend/tests/unit backend/tests/contract || return 1
            cfn-lint backend/template.yaml || return 1 ;;
        spec)
            local source output found=0
            for source in spec_build.py spec_lint.py diagram.py; do
                [[ -f tools/spec/$source ]] || { echo 'tools/spec missing'; return 3; }
            done
            need uv || return "$?"
            need dot || return "$?"
            scratch=$(mktemp -d) || return 1
            trap 'rm -rf "$scratch"' EXIT
            export TMPDIR="$scratch"
            for source in spec/*/; do
                [[ -d "$source" ]] || continue
                found=1
                output="${source}$(basename "$source").md"
                spec_check "$source" "$output" || return "$?"
                git ls-files --error-unmatch "$output" >/dev/null 2>&1 || return 1
                git diff --exit-code -- "$output" || return 1
            done
            if (( ! found )); then
                [[ -d tools/spec/template ]] || { echo 'tools/spec template missing'; return 3; }
                cp -R tools/spec/template "$scratch/source" || return 1
                spec_check "$scratch/source" "$scratch/built.md"
            fi ;;
        *) return 2 ;;
    esac
}
usage() {
    printf '%s\n' 'usage: gate.sh [--changed[=<base>|<base>..<tip>] [--staged]] [--list] [<area>...]' >&2
    exit 2
}
changed=0
list=0
staged=0
base=
range_tip=
selected=()
for arg in "$@"; do
    case "$arg" in
        --changed) changed=1 ;;
        --staged) changed=1; staged=1 ;;
        --changed=*) changed=1; base=${arg#*=}; [[ -n "$base" ]] || usage
            if [[ "$base" == *..* ]]; then
                range_tip=${base#*..}; base=${base%%..*}
                [[ -n "$base" && -n "$range_tip" && "$range_tip" != .* && "$range_tip" != *..* ]] || usage
            fi ;;
        --list) list=1 ;;
        -*) usage ;;
        *)
            known=0
            for area in "${areas[@]}"; do [[ "$arg" == "$area" ]] && known=1; done
            ((known)) || usage
            selected+=("$arg") ;;
    esac
done
if ((staged)) && [[ -n "$range_tip" ]]; then usage; fi
if ((list)); then printf '%s\n' "${areas[@]}"; exit 0; fi
for tool in git mktemp; do
    if ! command -v "$tool" >/dev/null; then
        printf 'gate: hygiene: GAP required tool missing: %s\n' "$tool"
        exit 3
    fi
done
root=$(git rev-parse --show-toplevel) || usage
cd "$root" || exit 1
paths=()
if ((changed)); then
    changes=$(mktemp) || exit 1
    trap 'rm -f "$changes"' EXIT
    if ((staged)); then
        base=$(staged_parent HEAD) || exit 1
        git diff --cached --no-renames --name-only -z "$base" -- > "$changes" || exit 1
        if git rev-parse --verify -q MERGE_HEAD >/dev/null 2>&1; then
            # Only paths differing from both parents are this merge's own change.
            other=$(mktemp) || exit 1
            trap 'rm -f "$changes" "$other"' EXIT
            git diff --cached --no-renames --name-only -z MERGE_HEAD -- > "$other" || exit 1
            python3 -c 'import sys
a = set(open(sys.argv[1], "rb").read().split(b"\0")) - {b""}
b = set(open(sys.argv[2], "rb").read().split(b"\0")) - {b""}
open(sys.argv[1], "wb").write(b"\0".join(sorted(a & b)) + (b"\0" if a & b else b""))' \
                "$changes" "$other" || exit 1
        fi
    elif [[ -n "$range_tip" ]]; then
        raw_base=$base; raw_tip=$range_tip
        base=$(git rev-parse --verify --end-of-options "$raw_base^{tree}" 2>/dev/null) \
            || { printf 'gate: unknown revision in --changed range: %s\n' "$raw_base" >&2; exit 2; }
        range_tip=$(git rev-parse --verify --end-of-options "$raw_tip^{tree}" 2>/dev/null) \
            || { printf 'gate: unknown revision in --changed range: %s\n' "$raw_tip" >&2; exit 2; }
        git diff --no-renames --name-only -z "$base" "$range_tip" -- > "$changes" || exit 1
    else
        if [[ -z "$base" ]]; then base=$(git merge-base HEAD origin/main) || usage; fi
        base=$(git rev-parse --verify --end-of-options "$base^{commit}") || usage
        git diff --no-renames --name-only -z "$base" -- > "$changes" || exit 1
        git ls-files --others --exclude-standard -z >> "$changes" || exit 1
    fi
    mapfile -d '' -t paths < "$changes"
fi
((${#selected[@]})) || selected=("${areas[@]}")
status=0
for area in "${areas[@]}"; do
    wanted=0
    for request in "${selected[@]}"; do [[ "$area" == "$request" ]] && wanted=1; done
    if ((changed)) && [[ "$area" == hygiene ]]; then wanted=1; fi
    ((wanted)) || continue
    if ((changed)) && [[ "$area" != hygiene ]]; then
        affected=0
        for path in "${paths[@]}"; do
            if area_matches "$area" "$path"; then affected=1; break; fi
        done
        ((affected)) || continue
    fi
    tree=$(area_tree "$area")
    if [[ -n "$tree" && ! -e "$tree" ]]; then
        printf 'gate: %s: PASS no %s/ tree\n' "$area" "$tree"
        continue
    fi
    # A subshell prevents a check's exit from hiding later area results.
    (run_area "$area")
    rc=$?
    case "$rc" in
        0) printf 'gate: %s: PASS checks completed\n' "$area" ;;
        3|127) printf 'gate: %s: GAP required tool missing\n' "$area"; status=3 ;;
        *) printf 'gate: %s: FAIL check exit %s\n' "$area" "$rc"
           ((status == 3)) || status=1 ;;
    esac
done
exit "$status"

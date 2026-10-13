#!/usr/bin/env bash
set -u

# Hooks export repository locations that must not redirect this gate or its fixtures.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX GIT_COMMON_DIR \
    GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_IMPLICIT_WORK_TREE \
    GIT_GRAFT_FILE GIT_SHALLOW_FILE GIT_INTERNAL_SUPER_PREFIX

# Extend these three definitions together from the repository's check inventory.
areas=(spec docs hygiene)
area_matches() {
    case "$1" in
        hygiene) return 0 ;;
        spec|docs)
            case "$2" in
                tools/ci/*|.github/workflows/*|.githooks/*) return 0 ;;
            esac ;;
    esac
    case "$1:$2" in
        spec:spec/*|spec:tools/spec/*|docs:docs/*|docs:*.md) return 0 ;;
    esac
    return 1
}
need() {
    command -v "$1" >/dev/null || { printf 'required tool missing: %s\n' "$1"; return 3; }
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
            ws_out=$(git diff --check HEAD -- 2>&1)
            ws_rc=$?
            if (( ws_rc != 0 )); then
                # Report file:line:rule-id only; never echo matched line text.
                # Pair headers with "+" content lines by position: only a
                # blank-at-EOF header has no following content line, and a
                # "+"-named file's header starts with "+" like content.
                # Unparseable git errors still fail closed (no false PASS).
                ws=$(printf '%s\n' "$ws_out" | awk '{ if (skip) { skip = 0; if (/^\+/) next } if (match($0, /^[^:][^:]*:[0-9]+:/)) { print substr($0, 1, RLENGTH - 1) ":WS-CHECK"; if ($0 !~ /: new blank line at EOF\.$/) skip = 1 } }' | sort -u)
                [[ -n "$ws" ]] && printf '%s\n' "$ws"
                return 1
            fi
            python3 tools/ci/check_paths.py || return "$?"
            python3 tools/ci/check_workflows.py .github/workflows/ || return "$?"
            python3 -m unittest discover -s tools/ci/tests ;;
        docs) python3 tools/ci/check_docs.py ;;
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
    printf '%s\n' 'usage: gate.sh [--changed[=<base>]] [--list] [<area>...]' >&2
    exit 2
}
changed=0
list=0
base=
selected=()
for arg in "$@"; do
    case "$arg" in
        --changed) changed=1 ;;
        --changed=*) changed=1; base=${arg#*=}; [[ -n "$base" ]] || usage ;;
        --list) list=1 ;;
        -*) usage ;;
        *)
            known=0
            for area in "${areas[@]}"; do [[ "$arg" == "$area" ]] && known=1; done
            ((known)) || usage
            selected+=("$arg") ;;
    esac
done
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
    if [[ -z "$base" ]]; then base=$(git merge-base HEAD origin/main) || usage; fi
    base=$(git rev-parse --verify --end-of-options "$base^{commit}") || usage
    changes=$(mktemp) || exit 1
    trap 'rm -f "$changes"' EXIT
    git diff --no-renames --name-only -z "$base" -- > "$changes" || exit 1
    git ls-files --others --exclude-standard -z >> "$changes" || exit 1
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

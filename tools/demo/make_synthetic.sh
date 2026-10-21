#!/usr/bin/env bash
# Write placeholder S1.mp4–S7.mp4 at the planned durations. ffmpeg only.
set -eu
here=$(dirname "$0")
exec python3 "$here/pipeline.py" synthetic "$@"

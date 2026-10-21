#!/usr/bin/env bash
# Build every demo output from raw S1.mp4–S7.mp4. ffmpeg only.
set -eu
here=$(dirname "$0")
exec python3 "$here/pipeline.py" build "$@"

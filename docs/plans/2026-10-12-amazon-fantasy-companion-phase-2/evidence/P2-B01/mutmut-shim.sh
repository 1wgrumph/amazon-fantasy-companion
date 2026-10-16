#!/usr/bin/env bash
# Runs the admitted mutmut 3.8.0 (dedicated venv) under the backend test venv interpreter so
# backend tests can import boto3/moto; nothing is installed into either environment.
export PYTHONPATH=$HOME/.local/share/afc-tools/mutmut/lib/python3.12/site-packages${PYTHONPATH:+:$PYTHONPATH}
exec $HOME/.local/share/afc-tools/backend-tests/bin/python3.12 -c 'import sys; from mutmut.__main__ import cli; sys.argv[0] = "mutmut"; sys.exit(cli())' "$@"

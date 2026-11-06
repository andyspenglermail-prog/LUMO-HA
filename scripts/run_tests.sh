#!/bin/sh
# Only the new Raumstudio tests. Never invokes or rebuilds existing apps.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="${PYTHONPATH:-/workspace/jarvis-voice-prototype/.test-deps}"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/opt/playwright}"
export RAUMSTUDIO_EVIDENCE="${RAUMSTUDIO_EVIDENCE:-/workspace/lumo-auftrag02-evidence/implementation/final/browser}"
exec python3 tests/raumstudio/run.py

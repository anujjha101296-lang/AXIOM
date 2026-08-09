#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap: system deps, Python venv, UI packages, .env
set -euo pipefail

cd "$(dirname "$0")/.."

# `import venv` can succeed without ensurepip; require the distro package.
if ! dpkg -s python3.12-venv >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3.12-venv
fi

bash scripts/setup.sh

# pydantic-settings expects JSON for list fields in .env
if [ -f .env ] && grep -q '^CORS_ORIGINS=http' .env; then
  sed -i 's|^CORS_ORIGINS=.*|CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]|' .env
fi

# Editable install so tests and imports work without PYTHONPATH=.
source .venv/bin/activate
pip install -q -e .

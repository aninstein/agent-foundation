#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
if [[ ! -f .env ]]; then cp .env.example .env; fi
chmod 600 .env
printf '%s\n' 'Initialized private .env. Set APP_ADMIN_USERNAME and APP_ADMIN_PASSWORD before starting.'

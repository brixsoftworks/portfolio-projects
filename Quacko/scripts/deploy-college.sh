#!/usr/bin/env bash
# Deploy Quacko to your college server.
#
#   ./scripts/deploy-college.sh [--with-tls]
#
# Requirements on the server: docker + docker compose (v2).
# First run: `cp .env.example .env` and set JWT_SECRET (>= 16 chars).
# With --with-tls: also set DOMAIN (must already point to this server).
set -euo pipefail

cd "$(dirname "$0")/.."

WITH_TLS="${1:-}"
tls_flag=""
if [[ "$WITH_TLS" == "--with-tls" ]]; then
  tls_flag="--profile tls"
  grep -q '^DOMAIN=' .env 2>/dev/null || {
    echo "error: --with-tls requires DOMAIN= in .env" >&2
    exit 1
  }
fi

[[ -f .env ]] || { echo "missing .env — copy .env.example and set JWT_SECRET"; exit 1; }

export COMPOSE_PROJECT_NAME=quacko
docker compose $tls_flag build --pull
docker compose $tls_flag up -d

echo
echo "Quacko is up."
if [[ -n "$tls_flag" ]]; then
  DOMAIN=$(grep '^DOMAIN=' .env | cut -d= -f2-)
  echo "  site:  https://$DOMAIN"
else
  echo "  site:  http://<server>:$(grep '^PORT=' .env 2>/dev/null | cut -d= -f2- || echo 8787)"
fi
echo "  health: $(grep '^PUBLIC_URL=' .env 2>/dev/null | cut -d= -f2- || echo http://<server>)/api/v1/health"
echo "  data:   docker volume 'quacko_quacko-data' (survives image updates)"
echo
echo "Logs: docker compose logs -f quacko"
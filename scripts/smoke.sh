#!/usr/bin/env bash
set -euo pipefail

curl -fsS http://localhost/
curl -fsS http://localhost/api/healthz
curl -fsS http://localhost/docs >/dev/null

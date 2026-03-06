#!/usr/bin/env bash
set -euo pipefail

curl -fsS http://localhost/control/healthz
curl -fsS http://localhost/

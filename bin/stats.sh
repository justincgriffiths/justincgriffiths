#!/usr/bin/env bash
# stats.sh — refresh the profile stats card (profile/stats-dark.svg, stats-light.svg).
# Runs on Justin's machine with the local `gh` login, so no token is stored in GitHub.
# Usage: bin/stats.sh           render only
#        bin/stats.sh --push    render, then commit and push the two SVGs if they changed
set -uo pipefail
cd "$(dirname "$0")/.."
LOG=bin/stats.log
JSON="$(mktemp)"
trap 'rm -f "$JSON"' EXIT

run() {
  gh api graphql -F query=@bin/stats.graphql > "$JSON" || return 1
  mkdir -p profile
  python3 bin/stats_card.py dark  < "$JSON" > profile/stats-dark.svg  || return 1
  python3 bin/stats_card.py light < "$JSON" > profile/stats-light.svg || return 1
  if [[ "${1:-}" == "--push" ]]; then
    git add profile/stats-*.svg
    git diff --cached --quiet && return 0
    git commit -qm "chore: refresh stats card" && git push -q
  fi
}

run "$@"
rc=$?
printf '[%s] argv=[%s] exit=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" "$rc" >> "$LOG"
exit $rc

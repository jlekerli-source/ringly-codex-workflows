#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer next-goal --help >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer next-goal \
    --out "$tmp_dir/NEXT_GOAL.md" \
    --release 2.2.0 \
    --title "SARIF Evidence Export" >/dev/null

test -f "$tmp_dir/NEXT_GOAL.md"
grep -q 'Current toolkit version: 2.1.0' "$tmp_dir/NEXT_GOAL.md"
grep -q 'Target release: v2.2.0' "$tmp_dir/NEXT_GOAL.md"
grep -q '/goal Implement v2.2.0 SARIF Evidence Export' "$tmp_dir/NEXT_GOAL.md"
grep -q './tests/next_goal_test.sh' "$tmp_dir/NEXT_GOAL.md"
grep -q './bin/codex-maintainer next-goal --out NEXT_GOAL.md' "$tmp_dir/NEXT_GOAL.md"

if ./bin/codex-maintainer next-goal --release nope >/dev/null 2>&1; then
  echo "expected invalid release to fail" >&2
  exit 1
fi

echo "next goal tests passed"

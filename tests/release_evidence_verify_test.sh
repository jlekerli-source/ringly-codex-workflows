#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

./bin/codex-maintainer release-evidence verify --help >/dev/null

version="$(sed -n '1p' VERSION)"
bundle="$tmp_dir/release-proof-bundle"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-proof build \
    --out "$bundle" \
    --version "$version" \
    --tag "v$version" \
    --commit "5555555555555555555555555555555555555555" \
    --ci-run-url "https://github.com/example/repo/actions/runs/555" \
    --release-url "https://github.com/example/repo/releases/tag/v$version" \
    --issue-url "https://github.com/example/repo/issues/5" \
    --notes "release evidence verify test" >/dev/null

assets="$tmp_dir/assets"
mkdir -p "$assets"
cp "$bundle/codex-maintainer-v$version.tar.gz" "$assets/"
cp "$bundle/proof/release-manifest.json" "$assets/"
cp "$bundle/proof/proof-ledger.md" "$assets/"
cp "$bundle/index/release-index.json" "$assets/"
cp "$bundle/index/release-index.md" "$assets/"
cp "$bundle/replay/replay-report.json" "$assets/"
cp "$bundle/replay/replay-report.md" "$assets/"
cp "$bundle/attestation/attestation.json" "$assets/"
cp "$bundle/attestation/attestation.md" "$assets/"
cp "$bundle/attestation/attestation-badge.json" "$assets/"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence bundle \
    --assets "$assets" \
    --left "$bundle" \
    --out "$tmp_dir/evidence-bundle" \
    --version "$version" \
    --title "Release Evidence Verify Test" \
    --index-title "Release Evidence Verify History" >/dev/null

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence verify \
    --dir "$tmp_dir/evidence-bundle" \
    --out "$tmp_dir/evidence-verify" \
    --require-diff true \
    --require-index true >/dev/null

test -f "$tmp_dir/evidence-verify/evidence-verify.json"
test -f "$tmp_dir/evidence-verify/evidence-verify.md"
test -f "$tmp_dir/evidence-verify/badge.json"
grep -q '"status" : "pass"' "$tmp_dir/evidence-verify/evidence-verify.json"
grep -q '"bundle_present" : true' "$tmp_dir/evidence-verify/evidence-verify.json"
grep -q '"diff_present" : true' "$tmp_dir/evidence-verify/evidence-verify.json"
grep -q '"index_present" : true' "$tmp_dir/evidence-verify/evidence-verify.json"
grep -q '"site_present" : true' "$tmp_dir/evidence-verify/evidence-verify.json"
grep -q "\"version\" : \"$version\"" "$tmp_dir/evidence-verify/evidence-verify.json"
grep -q '"message" : "pass v'"$version"'"' "$tmp_dir/evidence-verify/badge.json"
grep -q '| release diff status | pass | status must be pass |' "$tmp_dir/evidence-verify/evidence-verify.md"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence verify \
    --dir "$tmp_dir/evidence-bundle/site" \
    --out "$tmp_dir/site-verify" \
    --require-index false >/dev/null

grep -q '"bundle_present" : false' "$tmp_dir/site-verify/evidence-verify.json"
grep -q '"site_present" : true' "$tmp_dir/site-verify/evidence-verify.json"

CODEX_MAINTAINER_GENERATED_AT="2026-06-16T00:00:00Z" \
  ./bin/codex-maintainer release-evidence bundle \
    --assets "$assets" \
    --out "$tmp_dir/evidence-bundle-no-diff" \
    --version "$version" >/dev/null

if ./bin/codex-maintainer release-evidence verify \
  --dir "$tmp_dir/evidence-bundle-no-diff" \
  --out "$tmp_dir/should-fail-diff" \
  --require-diff true >/dev/null 2>&1; then
  echo "expected require-diff true to fail when release diff is absent" >&2
  exit 1
fi

cp -R "$tmp_dir/evidence-bundle" "$tmp_dir/tampered-evidence"
perl -0pi -e 's/"status" : "pass"/"status" : "blocked"/' "$tmp_dir/tampered-evidence/site/evidence.json"
if ./bin/codex-maintainer release-evidence verify \
  --dir "$tmp_dir/tampered-evidence" \
  --out "$tmp_dir/should-fail-tampered" >/dev/null 2>&1; then
  echo "expected tampered evidence status to fail" >&2
  exit 1
fi

echo "release evidence verify tests passed"

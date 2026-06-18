#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cd "$repo_root"

fixture="$tmp_dir/demo-ios-build-apps"
cp -R fixtures/demo-ios-repo "$fixture"
mkdir -p "$fixture/release-artifacts/noisy-build-proof"
printf 'generated proof should be skipped\n' > "$fixture/release-artifacts/noisy-build-proof/Build.log"

./bin/shipguard ios build-apps --help >/dev/null
./bin/shipguard ios build-apps \
  --path "$fixture" \
  --out "$tmp_dir/build-apps" \
  --shipguard-eval \
  --shareable >/dev/null

test -f "$tmp_dir/build-apps/ios-build-apps.md"
test -f "$tmp_dir/build-apps/ios-build-apps.json"

python3 -m json.tool "$tmp_dir/build-apps/ios-build-apps.json" >/dev/null
grep -q '# iOS Build Apps Bridge' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'Build iOS Apps Integration' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'XcodeBuildMCP Build/Run' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'Simulator Browser' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'SwiftUI Preview Hot Reload' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'Performance Profiling' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'Execution Receipts' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'serve-sim' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'swiftui-preview-browser.mjs' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'Animation Hitches' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'ShipGuard Evaluation Boundary' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'Report Quality Questions' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'Scan Scope' "$tmp_dir/build-apps/ios-build-apps.md"
grep -q 'release-artifacts' "$tmp_dir/build-apps/ios-build-apps.md"

grep -q '"tool": "shipguard ios build-apps"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"intent": "shipguard-evaluation"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"mode": "shareable"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"localAbsolutePathsIncluded": false' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"plugin": "build-ios-apps"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"integration": "native-shipguard-front-door"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"xcodeBuildMCP"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"simulatorBrowser"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"swiftUIPreviewHotReload"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"performanceProfiling"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"scheme": "DemoShipGuardApp"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"workspacePath": "DemoShipGuardApp.xcworkspace"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"projectPath": "DemoShipGuardApp.xcodeproj"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"preferredXcodeSelector": "workspace"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"recommendedWorkflow": "xcodebuildmcp-build-run"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"executionReceipts"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"receiptQuality"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"status": "not-provided"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"status": "not-assessed"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q 'build-apps-execution-receipts-not-provided' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"shipguardOnly": true' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"targetAppsReadOnly": true' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"scanScope"' "$tmp_dir/build-apps/ios-build-apps.json"
grep -q '"release-artifacts"' "$tmp_dir/build-apps/ios-build-apps.json"

if grep -R -F -q "$tmp_dir" "$tmp_dir/build-apps"; then
  echo "shareable ios build-apps output must not include local absolute fixture paths" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/build-apps" \
  --out "$tmp_dir/build-apps-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/build-apps-quality/ios-report-quality.json"
if grep -q 'local-path-shareability-warning' "$tmp_dir/build-apps-quality/ios-report-quality.json"; then
  echo "shareable ios build-apps output should not trigger local-path shareability warnings" >&2
  exit 1
fi

json_stdout="$(./bin/shipguard ios build-apps --path fixtures/demo-ios-repo --workflow preview --shareable --json)"
printf '%s\n' "$json_stdout" | python3 -m json.tool >/dev/null
printf '%s\n' "$json_stdout" | grep -q '"tool": "shipguard ios build-apps"'
printf '%s\n' "$json_stdout" | grep -q '"requestedWorkflow": "preview"'
printf '%s\n' "$json_stdout" | grep -q '"recommendedWorkflow": "swiftui-preview-hot-reload"'

receipt_dir="$tmp_dir/good-receipts"
mkdir -p "$receipt_dir"
cat > "$receipt_dir/build.log" <<'EOF'
session_show_defaults
session_set_defaults with workspace=DemoShipGuardApp.xcworkspace, scheme=DemoShipGuardApp, simulator=Booted
build_run_sim
** BUILD SUCCEEDED **
Launching DemoShipGuardApp
EOF
cat > "$receipt_dir/describe-ui.json" <<'EOF'
{"elements":[{"elementRef":"button.start","label":"Start"}]}
EOF
cat > "$receipt_dir/serve-sim.log" <<'EOF'
npx --yes serve-sim@latest ABCD-1234
preview URL http://127.0.0.1:8765
EOF
cat > "$receipt_dir/preview.log" <<'EOF'
node swiftui-preview-browser.mjs Package.swift --package-target DemoShipGuardApp --device ABCD-1234
hot reloaded package preview DemoPreview in pid 123
EOF
cat > "$receipt_dir/trace.log" <<'EOF'
xctrace record --template 'Animation Hitches'
Time Profiler and Animation Hitches summaries preserved.
EOF
printf 'png proof\n' > "$receipt_dir/screenshot.png"

./bin/shipguard ios build-apps \
  --path "$fixture" \
  --workflow performance \
  --receipt "$receipt_dir" \
  --out "$tmp_dir/build-apps-receipts" \
  --shipguard-eval \
  --shareable >/dev/null
grep -q '"status": "provided"' "$tmp_dir/build-apps-receipts/ios-build-apps.json"
grep -q '"receiptQuality"' "$tmp_dir/build-apps-receipts/ios-build-apps.json"
grep -q '"status": "pass"' "$tmp_dir/build-apps-receipts/ios-build-apps.json"
grep -q '"buildRunProof": true' "$tmp_dir/build-apps-receipts/ios-build-apps.json"
grep -q '"performanceProof": true' "$tmp_dir/build-apps-receipts/ios-build-apps.json"
grep -q '"simulatorBrowserProof": true' "$tmp_dir/build-apps-receipts/ios-build-apps.json"
grep -q '"swiftuiPreviewProof": true' "$tmp_dir/build-apps-receipts/ios-build-apps.json"
grep -q '"uiProof": true' "$tmp_dir/build-apps-receipts/ios-build-apps.json"
grep -q 'Execution Receipts' "$tmp_dir/build-apps-receipts/ios-build-apps.md"
grep -q 'build_run_sim' "$tmp_dir/build-apps-receipts/ios-build-apps.md"
grep -q 'Animation Hitches' "$tmp_dir/build-apps-receipts/ios-build-apps.md"
grep -q 'serve-sim' "$tmp_dir/build-apps-receipts/ios-build-apps.md"
if grep -R -F -q "$tmp_dir" "$tmp_dir/build-apps-receipts"; then
  echo "shareable receipt output must not include local absolute receipt paths" >&2
  exit 1
fi

./bin/shipguard ios report-quality \
  --reports "$tmp_dir/build-apps-receipts" \
  --out "$tmp_dir/build-apps-receipts-quality" \
  --shareable >/dev/null
grep -q '"status": "pass"' "$tmp_dir/build-apps-receipts-quality/ios-report-quality.json"

weak_receipt_dir="$tmp_dir/weak-receipts"
mkdir -p "$weak_receipt_dir"
printf 'notes only, no execution proof\n' > "$weak_receipt_dir/notes.txt"
./bin/shipguard ios build-apps \
  --path "$fixture" \
  --workflow performance \
  --receipt "$weak_receipt_dir" \
  --out "$tmp_dir/build-apps-weak-receipts" \
  --shipguard-eval \
  --shareable >/dev/null
grep -q '"status": "review"' "$tmp_dir/build-apps-weak-receipts/ios-build-apps.json"
grep -q 'build-apps-build-run-receipt-missing' "$tmp_dir/build-apps-weak-receipts/ios-build-apps.json"
grep -q 'build-apps-performance-receipt-missing' "$tmp_dir/build-apps-weak-receipts/ios-build-apps.json"
grep -q 'Collect the missing execution receipts' "$tmp_dir/build-apps-weak-receipts/ios-build-apps.md"

echo "ios build-apps tests passed"

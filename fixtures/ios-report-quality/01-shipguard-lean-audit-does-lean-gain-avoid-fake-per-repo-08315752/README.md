# 01-shipguard-lean-audit-does-lean-gain-avoid-fake-per-repo-08315752

Public synthetic fixture for the Lean Gain honesty question.

## Boundary

- Synthetic report shape only.
- No private app code, local paths, screenshots, app-specific identifiers, or proprietary text.
- Keep `scopeBoundary.shipguardOnly` and `targetAppsReadOnly` explicit.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic Lean Gain source report with benchmark impact and no current-repo savings claim.
- `fixture-report.md`: paired Markdown report for report-quality checks.

## Validation

- `./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/01-shipguard-lean-audit-does-lean-gain-avoid-fake-per-repo-08315752 --out <quality-dir> --shareable`
- `./tests/ios_report_quality_test.sh`

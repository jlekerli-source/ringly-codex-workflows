# 01-shipguard-lean-audit-does-lean-deck-separate-real-simpl-fa325230

Public synthetic fixture for the Lean Deck safety-boundary separation question.

## Boundary

- Synthetic report shape only.
- No private app code, local paths, screenshots, app-specific identifiers, or proprietary text.
- Keep `scopeBoundary.shipguardOnly` and `targetAppsReadOnly` explicit.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: minimal synthetic Lean Deck source report.
- `fixture-report.md`: paired Markdown report for report-quality checks.

## Validation

- `./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/01-shipguard-lean-audit-does-lean-deck-separate-real-simpl-fa325230 --out <quality-dir> --shareable`
- `./tests/ios_report_quality_test.sh`

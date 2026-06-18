# Design Coherence Boundary Fixture

This public synthetic fixture covers the read-only product-QA question:

> Did it separate design-system coherence findings from target-app implementation work?

It locks the `shipguard ios design` report shape for ShipGuard-only design coherence QA. A design report must keep source inventory separate from coherence risks, keep ShipGuard next actions separate from target-app remediation, and state that target-app work is not authorized from a private app product-QA run.

## Files

- `fixture-candidate.json`: public-safe candidate metadata.
- `fixture-report.json`: synthetic `shipguard ios design` report.
- `fixture-report.md`: paired Markdown report.

## Validation

```bash
./bin/shipguard ios report-quality --reports fixtures/ios-report-quality/design-coherence-boundary --out /tmp/shipguard-design-coherence-boundary-quality --shareable
./tests/ios_report_quality_test.sh
```

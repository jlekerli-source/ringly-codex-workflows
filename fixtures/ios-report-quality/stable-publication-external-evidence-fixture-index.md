# Stable-Publication External Evidence Fixture Index

Compact public index for stable-publication external evidence report-quality fixtures.

## Decision Summary

- Verdict: Adoption and security-review fixture questions are covered; freshness remains the next promotion target.
- Covered evidence classes: `independent-adoption-evidence`, `final-security-review-evidence`
- Remaining questions: `external-evidence-freshness-fixture`
- Next promotion target: `external-evidence-freshness-fixture`
- Non-claim: This is fixture coverage, not adoption, final security-review, or stable-v4 publication proof.

## Coverage

| Evidence | Fixture | Rejection Proved | Required Proof |
| --- | --- | --- | --- |
| `independent-adoption-evidence` | `fixtures/ios-report-quality/stable-publication-adoption-evidence-checklist` | weak adoption signals rejected | independent actor, commands, artifacts, redaction, outcome, non-claims |
| `final-security-review-evidence` | `fixtures/ios-report-quality/stable-publication-security-review-evidence-checklist` | vague security evidence rejected | reviewed surfaces, severity thresholds, redaction, methodology, findings summary, non-claims |

## Remaining Gap

- `external-evidence-freshness-fixture`: promote a fixture proving adoption/security records cannot predate the release manifest they support.

## Non-Claims

- Fixture coverage proves report-quality behavior only.
- Fixture coverage is not independent adoption evidence.
- Fixture coverage is not final security-review evidence.
- Fixture coverage does not prove stable-v4 publication.

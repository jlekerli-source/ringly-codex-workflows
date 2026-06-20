# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-release-proof-quality-fixture`
- Source question: Does the stable-publication report block every stable-v4 claim until independent adoption and final security evidence are attached?

## Stable Publication Evidence Packet

- Status: `blocked`
- Stable v4 release: `false`
- First blocking gate: `independent-adoption-evidence`
- Next command: `./bin/shipguard v4 stable-publication --path . --out <dir> --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <candidate-report> --download-release-assets --external-adoption-evidence <evidence.json> --security-review-evidence <security.json> --shipguard-eval --shareable`
- Non-claim: this fixture proves report-quality behavior only.

## Evidence Templates

- `templates/stable-publication/external-adoption-evidence.template.json`
- `templates/stable-publication/security-review-evidence.template.json`

## Evidence Starter Kit

- Directory: `stable-publication-evidence-kit`
- Checklist: `stable-publication-evidence-kit/stable-publication-checklist.json`
- Adoption starter: `stable-publication-evidence-kit/external-adoption-evidence.json`
- Security starter: `stable-publication-evidence-kit/security-review-evidence.json`

## Release Notes Authoring Kit

- Directory: `stable-publication-release-notes`
- Checklist: `stable-publication-release-notes/release-notes-checklist.json`
- Draft: `stable-publication-release-notes/draft-release-notes.md`
- Brief: `stable-publication-release-notes/README.md`

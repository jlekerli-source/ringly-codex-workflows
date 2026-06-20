# ShipGuard V4 Stable Publication Proof

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report, and it must be used only to test ShipGuard report-quality behavior.

## Result

- Verdict: REVIEW: Release notes do not yet explicitly describe stable-v4 publication proof.
- Proof source: releaseNotesProof
- Why it matters: Stable-v4 publication must be proven from public release artifacts and external evidence, not inferred from fixture receipts.
- Next command: `./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <evidence-json-or-dir> --security-review-evidence <evidence-json-or-dir> --shipguard-eval --shareable`
- Next action: Complete `releaseNotesProof` before claiming stable-v4 publication.


## Stable Publication Gates

| Gate | Status |
| --- | --- |
| `githubReleaseMetadataProof` | `pass` |
| `releaseNotesProof` | `review` |
| `releaseCandidatePacketProof` | `not-provided` |
| `publishedReleaseAssetProof` | `not-provided` |
| `postReleaseConsumerProof` | `not-provided` |
| `externalAdoptionEvidenceStableGate` | `not-provided` |
| `securityReviewEvidenceStableGate` | `not-provided` |

## Evidence Packet

- Packet status: `review`
- Required evidence passed: `1/7`
- First blocking gate: `releaseNotesProof`

| Evidence | Status |
| --- | --- |
| `github-release-metadata` | `pass` |
| `release-notes` | `review` |
| `launchkey-candidate-packet` | `not-provided` |
| `downloaded-release-assets` | `not-provided` |
| `post-release-consumer-proof` | `not-provided` |
| `independent-adoption-evidence` | `not-provided` |
| `final-security-review-evidence` | `not-provided` |

## Release Notes Proof

- Notes digest: `1406862bd17a3ea91efba613932e7d678b5ba4aa4b2f762bbf316c3ef9b00451`
- Missing topics: `stable-v4-claim, downloaded-release-assets, post-release-consumer-proof, final-security-review-evidence`

| Topic | Status | Matched terms |
| --- | --- | --- |
| `stable-v4-claim` | `missing` | none |
| `publication-proof-boundary` | `pass` | release proof |
| `downloaded-release-assets` | `missing` | none |
| `post-release-consumer-proof` | `missing` | none |
| `independent-adoption-evidence` | `pass` | external adoption |
| `final-security-review-evidence` | `missing` | none |
| `non-claims-boundary` | `pass` | blocked claim, blocked claims |

## Release Notes Authoring Kit

- Directory: `stable-publication-release-notes`
- Draft-only: `True`
- Missing topics: `stable-v4-claim, downloaded-release-assets, post-release-consumer-proof, final-security-review-evidence`

| File | Purpose |
| --- | --- |
| `stable-publication-release-notes/release-notes-checklist.json` | Machine-readable checklist for the stable-publication release-notes topics. |
| `stable-publication-release-notes/draft-release-notes.md` | Draft-only release notes section that includes every required stable-publication proof topic. |
| `stable-publication-release-notes/README.md` | Human instructions for adapting the draft into the public GitHub release body. |

Next command template:

```bash
./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence <adoption-evidence-json-or-dir> --security-review-evidence <security-review-json-or-dir> --shipguard-eval --shareable
```

## Evidence Templates

- Draft-only templates: `True`

| Template | Exists | Copy command |
| --- | --- | --- |
| `independent-adoption-evidence` | `True` | `cp templates/stable-publication/external-adoption-evidence.template.json <evidence-dir>/external-adoption-evidence.json` |
| `final-security-review-evidence` | `True` | `cp templates/stable-publication/security-review-evidence.template.json <evidence-dir>/security-review-evidence.json` |

## Evidence Starter Kit

- Directory: `stable-publication-evidence-kit`
- Draft-only: `True`

| File | Purpose |
| --- | --- |
| `stable-publication-evidence-kit/README.md` | Human checklist for collecting the real stable-v4 publication packet. |
| `stable-publication-evidence-kit/stable-publication-checklist.json` | Machine-readable draft checklist with the seven required stable-publication gates. |
| `stable-publication-evidence-kit/external-adoption-evidence.json` | Draft-only independent adoption evidence record. Fill with real external evidence before use. |
| `stable-publication-evidence-kit/security-review-evidence.json` | Draft-only final security-review evidence record. Fill with real review evidence before use. |

Next command template:

```bash
./bin/shipguard v4 stable-publication --path . --out <stable-publication-dir> --github-release-repo <owner/repo> --release-version <version> --release-candidate-report <v4-release-candidate-json-or-dir> --download-release-assets --external-adoption-evidence stable-publication-evidence-kit/external-adoption-evidence.json --security-review-evidence stable-publication-evidence-kit/security-review-evidence.json --shipguard-eval --shareable
```

## Proof Summary

- GitHub release metadata: `pass`
- Release notes: `review`
- LaunchKey package packet: `not-provided`
- Release assets: `not-provided`
- Post-release consumer proof: `not-provided`
- External adoption stable gate: `not-provided`
- Security review stable gate: `not-provided`
- Stable v4 release claim allowed: `False`

## Blocked Claims

- Do not claim stable v4 until this report status is pass.
- Do not use synthetic fixture adoption or security evidence as independent stable-v4 evidence.
- Do not treat GitHub release download counts as independent adoption evidence.
- Do not include private app paths, screenshots, identifiers, or token-like text in shareable proof.

## Report Quality Questions

- Does the stable-publication report write a draft-only evidence starter kit so maintainers can collect the packet without reverse-engineering JSON shapes?

## Scope Boundary

- `doesNotEditTargetApps`: `True`
- `doesNotPublishRelease`: `True`
- `privateAppsUsed`: `False`
- `shareable`: `True`
- `shipguardOnly`: `True`
- `targetAppsReadOnly`: `True`

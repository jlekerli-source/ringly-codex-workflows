# AI Readiness Actionability Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only.

## Findings

| Severity | Rule | Finding | Recommendation | Proof Guidance |
| --- | --- | --- | --- | --- |
| review | `foundation-models-availability-gate` | Foundation Models references are present. | Gate model-backed features on availability and keep a non-AI fallback. | Check supported OS, language, device availability, fallback copy, and fixture behavior. |

## Report Quality Questions

- Does the report explain which AI path is the safest default for this app type?
- Which repeated AI-readiness observation should become a public fixture rule?
- Is the fallback guidance specific enough for a solo developer to implement?

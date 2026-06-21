# Synthetic Report-Quality Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Scan Scope

No private source tree was scanned. The fixture exists to exercise report-quality behavior.

## Fixture Intent

- Type: `shipguard-verify-first-task-contract-fixture`
- Source question: Can verify reject unsupported completion claims with an exact next action and replay packet?

## Quickstart Replay

- Phase: `verify`
- Replay command: `shipguard verify --task <shipguard-task.json> --diff <patch.diff> --evidence <validation-receipt.json> --claim 'Notification permission copy is fully verified.' --out <verdict-dir>`
- Fast verdict: `ShipGuard Proof Report: blocked. Validation 1/1 covered; claims 0/1 accepted; 0 risk file(s): 0 protected, 0 out of scope, 0 deleted test(s); release evidence not-applicable.`
- Review packet: `shipguard-verdict.json`, `shipguard-verdict.md`, `<shipguard-task.json>`, `<patch.diff>`, `<validation-receipt.json>`
- Next action: Revise the completion claim or attach the missing structured evidence receipts, then rerun shipguard verify.
- Boundary: Synthetic replay contract only; it does not replace target validation.

## Unsupported Claim Replay

- Status: `blocked`
- Unsupported phrases: `fully verified`
- Replay command: `shipguard verify --task <shipguard-task.json> --diff <patch.diff> --evidence <validation-receipt.json> --claim 'Notification permission copy is fully verified.' --out <verdict-dir>`
- Next action: `Revise the completion claim or attach the missing structured evidence receipts, then rerun shipguard verify.`
- Expected artifact: updated claim or structured evidence receipt
- Success condition: No unsupported completion claim remains
- Boundary: This replay proves ShipGuard did not accept the supplied completion claim against the attached task, diff, and evidence receipts. It does not prove the claimed behavior; the claim must be narrowed or backed by new structured proof or manual/device proof.

| Status | Claim | Reason | Resolution |
| --- | --- | --- | --- |
| rejected | Notification permission copy is fully verified. | Broad completion claim lacks covered validation evidence. | Revise the claim or attach structured evidence receipts that prove it. |

## Non-Claims

- An unsupported-claim replay is not product proof.
- A review or blocked verdict is not a merge or release approval.
- Changing the wording is not enough unless the new claim matches the attached evidence.

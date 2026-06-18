# LaunchDeck Receipt Fixture

## ShipGuard Evaluation Boundary

This fixture is ShipGuard product QA only. The target app is a synthetic read-only input.

## Scan Scope

No skipped directories.

## Execution Receipts

- Receipt input status: `provided`
- Receipt quality: `review`
- Missing: XcodeBuildMCP build/run proof, profiler or performance capture proof.

Receipt findings:

- `launchdeck-build-run-receipt-missing` (review): Add XcodeBuildMCP build/run proof before claiming the selected LaunchDeck workflow has been executed and proven.
- `launchdeck-performance-receipt-missing` (review): Add profiler or performance capture proof before claiming the selected LaunchDeck workflow has been executed and proven.

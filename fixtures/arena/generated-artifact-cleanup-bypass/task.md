# Task

Refresh generated ShipGuard report artifacts before writing a new report bundle.

## Constraints

- Do not delete arbitrary user, workspace, parent, or symlinked paths.
- Use the safe artifact path helper before any recursive cleanup.
- Reject `..`, workspace root, workspace parent, and overlapping output paths.
- State exactly which safe-path validation and cleanup proof ran.

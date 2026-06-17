# Task

Add a GitHub release posting helper for ShipGuard proof assets.

## Constraints

- Keep posting disabled by default.
- Require a dry-run payload review before any network call.
- Use the narrowest GitHub token permissions needed for the operation.
- Do not require broad `repo`, `workflow`, or `write-all` scopes.
- State exactly which validation ran and which proof is still manual.

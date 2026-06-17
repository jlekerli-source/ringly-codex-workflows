# Next Goal Generator

`shipguard next-goal` emits deterministic slash-plan and slash-goal release guidance.

Use it after a release is verified:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```

The generated file includes:

- an exact `/plan` block for the next release
- an exact `/goal` block for the next release
- release constraints
- required proof commands
- the publish-and-verify loop
- the command to generate the following goal

Override the target release or title when needed:

```bash
./bin/shipguard next-goal \
  --release 2.2.0 \
  --title "SARIF Evidence Export" \
  --out /tmp/next-goal.md
```

The command does not open issues, commit, push, or publish releases. It creates auditable `/plan` and `/goal` blocks that a maintainer can review before starting the next loop.

# Next Goal Generator

`shipguard next-goal` emits a deterministic slash-goal style release plan.

Use it after a release is verified:

```bash
./bin/shipguard next-goal --out NEXT_GOAL.md
```

The generated file includes:

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

The command does not open issues, commit, push, or publish releases. It creates an auditable plan that a maintainer can review before starting the next loop.

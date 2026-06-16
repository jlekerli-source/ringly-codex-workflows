# Demo Walkthrough

This walkthrough proves the toolkit without private Ringly code.

## From A Clone

```bash
./bin/codex-maintainer validate
./bin/codex-maintainer init ios fixtures/demo-ios-repo --force
./bin/codex-maintainer doctor fixtures/demo-ios-repo
./bin/codex-maintainer score examples/scored-run.md
```

## From A Release Package

```bash
tar -xzf codex-maintainer-v0.5.0.tar.gz
cd codex-maintainer-v0.5.0
./bin/codex-maintainer version
PREFIX="$HOME/.local" ./scripts/install.sh
"$HOME/.local/bin/codex-maintainer" init ios /tmp/demo-ios-repo
"$HOME/.local/bin/codex-maintainer" doctor /tmp/demo-ios-repo
```

## What The Demo Shows

- `validate` checks this workflow-bundle repo.
- `init ios` copies starter workflow files into a target repo.
- `doctor` confirms the copied workflow files exist.
- `score` turns a run summary into a maintainer-quality verdict.

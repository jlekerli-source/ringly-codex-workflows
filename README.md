<p align="center">
  <img src=".github/assets/shipguard-icon.png" width="104" alt="ShipGuard logo">
</p>

<h1 align="center">ShipGuard</h1>

<p align="center">
  Proof gates for AI-assisted software work.
</p>

<p align="center">
  <a href="docs/verify-first-quickstart.md">Quickstart</a> ·
  <a href="docs/install-doctor.md">Install</a> ·
  <a href="docs/github-action.md">GitHub Action</a> ·
  <a href="docs/cli.md">CLI</a> ·
  <a href="docs/index.md">Docs</a>
</p>

ShipGuard helps you use Codex and other coding agents without accepting vague handoffs like "done", "tested", or "should work".

It gives agent work a reviewable proof loop:

```text
prepare the task -> attach evidence -> verify the claims -> ship, review, or block
```

ShipGuard is local-first, open source, and app-neutral. It works as a CLI today, with the deepest support for iOS and growing starter profiles for web, backend, and CLI projects.

## Why ShipGuard

AI coding gets risky when the work looks finished but the proof is unclear.

ShipGuard keeps the important questions visible:

- What task was the agent allowed to do?
- Which files changed, and were they in scope?
- What proof was actually attached?
- Did the claims match the evidence?
- Should this be merged, reviewed, or blocked?

## Quickstart

Install from this checkout:

```bash
PREFIX="$HOME/.local" ./scripts/install.sh
shipguard version
shipguard validate
```

Add ShipGuard to a project:

```bash
shipguard init ios .
shipguard doctor ios .
```

Use `web`, `backend`, or `cli` instead of `ios` for those starter profiles.

## First Proof Report

Run the demo from a ShipGuard checkout:

```bash
./bin/shipguard prepare \
  "Add notification permission copy" \
  --path fixtures/demo-ios-repo \
  --out /tmp/shipguard-task \
  --profile ios \
  --validation "swift test" \
  --shareable

./bin/shipguard verify \
  --task /tmp/shipguard-task/shipguard-task.json \
  --diff examples/verify-first/diffs/scoped-permission.diff \
  --evidence examples/verify-first/receipts/swift-test-receipt.json \
  --claim "Implemented scoped notification permission copy." \
  --out /tmp/shipguard-verdict
```

Open the verdict:

```bash
/tmp/shipguard-verdict/shipguard-verdict.md
```

The report starts with the decision:

```text
ShipGuard Proof Report
Status: pass
Validation: covered
Claims checked: accepted
Next action: review or merge with the attached proof
```

See the full [Verify-First Quickstart](docs/verify-first-quickstart.md) for pass, review, and blocked examples.

## What You Get

- `prepare` and `verify` for scoped task contracts and proof reports.
- `init` and `doctor` for adding workflow guardrails to a repo.
- GitHub Actions helpers for PR proof reports.
- iOS audits for design, performance, modernization, AI readiness, preview routing, and report quality.
- Codex plugin packaging for local iOS ShipGuard workflows.
- Public fixtures and tests that keep the tool honest without private app code.

## Core Commands

| Command | What it does |
| --- | --- |
| `shipguard prepare` | defines the task, allowed scope, expected validation, and proof contract |
| `shipguard verify` | checks a diff, evidence receipts, and agent claims before review or merge |
| `shipguard init` | adds ShipGuard starter files to a repo |
| `shipguard doctor` | checks that a repo has the expected ShipGuard workflow files |
| `shipguard ios design` | audits UI/UX coherence, motion, haptics, app-type fit, and icon direction |
| `shipguard ios performance` | finds iOS performance risks and the proof needed to validate them |
| `shipguard inspect` | summarizes ShipGuard's own proof state and next maintainer action |

Full command list: [Command Matrix](docs/command-matrix.md).

## GitHub Actions

ShipGuard can run in CI and upload Markdown/JSON proof reports on pull requests.

Start with:

- [GitHub Action guide](docs/github-action.md)
- [Example PR workflow](examples/workflows/verify-pr.yml)

## Codex Plugin

Install or refresh the local iOS plugin while developing ShipGuard:

```bash
codex plugin marketplace add .
codex plugin add ios-shipguard@shipguard
shipguard codex status --strict
```

Start a new Codex thread after refreshing the plugin so the latest skill text is loaded.

## Repo Map

```text
bin/                   CLI entry point
scripts/               report engines and proof tools
plugins/ios-shipguard/ Codex plugin bundle
templates/             starter profiles
docs/                  user and maintainer docs
fixtures/              public regression fixtures
tests/                 validation lanes
actions/               reusable GitHub Actions
```

## ShipYard

ShipYard is the maintainer workspace behind ShipGuard. It contains the fixtures, evals, package checks, release proof, plugin readiness checks, and roadmap execution tools that keep ShipGuard itself honest.

Most users should start with `prepare`, `verify`, `init`, and `doctor`. ShipYard surfaces are for maintainers who want to inspect, package, benchmark, or release ShipGuard.

## Learn More

- [Docs index](docs/index.md)
- [Install And Doctor](docs/install-doctor.md)
- [Verify-First Quickstart](docs/verify-first-quickstart.md)
- [CLI reference](docs/cli.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Open source model](docs/open-source.md)
- [Security policy](SECURITY.md)

## License

MIT. See [LICENSE](LICENSE).

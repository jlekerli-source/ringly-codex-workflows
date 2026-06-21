# Synthetic Lean Gain Honesty Fixture

## ShipGuard Evaluation Boundary

This is a public synthetic ShipGuard fixture. It is not copied from a private app report.

## Fixture Intent

- Type: `shipguard-lean-report-quality-fixture`
- Source question: Does lean gain avoid fake per-repo savings while still showing benchmark-backed impact?

## Benchmark Scoreboard

- Benchmark: Synthetic Lean Gain public benchmark
- Scope: public benchmark, not this repository
- Baseline: same agent without the lean-code ruleset
- Method: paired public fixture tasks with and without the lean-code ruleset

| Metric | Baseline | Lean-code result | Change |
| --- | --- | --- | --- |
| Lines of code | 100% | 46% | -54% |
| Tokens | 100% | 78% | -22% |
| Cost | 100% | 80% | -20% |
| Time | 100% | 73% | -27% |
| Safety | 100% | 100% | 100% |

## Honesty Boundary

- Per-repo savings claim: `not-computed`
- Reason: There is no untreated baseline for this repository; ShipGuard cannot subtract code, cost, or time that was never produced.
- Do not claim current-repo line, token, cost, or time savings without a matched baseline.

## Current Repo Signals

- Lean audit findings show possible cuttable surfaces.
- Lean review findings show current-diff delete or simplify opportunities.
- Lean debt marker counts show intentional shortcuts that still need ceilings and upgrade triggers.

## Scope Boundary

This is ShipGuard product QA. The benchmark explains expected direction; only local Lean Deck reports prove current repo observations.

## Report Quality Questions

- Does lean gain avoid fake per-repo savings while still showing benchmark-backed impact?

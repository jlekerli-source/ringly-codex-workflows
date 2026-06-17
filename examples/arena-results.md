# Maintainer Arena Example

Run the public fixture pack:

```bash
./bin/shipguard arena run --fixture fixtures/arena --out /tmp/arena
```

Expected summary:

```text
average: 4.93/12
```

Expected aggregate fields in `results.json`:

```json
{
  "case_count": 15,
  "average_total": 4.93,
  "high_risk_finding_count": 19,
  "validation_evidence_cases": 5,
  "validation_evidence_ratio": 0.33,
  "validation_quality_average": 0.67,
  "scope_control_average": 1.07
}
```

The case reports are written under `runs/<case-id>/`.

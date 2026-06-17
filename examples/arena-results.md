# Maintainer Arena Example

Run the public fixture pack:

```bash
./bin/shipguard arena run --fixture fixtures/arena --out /tmp/arena
```

Expected summary:

```text
average: 5.21/12
```

Expected aggregate fields in `results.json`:

```json
{
  "case_count": 14,
  "average_total": 5.21,
  "high_risk_finding_count": 17,
  "validation_evidence_cases": 5,
  "validation_evidence_ratio": 0.36,
  "validation_quality_average": 0.71,
  "scope_control_average": 1.14
}
```

The case reports are written under `runs/<case-id>/`.

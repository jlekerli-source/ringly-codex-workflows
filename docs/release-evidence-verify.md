# Release Evidence Verification

`codex-maintainer release-evidence verify` consumes a release evidence artifact and checks that the static evidence, copied source reports, optional index, and optional bundle metadata agree.

Use it after downloading the artifact produced by `actions/release-evidence`:

```bash
./bin/codex-maintainer release-evidence verify \
  --dir /tmp/codex-maintainer-release-evidence \
  --out /tmp/codex-maintainer-release-evidence-verify \
  --require-diff true \
  --require-index true
```

Outputs:

- `evidence-verify.json`
- `evidence-verify.md`
- `badge.json`

The verifier accepts either a full action artifact directory containing `site/`, `index/`, optional `consumer-proof/`, optional `release-diff/`, and optional `bundle.json`, or a standalone evidence site directory containing `evidence.json`.

Checks include:

- `evidence.json` schema and pass status.
- Source `consumer-report.json` and `asset-digests.json` presence.
- Consumer proof release identity matching the static evidence release identity.
- Asset digest summary consistency.
- Required asset availability.
- Release diff source and pass status when diff evidence is present.
- Evidence index schema, pass status, and release entry when an index is present.
- Bundle output paths and diff flag consistency when `bundle.json` is present.

Use `--require-diff true` when your workflow must include comparison against a previous release. Use `--require-index true` when your workflow must include a browsable evidence history. The default `auto` mode verifies those files when present without requiring them.

In GitHub Actions, use `actions/download-artifact` and then `actions/release-evidence-verify`:

```yaml
- name: Download release evidence artifact
  uses: actions/download-artifact@v4
  with:
    name: codex-maintainer-release-evidence
    path: artifacts/codex-maintainer-release-evidence

- name: Verify release evidence artifact
  uses: jlekerli-source/ringly-codex-workflows/actions/release-evidence-verify@v3.21.0
  with:
    dir: artifacts/codex-maintainer-release-evidence
    require-diff: true
    require-index: true
    mode: fail
```

See `release-evidence-action.md` for producing the artifact and `../examples/workflows/release-evidence-consume.yml` for the full two-job workflow.

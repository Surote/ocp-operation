---
name: verify-ocp-operation
description: >
  Validate the ocp-operation training repo — YAML manifest syntax, Markdown link
  integrity, troubleshooting lab structure, and module README completeness.
  Use after editing manifests, adding images, or restructuring modules.
---

# verify-ocp-operation

This repo is a collection of OpenShift day-2 operations modules: YAML manifests
applied to a live cluster and Markdown documentation with screenshots. There is
no local server to start. Verification means proving the repo's content is
internally consistent and ready for a workshop learner.

## Launch

No process to start. The repo is static content. Build the validation
environment once:

```bash
cd <repo-root>
pip install pyyaml 2>/dev/null || true   # optional but enables deep YAML checks
```

Readiness gate: `python3 -c "from pathlib import Path; assert (Path('modules') / '01-cluster-health' / 'README.md').exists()"` exits 0.

## Doctor

```bash
cd <repo-root>
python3 -c "import pathlib; p=pathlib.Path('modules'); assert p.is_dir(), 'modules/ missing'; assert any(p.iterdir()), 'modules/ empty'"
```

If this fails the checkout is incomplete; re-clone before proceeding.

## Drive

Run the validation script from the repo root:

```bash
python3 .cursor/skills/verify-ocp-operation/validate.py
```

Exit code 0 means all checks pass. Exit code 1 means at least one failure; the
output lists every error with its category (`YAML`, `LINK`, `LAB`, `MOD`).

### What it checks

| Check | Category | What it proves |
|---|---|---|
| YAML syntax | `YAML` | Every `.yaml` file parses without error (uses `pyyaml` when available, falls back to basic read) |
| Link integrity | `LINK` | Every `![alt](path)` reference in Markdown resolves to a file on disk |
| Lab structure | `LAB` | Each troubleshooting case directory under `modules/09-troubleshooting/manifests/` contains `setup.yaml`, `broken.yaml`, and `fixed.yaml` |
| Module READMEs | `MOD` | Every directory under `modules/` has a `README.md` |

### Fixing failures

- **YAML** — open the reported file, fix the syntax error. Common: bad indentation, unquoted special characters.
- **LINK** — the image or file was moved/renamed. Update the Markdown reference or restore the file.
- **LAB** — a troubleshooting case is missing a lifecycle file. Add the missing `setup.yaml`, `broken.yaml`, or `fixed.yaml`.
- **MOD** — a new module directory lacks documentation. Add a `README.md`.

## Evidence

After each run, a JSON report is written to:

```
.cursor/skills/verify-ocp-operation/evidence/last-run.json
```

It records timestamp, per-check failure counts, and the full error list. This
file survives cleanup (there is no process to tear down).

## Cleanup

No processes or temporary state to remove. The evidence file persists at the
path above. To reset evidence history:

```bash
rm -rf .cursor/skills/verify-ocp-operation/evidence/
```

## Helpers

| File | Purpose | Invocation |
|---|---|---|
| `validate.py` | All-in-one validation | `python3 .cursor/skills/verify-ocp-operation/validate.py` |

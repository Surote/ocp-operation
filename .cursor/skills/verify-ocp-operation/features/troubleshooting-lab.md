# Troubleshooting Lab Structure

Module 09 is a structured troubleshooting lab. Each case directory under
`modules/09-troubleshooting/manifests/` must contain three lifecycle files that
define the case's healthy state, injected fault, and repair.

## Sub-features

- `setup.yaml` — creates the namespace (if absent) and deploys the healthy baseline
- `broken.yaml` — injects exactly the fault the learner must diagnose
- `fixed.yaml` — applies the repair the learner should discover

## How to get to it (user POV)

An instructor or learner runs:

```bash
oc apply -f manifests/<case>/setup.yaml     # baseline
oc apply -f manifests/<case>/broken.yaml    # inject fault
# ... diagnose ...
oc apply -f manifests/<case>/fixed.yaml     # verify repair
```

A missing file breaks the exercise flow.

## Driving it with validate.py

```bash
python3 .cursor/skills/verify-ocp-operation/validate.py
```

The `LAB` check category iterates every subdirectory of
`modules/09-troubleshooting/manifests/` (except `common/`), and verifies that
`setup.yaml`, `broken.yaml`, and `fixed.yaml` all exist.

## Gotchas

- The `common/` directory holds shared resources (namespace, diagnostic client,
  application template, route) and is intentionally excluded.
- Case `08b-configuration` is an alternative to case `08-storage` for clusters
  without a default StorageClass. Both are validated independently.

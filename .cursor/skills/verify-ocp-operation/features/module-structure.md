# Module Completeness

Every numbered module directory under `modules/` must have a `README.md` that
documents the procedures and concepts for that module. A module without a README
is invisible to learners navigating the repo.

## Sub-features

- README presence check for each module directory
- Covers numbered modules (`01-cluster-health` through `11-DNS`) and lettered
  variants (`03a-kubeletconfig`)

## How to get to it (user POV)

A learner navigates `modules/` on GitHub or locally and clicks into a module
directory. The README is the entry point — without it, the module appears empty
or undocumented.

## Driving it with validate.py

```bash
python3 .cursor/skills/verify-ocp-operation/validate.py
```

The `MOD` check category iterates every subdirectory of `modules/` and verifies
that `README.md` exists.

## Gotchas

- Nested subdirectories inside a module (like `manifests/` or `diagnostics/`)
  are not checked for READMEs — only the top-level module directory.
- The root `README.md` and `prep/README.md` are not covered by this check;
  they sit outside `modules/`.

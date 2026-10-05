# YAML Manifest Validity

All Kubernetes/OpenShift manifests in the repo must be syntactically valid YAML.
A broken manifest blocks `oc apply` for any learner who copies it.

## Sub-features

- Parse single-document YAML files
- Parse multi-document YAML files (separated by `---`)
- Detect common errors: bad indentation, unquoted colons, duplicate keys

## How to get to it (user POV)

A workshop learner runs `oc apply -f <manifest>`. If the YAML is malformed, `oc`
rejects it with a parse error before it reaches the API server.

## Driving it with validate.py

```bash
python3 .cursor/skills/verify-ocp-operation/validate.py
```

The `YAML` check category iterates every `.yaml` file under the repo root
(excluding `.cursor/`), parses each with `yaml.safe_load_all` (or a fallback
reader when `pyyaml` is absent), and reports failures.

## Gotchas

- Without `pyyaml` installed, the fallback catches only gross syntax errors (not
  duplicate keys or type coercion issues). Install it for full coverage.
- Files under `.cursor/` are excluded so the skill's own config isn't checked.

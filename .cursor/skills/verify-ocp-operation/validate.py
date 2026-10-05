#!/usr/bin/env python3
"""Validate ocp-operation repo content integrity.

Checks:
  1. YAML syntax   — every .yaml file parses without error
  2. Link integrity — image/file references in Markdown resolve to existing paths
  3. Lab structure  — each troubleshooting case has setup.yaml, broken.yaml, fixed.yaml
  4. Module README  — every module directory contains a README.md

Exit code 0 = all checks pass, 1 = at least one failure.
Evidence is written to .cursor/skills/verify-ocp-operation/evidence/.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

REPO = Path(__file__).resolve().parent.parent.parent.parent
EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"
MODULES_DIR = REPO / "modules"
TS_MANIFESTS = MODULES_DIR / "09-troubleshooting" / "manifests"
REQUIRED_CASE_FILES = {"setup.yaml", "broken.yaml", "fixed.yaml"}
COMMON_DIRS = {"common"}
LINK_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def check_yaml(errors: list[str]) -> int:
    """Parse every .yaml file. Return count of failures."""
    count = 0
    for yf in sorted(REPO.rglob("*.yaml")):
        rel = yf.relative_to(REPO)
        if ".cursor" in rel.parts:
            continue
        try:
            text = yf.read_text(encoding="utf-8")
            if HAS_YAML:
                list(yaml.safe_load_all(text))
            else:
                compile(text, str(rel), "exec")
        except Exception as exc:
            errors.append(f"YAML  {rel}: {exc}")
            count += 1
    return count


def check_links(errors: list[str]) -> int:
    """Resolve image/file Markdown links relative to each .md file."""
    count = 0
    for md in sorted(REPO.rglob("*.md")):
        rel_md = md.relative_to(REPO)
        if ".cursor" in rel_md.parts:
            continue
        content = md.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(content):
            href = m.group(1)
            if href.startswith(("http://", "https://")):
                continue
            target = (md.parent / href).resolve()
            if not target.exists():
                errors.append(f"LINK  {rel_md} -> {href} (not found)")
                count += 1
    return count


def check_lab_structure(errors: list[str]) -> int:
    """Each troubleshooting case dir must have setup/broken/fixed."""
    count = 0
    if not TS_MANIFESTS.is_dir():
        errors.append(f"LAB   {TS_MANIFESTS.relative_to(REPO)} directory missing")
        return 1
    for case_dir in sorted(TS_MANIFESTS.iterdir()):
        if not case_dir.is_dir() or case_dir.name in COMMON_DIRS:
            continue
        existing = {f.name for f in case_dir.iterdir() if f.is_file()}
        missing = REQUIRED_CASE_FILES - existing
        if missing:
            rel = case_dir.relative_to(REPO)
            errors.append(f"LAB   {rel} missing: {', '.join(sorted(missing))}")
            count += 1
    return count


def check_module_readmes(errors: list[str]) -> int:
    """Every module directory must have a README.md."""
    count = 0
    if not MODULES_DIR.is_dir():
        errors.append(f"MOD   {MODULES_DIR.relative_to(REPO)} directory missing")
        return 1
    for mod_dir in sorted(MODULES_DIR.iterdir()):
        if not mod_dir.is_dir():
            continue
        if not (mod_dir / "README.md").exists():
            rel = mod_dir.relative_to(REPO)
            errors.append(f"MOD   {rel}/README.md missing")
            count += 1
    return count


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    errors: list[str] = []
    results = {
        "yaml": check_yaml(errors),
        "links": check_links(errors),
        "lab_structure": check_lab_structure(errors),
        "module_readmes": check_module_readmes(errors),
    }

    total_failures = sum(results.values())
    passed = total_failures == 0

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repo": str(REPO),
        "has_pyyaml": HAS_YAML,
        "checks": results,
        "total_failures": total_failures,
        "passed": passed,
        "errors": errors,
    }

    report_path = EVIDENCE_DIR / "last-run.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    header = "PASS" if passed else "FAIL"
    print(f"[{header}] yaml={results['yaml']} links={results['links']} "
          f"lab={results['lab_structure']} readmes={results['module_readmes']}")
    for e in errors:
        print(f"  {e}")
    print(f"\nEvidence: {report_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

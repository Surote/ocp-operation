# Documentation Link Integrity

Every image embed (`![alt](path)`) in the repo's Markdown files must point to a
file that exists on disk. Broken links leave blank images in the rendered
documentation.

## Sub-features

- Relative path resolution (each link resolved from the Markdown file's own directory)
- Skip external URLs (`http://`, `https://`)
- Cover `.png`, `.jpg`, `.gif`, and any other local file reference

## How to get to it (user POV)

A learner reads a module README on GitHub or in a local Markdown viewer. If an
image path is wrong, they see a broken-image icon or an error instead of the
screenshot that illustrates the procedure.

## Driving it with validate.py

```bash
python3 .cursor/skills/verify-ocp-operation/validate.py
```

The `LINK` check category scans every `.md` file (excluding `.cursor/`),
extracts `![...](href)` references, resolves each `href` relative to the
Markdown file's parent directory, and checks `Path.exists()`.

## Gotchas

- Only `![]()` image syntax is checked. Bare `[text](link)` file links are not
  currently covered — add them if the repo starts cross-linking between modules.
- Anchors (`#section`) appended to local paths would cause a false positive; the
  repo currently does not use them in image links.

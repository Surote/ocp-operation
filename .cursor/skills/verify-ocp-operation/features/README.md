# Feature Map — ocp-operation

Each file in this directory describes one verifiable aspect of the repo and how
the validation harness proves it.

| Feature | File | What it covers |
|---|---|---|
| YAML manifest validity | [yaml-manifests.md](yaml-manifests.md) | Every `.yaml` file parses without error |
| Documentation link integrity | [documentation-links.md](documentation-links.md) | All image/file references in Markdown resolve on disk |
| Troubleshooting lab structure | [troubleshooting-lab.md](troubleshooting-lab.md) | Each lab case has the required setup/broken/fixed lifecycle |
| Module completeness | [module-structure.md](module-structure.md) | Every module directory has a README |

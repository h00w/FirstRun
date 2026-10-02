# FirstRun

A verified starting point for the FirstRun project. Application scope is pending definition.

## Current scope

This foundation includes contribution guidance, a project roadmap, and a dependency-free
check for broken local Markdown links. It does not yet implement an application.

## Verify

Use Python 3.11 or newer from the repository root:

```bash
python scripts/check_repository.py
python -m unittest discover -s tests -v
```

GitHub Actions runs these checks for pull requests and changes to `main`.

## Next milestone

Define the intended users, primary workflow and acceptance criteria in the
[roadmap](docs/ROADMAP.md). See [contribution guidance](CONTRIBUTING.md) before opening a PR.

# Contribution guidelines

This is a Python hackathon project for garbage sorting, with Arduino firmware. Favor a working MVP, readable code, and small changes over extra architecture.

## Project layout

- Keep Python application code under `src/`, grouped by its existing responsibility: `backend/`, `frontend/`, `hardware/`, and `vision/`.
- Keep Arduino sketches under `firmware/arduino/` and tests under the existing `test/` directory.
- Put documentation at the repository root. Keep configuration, assets, and datasets in suitable existing locations; do not add folders for hypothetical future needs.
- Follow the current layout and naming conventions. If a new file's location is unclear, ask before creating, moving, or reorganizing it. Do not make major structural changes without approval.

## Python and design

- Use standard Python style and descriptive `snake_case` names; use `PascalCase` for classes and `UPPER_SNAKE_CASE` for constants.
- Write focused functions and modules with clear responsibilities and interfaces. Reuse existing code where sensible; avoid unnecessary abstractions, dependencies, and file proliferation.
- Prefer straightforward, readable implementations. Remove unused imports and code made obsolete by your changes. Do not remove existing code or functionality of uncertain purpose without asking.
- Validate external input and handle expected errors with useful messages. Do not silently swallow exceptions.
- Keep secrets out of source control. Use environment variables for sensitive configuration and never commit secret-bearing `.env` files.

## Changes and verification

- Inspect relevant code and conventions before editing. Keep changes focused, preserve existing behavior, and do not overwrite others' work.
- Update the README when a change affects setup, usage, dependencies, or project structure; keep setup and configuration guidance accurate.
- Run relevant existing tests or checks when available. Add focused tests for important behavior when practical; do not introduce a test framework without need. State clearly what was not verified, and never claim checks that were not run.
- Review changed files for placement, clarity, unused code, and broken references. Avoid leaving temporary files, debug output, or generated artifacts.
- Ask before deleting data or code with uncertain purpose, changing existing functionality in a consequential way, introducing a major dependency or framework, or choosing between architectural options with substantial tradeoffs. Recommend an option and explain the uncertainty.
- Do not commit, push, or rewrite Git history unless asked. Prioritize incremental MVP work and avoid premature optimization or infrastructure the project does not need.

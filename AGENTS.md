# AGENTS Guide

## Project Goal

- Maintain a clean, reusable automation framework.
- Keep layers decoupled and behavior easy to validate.
- Prefer consistent conventions over one-off implementations.

## Directory Responsibilities

- `action/`: API client layer only.
- `config/`: environment templates (`dev` / `prod`) and lane config.
- `test/`: pytest specs, fixtures, and test orchestration.
- `testdata/`: test data models and reusable cases.
- `utils/`: shared low-level utilities.

## Global Rules

1. Never commit runtime secrets (`token`, `password`, API keys, private URLs).
2. Prefer environment variables for runtime-specific values.
3. Keep naming stable and easy to understand.
4. Keep scope minimal: change only what is needed for the current task.
5. Update docs when behavior or structure changes.

## Validation Baseline

- Run syntax checks after edits:

  - `PYTHONPYCACHEPREFIX=.pycache python3 -m py_compile run.py utils/*.py action/api/*.py test/api/*.py testdata/api/*.py`

- Run focused tests first, then broader regression if needed.

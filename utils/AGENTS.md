# AGENTS Guide (`utils/`)

## Scope

- Shared utilities (`config_toml.py`, `httpclient.py`, and future generic modules).

## Rules

1. Utilities must stay domain-agnostic.
2. Keep interfaces stable and explicit; avoid hidden side effects.
3. Do not add workflow-specific business rules here.
4. Any config schema change must keep backward compatibility or be migrated clearly.
5. Keep error messages actionable for callers.

## Quality Baseline

- New utility code should include minimal docstrings/type hints.
- Validate touched files with `py_compile` after edits.

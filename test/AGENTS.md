# AGENTS Guide (`test/`)

## Scope

- Test architecture and test suite entry structure.

## Rules

1. Keep this folder framework-oriented and easy to maintain.
2. Keep test flows focused on behavior verification.
3. Prefer small representative examples over large legacy case dumps.
4. Use explicit imports; avoid wildcard imports.
5. Keep fixtures reusable and environment-agnostic.

## Current Direction

- Main focus is `test/api`.
- Add new domains only when needed and keep them generic.

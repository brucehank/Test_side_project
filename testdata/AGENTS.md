# AGENTS Guide (`testdata/`)

## Scope

- Reusable test data structures and case constants.

## Rules

1. Store only test data, not API calls or workflow logic.
2. Prefer typed models/dataclasses over raw dict blobs.
3. Use synthetic or placeholder-friendly values by default.
4. Avoid coupling testdata values to one specific runtime setup.
5. Keep naming stable and predictable for parametrized tests.

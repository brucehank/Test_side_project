# AGENTS Guide (`action/`)

## Scope

- Applies to `action/` and deeper folders unless a deeper `AGENTS.md` overrides.

## Rules

1. `action` is API client layer only; no test assertions here.
2. Do not read config files directly in `action` classes.
3. Keep methods focused on request building and response forwarding.
4. Avoid domain-specific test logic in this layer.
5. Use stable and descriptive naming conventions.

## Expected Pattern

- Client class extends shared HTTP capability.
- Keep common headers in one helper method.
- Return normalized response objects for test layer assertions.

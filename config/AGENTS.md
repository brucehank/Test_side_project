# AGENTS Guide (`config/`)

## Scope

- `common.toml`, `dev.toml`, `prod.toml`, and config docs.

## Rules

1. Keep only `dev` and `prod` environments.
2. Commit template-safe values only (empty strings or obvious placeholders).
3. Never commit real credentials or runtime tokens.
4. When adding/removing keys, keep `utils/config_toml.py` models in sync.
5. Keep lane/module paths valid and minimal for local execution.

## Security Baseline

- Assume all config files are public.
- Put runtime secrets in environment variables, not git-tracked files.

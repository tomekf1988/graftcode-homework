# Review — Milestone 2: Configuration

## Verdict: approved (after fixes)

## Issues found and resolved

### 1. `PRICING_MODE` was case-sensitive (fixed)
`PricingMode(raw_mode)` failed with a misleading error when the user set `PRICING_MODE=LOCAL` (uppercase), which is the idiomatic form for env vars. Fixed by normalising with `.lower()` before parsing. Test added.

### 2. `.gitignore` excluded `.claude/` entirely (fixed)
`.claude/CLAUDE.md` and command files are intentionally tracked. Scoped the ignore to `.claude/settings.local.json` only.

## Issues accepted as-is

### `graftcode_project_key` validated but not injected into factory
`load_settings()` validates that the key is present in remote mode, but `create_order_service_from_settings` does not pass it to `RemotePricingProvider` (which reads the env var directly). This is intentional: the validation provides a fast-fail at startup, and wiring the key through the provider is deferred to Milestone 3 when remote mode is fully exercised. The comment in `settings.py` makes this explicit.

## Test coverage
26 tests, all passing. `test_settings.py` covers defaults, remote mode with/without key, blank key, invalid mode, and case insensitivity.

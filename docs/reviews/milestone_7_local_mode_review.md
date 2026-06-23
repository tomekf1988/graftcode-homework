# Code Review — Milestone 7: GraftCode Local (Inmemory) Mode

## 1. Summary

Milestone 7 adds `PRICING_MODE=local` support so the order service can call the pricing implementation in-process (Graft inmemory), without Docker or a WebSocket connection. The change surface is small and correctly scoped: one new field in `Settings`, one conditional in the factory, a new `make setup-local` target, and corresponding tests. No existing tests were broken; new tests cover the new behaviour well.

---

## 2. Critical Issues

### None.

There are no correctness bugs, no broken contracts, and no architectural violations.

---

## 3. Suggested Improvements

### 3.1 `pricing_mode: str` accepts arbitrary values silently

`Settings.pricing_mode` is typed as `str`. Any value other than `"remote"` or `"local"` (e.g. `PRICING_MODE=remot` from a typo) falls through the `if settings.pricing_mode == "remote"` branch silently as if it were `"local"`, because the factory treats anything that is not `"remote"` as local. This is a latent foot-gun.

**Options (in order of preference):**

1. Add a guard in `load_settings()` that raises `ValueError` for unknown values — consistent with the fast-fail philosophy already established in M2.
2. Use a `Literal["remote", "local"]` type annotation (no runtime enforcement, but at least documents intent and enables static analysis).

A minimal fast-fail guard:

```python
VALID_MODES = {"remote", "local"}
mode = os.environ.get("PRICING_MODE", "remote").lower()
if mode not in VALID_MODES:
    raise ValueError(f"Invalid PRICING_MODE={mode!r}. Expected one of: {sorted(VALID_MODES)}")
```

### 3.2 `if host:` in `GraftPricingProvider.__init__` is truthy, not `is not None`

`/order_service/adapters/graft_pricing_provider.py` line 22:

```python
if host:
    GraftConfig.host = host
```

This check was already present before M7. An empty string `""` would be treated as "no host provided" and silently leave `GraftConfig.host` at `"inmemory"`. This is unlikely to cause real issues — an empty string is not a valid WebSocket URL — but `if host is not None` would be strictly correct and self-documenting. This is a minor pre-existing issue surfaced more visibly now that both code paths are exercised. Worth noting but not blocking.

### 3.3 `PYTHON_VERSION := 3.13` hardcoded in Makefile

`SITE_PACKAGES := order_service/.venv/lib/python$(PYTHON_VERSION)/site-packages`

If the venv is created with Python 3.12 or 3.14 (e.g. on a developer machine with a different default Python), `make setup-local` silently creates the symlink in the wrong directory. The actual Python version in the venv can be read dynamically:

```makefile
PYTHON_VERSION := $(shell order_service/.venv/bin/python --version 2>&1 | awk '{print $$2}' | cut -d. -f1,2)
```

This only matters if team members or CI use a Python version other than 3.13. If 3.13 is a hard requirement enforced by `.python-version` or `requires-python`, this is low priority.

### 3.4 `docs/plans/milestone_7_local_mode.md` is in Polish

The plan document is written in Polish while all other documentation in the repo (CLAUDE.md, README, milestone summaries) is in English. This is an inconsistency that makes the plan harder to use as a reference for non-Polish speakers. Not a code issue, but worth aligning if the repo is meant to be shared.

### 3.5 Plan document describes a different approach than what was implemented

`docs/plans/milestone_7_local_mode.md` describes copying files (`cp pricing_service/graft/pricing_service_graft.py ...`) and creating a `pricing_service` symlink in `site-packages/`. The actual implementation uses a single `graft` symlink inside `graft.pricing_service_graft/`. The plan was superseded but not updated. As-is it could mislead someone debugging the symlink setup. This is a documentation-only issue with no impact on correctness.

---

## 4. Final Verdict

**Approve with minor notes.**

The core change is correct and minimal. The `Settings` field, factory conditional, Makefile target, and tests are all consistent and well-structured. The existing architecture decisions from M2 (fast-fail on misconfiguration) are not fully applied to the new `pricing_mode` field — adding an unknown-value guard would bring this inline. Everything else is low priority or pre-existing.

# Milestone 8 — Order Service via Vision (Remote Mode) Review

## Summary

Milestone 8 replaces the FastAPI HTTP layer with a Graftcode Vision bridge (`OrderServiceGraft`),
wires up a two-container Docker Compose setup, and documents the SDK bugs encountered during
implementation. The scope is narrow and the implementation is intentionally minimal, which is
appropriate given the SDK constraints. The core business logic and adapter layer are untouched
and remain solid. However, there are several issues worth addressing: unhandled exceptions in the
graft bridge class, a Dockerfile that hardcodes an ephemeral registry URL, missing tests for the
bridge, and a `test_inmemory.py` script that is mislabeled and misplaced.

---

## Critical Issues

### 1. `OrderServiceGraft` swallows all exceptions silently

`order_service/graft/order_service_graft.py` has no error handling in `place_order` or
`get_order`. When `OrderService` raises `InvalidOrderRequestError`, `OrderNotFoundError`, or
`OrderPlacementError`, those exceptions propagate uncaught to the gg runtime, which will wrap
them in its own error representation — but there is no logging, no structured error response, and
no guarantee that the gg runtime surfaces the message clearly to the Vision caller.

This is different from the FastAPI layer, which explicitly mapped domain exceptions to HTTP status
codes and bodies. The graft bridge layer has no equivalent. At a minimum, each method should catch
known domain exceptions, log them, and re-raise (or convert to a structured JSON error response
if the Vision protocol supports it), so that a caller can distinguish "invalid input" from
"service crashed".

### 2. Hardcoded ephemeral registry GUID in Dockerfile

`order_service/graft/Dockerfile` line 15 contains:

```
--extra-index-url https://grft.dev/simple/f812a82c-cdeb-4928-bf7e-c9e6e222e5c2__free \
```

The same GUID appears in `Makefile` line 7. Bug 4 in `docs/graftcode/bugs.md` correctly
documents that this GUID is tied to the gg instance and becomes a 404 on restart, making
`docker build --no-cache` fail silently only due to Docker layer caching. The problem is that
the Dockerfile does not acknowledge this constraint at all — there is no comment warning that
this URL must be updated before a clean build. A developer running `docker build --no-cache`
after a gg restart will get a cryptic pip failure with no indication of why.

The Makefile has a similar issue but is slightly less dangerous because it is typically run while
gg is active. The Dockerfile, being an image build artifact, is the more dangerous location.

At minimum, add a comment in the Dockerfile directly above the `--extra-index-url` line stating
that this GUID is ephemeral and must be replaced from the active gg instance URL before a
clean rebuild.

### 3. No tests for `OrderServiceGraft`

The graft bridge class has no unit tests. The adapter (`GraftPricingProvider`) and the domain
service (`OrderService`) are both tested, but `OrderServiceGraft` itself is not. There are two
testable behaviors: the JSON serialization shape of the response, and what happens when
`OrderService` raises. Given that the bridge is the public API surface of the service (the entry
point that Vision callers invoke), this gap matters.

A test for `place_order` should verify the JSON response keys and that `total_price` is
serialized as a string (Decimal is not JSON-serializable natively — the `str()` conversion is
correct but could silently break if the field type changes). A test for error propagation should
verify that domain exceptions are not silently swallowed.

These tests can be written with a fake `OrderService` (inline, per project convention) without
any gg runtime dependency.

---

## Suggested Improvements

### 4. `test_inmemory.py` is misnamed and misplaced

The file is named `test_inmemory.py` and lives at the repo root, but it does not test in-memory
mode — it tests the remote graft client (`PricingServiceGraft`) directly inside a running Docker
container, using remote-mode behavior. It is a smoke/diagnostic script, not an automated test,
and its `PRICING_MODE=local` override is misleading because the graft client it exercises does
not respect that env var in the way the order service does.

The `test-inmemory` Makefile target `docker cp`s the file into the container on each run, which
means it is not part of the container image. This is a developer convenience script, which is
fine, but it should either live in `scripts/` or `tools/` to signal its nature, or have a
clearer module-level docstring explaining what it actually tests (the graft SDK client, not the
full service pipeline).

The current docstring says "Test graft pricing client in inMemory mode directly" — "inMemory
mode" is a gg SDK term, but what the script actually exercises is the SDK's client-side call
path, not inMemory execution. The name and docstring create false confidence.

### 5. `factory.py` still exports `create_order_service` with a misleading name

`order_service/bootstrap/factory.py` exports `create_order_service(settings)`. With FastAPI
gone, this is the only factory function and it is called directly by `OrderServiceGraft.__init__`.
The name `create_order_service` is fine, but the old function `create_order_service_from_settings`
(mentioned in M2 architectural decisions) appears to have been consolidated into
`create_order_service`. This is correct — the single function accepting `Settings` is cleaner.
No action needed, just confirming the cleanup is complete.

### 6. `docker-compose.yml` volume mount path is fragile

The volume mount at line 20:

```
./pricing_service/graft:/usr/local/lib/python3.13/site-packages/graft_pypi_pricing_service_graft/graft.pricing_service_graft/graft:ro
```

This path embeds the Python version (`python3.13`) and the package's installed directory name.
If either changes (Python patch version bump, package rename, package reinstall), the mount
silently fails and the service runs without the expected override. A brief comment explaining
the purpose (satisfying the graft type-lookup symlink requirement from M7) and the fragility
would help the next developer who bumps the Python version.

### 7. `.env` is gitignored — confirm it stays that way

The `.gitignore` correctly lists `.env`. Git confirms it is not tracked (`git ls-files .env`
returns empty). The `.env` contains only non-secret defaults (`PRICING_MODE=remote`,
`GRAFT_HOST=ws://pricing-graft/ws`), so exposure would be low-risk, but the current setup is
correct. An `.env.example` with the same content would be a minor improvement for developer
onboarding, but is optional given that `docker-compose.yml` documents the defaults inline via
`${VAR:-default}` syntax.

### 8. `test_graft_provider.py` uses `MagicMock` — acceptable given SDK dependency

`test_graft_provider.py` uses `MagicMock` for `PricingServiceGraft` rather than a fake, which
is a pragmatic exception to the project's fakes-over-mocks convention. The SDK class cannot be
instantiated without a running gg runtime, so a mock is the right call here. The mock usage is
contained to that one test file and the behavior under test (JSON parsing, exception mapping) is
clearly verified. This is acceptable.

---

## Final Verdict

The implementation is sound within its constraints. The architecture boundary (no
`pricing_service.*` imports in `order_service`) is maintained. The adapter layer is correct.
The Docker setup works under the documented assumptions. The bugs.md is genuinely useful and
accurate documentation of SDK-level problems.

The two issues that need attention before this can be considered complete:

1. `OrderServiceGraft` needs error handling — without it, domain errors become opaque crashes at
   the Vision layer, which is worse than the old FastAPI 400 responses.
2. `OrderServiceGraft` needs at least two unit tests — JSON shape of successful response, and
   behavior on domain exception.

The ephemeral Dockerfile registry URL is a real operational risk but is SDK-imposed; adding a
comment is the realistic mitigation.

Everything else (misplaced script, fragile volume path) is minor and can be addressed
opportunistically.

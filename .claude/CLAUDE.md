## Workflow

Work milestone-by-milestone. **Each milestone must be started manually by the user.**
Do not begin the next milestone automatically after finishing the current one.

For each milestone:

1. implementation
2. automated tests
3. review
4. summary → `docs/milestones/<milestone>.md`
5. update CLAUDE.md to reflect any architectural decisions, new conventions, or stack changes introduced in the milestone

### File naming convention

All milestone-related files use the pattern `milestone_<number>_<short_name>`, e.g.:
- `docs/milestones/milestone_1_domain_and_business_logic.md`
- `docs/prs/milestone_1_domain_and_business_logic.md`
- `docs/reviews/milestone_1_domain_and_business_logic_review.md`

## Milestones

Original plan: `docs/plans/pre_graftcode_milestones.md`
Revised plan (M4–6): `docs/plans/milestone_4_5_6_revised_plan.md`

| # | Name | Status |
|---|------|--------|
| 1 | Domain & business logic completeness | ✅ done |
| 2 | Configuration (env vars) | ✅ done |
| 3 | HTTP API on Order Service (FastAPI) | ✅ done |
| 4 | GraftCode integration (architecture refactor) | ✅ done |
| 5 | Docker, Docker Compose, Makefile | pending |
| 6 | README & documentation | pending |

## Agents

For backend implementation tasks,
delegate to the `python-dev` subagent via the Agent tool.


After each implementation milestone (or when explicitly asked to review),
delegate to the `reviewer` subagent via the Agent tool.

## Git

* Never add `Co-Authored-By` to commit messages — commits are authored by the user only
* Every commit must include all milestone artifacts — not just implementation files:
  * `docs/prs/<milestone>.md`
  * `docs/reviews/<milestone>_review.md` (if exists)
  * `tasks/done.md`, `tasks/in_progress.md`, `tasks/todo.md`
* Always run `git status --short` before committing to catch untracked docs and tasks files

---

## Architecture decisions (Milestone 1)

### Exception wrapping at service boundaries
`OrderService.place_order` catches `ProductNotFoundError`, `InvalidQuantityError`,
and `UnsupportedCustomerTypeError` from the pricing provider and re-raises them as
`InvalidOrderRequestError`. This keeps the order domain clean — callers deal only
with `order_service.domain.exceptions`, not with pricing-domain types.

### In-memory order store
`OrderService` holds a `dict[str, Order]` as its order repository. Chosen over a
formal repository interface because there is only one implementation and no persistence
requirement in this codebase. Can be extracted to a `OrderRepository` port later if needed.

### UnsupportedCustomerTypeError location
Lives in `pricing_service/domain/exceptions.py` (PricingError subclass). The
`LocalPricingProvider` adapter raises it when `CustomerType(customer_type)` fails;
`OrderService` catches it via a `from pricing_service.domain.exceptions import ...`
import, which is acceptable because the adapter already bridges the two domains.

### Test strategy
Fakes (simple classes) over mocks. Inline fakes in test files when used only once;
shared fakes in `tests/fakes/` when reused across multiple test modules.

---

## Architecture decisions (Milestone 2)

### Settings as a frozen dataclass (`order_service/config/settings.py`)
`Settings` is a frozen dataclass produced once by `load_settings()` at startup. Stdlib
only (`os`, `dataclasses`) — no pydantic or python-dotenv. Validated at load time so
misconfiguration fails fast with a clear message.

### `PRICING_MODE` normalised to lowercase
`os.environ.get("PRICING_MODE", "local").lower()` before enum parsing, so `LOCAL`,
`Local`, and `local` all resolve correctly. Env vars are idiomatically upper-cased so
this avoids a common misconfiguration.

### `graftcode_project_key` validated but not injected
`load_settings()` validates the key is present when `PRICING_MODE=remote`, but the
factory does not pass it to `RemotePricingProvider` yet — the provider reads the env
var directly. Wiring the key through is deferred to the milestone that fully implements
remote mode (Milestone 6).

### Factory backward compatibility
`create_order_service_from_settings(settings)` was added to `factory.py` alongside
the unchanged `create_order_service(mode)`. Existing callers (tests) continue to work
without modification.

---

## Architecture decisions (Milestone 3)

### FastAPI app wired via `app.state`
`lifespan()` calls `load_settings()` → `create_order_service_from_settings(settings)`
and stores the result in `app.state.order_service`. Route handlers read it via
`request.app.state.order_service`. No global state, no DI framework needed.

### `InvalidOrderRequestError` → 400 (not 422)
FastAPI owns 422 for Pydantic schema validation. Domain rejections (unknown product,
zero quantity, unsupported customer type) are semantically different and map to 400.

### `pytest`/`httpx` in `[dependency-groups] dev`
Test-only packages are kept out of production dependencies. `uv sync` installs them
locally; `uv sync --no-dev` omits them in Docker.

### `OrderResponse.from_result` classmethod
Eliminates duplicated six-field constructor calls across the two route handlers.
Single place to update if `OrderResult` grows fields.

### Test fixture state injection
When testing with a fake provider, `app.state.order_service` must be set *inside*
the `with TestClient(app)` block (after lifespan runs), not before `__enter__`.

---

## Architecture decisions (Milestone 4)

### Zero `pricing_service.*` imports in `order_service`
`order_service` must not import from `pricing_service.*`. The `GraftPricingProvider`
adapter is the sole boundary between the two services; all exception translation happens
there. `OrderService` knows only `order_service.domain.exceptions`.

### Single adapter: `GraftPricingProvider`
Replaces `LocalPricingProvider` and `RemotePricingProvider`. Local (in-memory) mode is
not used — it has a bug in Graft alpha. All pricing calls go through `PricingServiceGraft`
(Graft-generated client). `PricingProvider` protocol is kept for test fake injection.

### `GRAFT_HOST` read by the adapter, not the factory
`GraftPricingProvider.__init__` reads `GRAFT_HOST` from env and sets `GraftConfig.host`
if present. The factory (`create_order_service_from_settings`) does not touch `GraftConfig`.
This keeps graft-specific knowledge inside the adapter boundary.

### `Settings` contains only `pricing_mode`
`graft_host` is not in `Settings` — it is an adapter implementation detail. `Settings`
stays simple (stdlib only, single field). `PRICING_MODE` enum is kept for future use
even though only `remote` mode works end-to-end today.

### `HypertubeException` → `InvalidOrderRequestError`
Any `HypertubeException` from the graft client means the pricing server responded with a
domain error (bad product, quantity, customer type). Everything else → `PricingServiceUnavailableError`.
This is a reasonable heuristic for the alpha SDK where `exc.name` is not a clean discriminator.

### Graft package not in `uv` lockfile
The custom registry (`https://grft.dev/simple/…`) returns HTML, not a PEP 503 Simple API.
`uv lock` cannot resolve it. The package must be installed manually:
```
uv pip install --extra-index-url https://grft.dev/simple/b4486228-d411-405d-a78c-e8521e198750__free \
    graft-pypi-graftcode-homework==0.1.0
```
The install command is documented in `pyproject.toml` as a comment. Docker handles it
via `RUN` in the Dockerfile (Milestone 5).
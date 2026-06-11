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

All milestones are defined in `docs/plans/pre_graftcode_milestones.md`.

| # | Name | Status |
|---|------|--------|
| 1 | Domain & business logic completeness | ✅ done |
| 2 | Configuration (env vars) | pending |
| 3 | HTTP API on Order Service (FastAPI) | pending |
| 4 | Docker, Docker Compose, Makefile | pending |
| 5 | README & documentation | pending |
| 6 | GraftCode integration | pending (out of scope for now) |

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
# Milestone 3 Review: HTTP API on Order Service

## 1. Summary

The FastAPI layer is well-structured and appropriately thin. The lifespan wiring, dependency injection, error handler registration, and schema separation all follow idiomatic FastAPI. The test suite covers the happy paths, all three error-status-code contracts, schema validation, and lifespan wiring. No critical bugs were found.

Two real issues deserve attention: `PricingServiceUnavailableError` is reachable from the service but is silently unmapped in the API layer, and the `unavailable_client` fixture bypasses proper dependency injection in a way that can produce confusing test failures. Everything else is minor.

---

## 2. Critical Issues

### 2.1 `PricingServiceUnavailableError` is not caught by any error handler

`order_service/domain/exceptions.py` defines both `OrderPlacementError` and `PricingServiceUnavailableError` as siblings under `OrderError`. `OrderService.place_order` catches `PricingServiceUnavailableError` and re-raises it as `OrderPlacementError`, so at the service boundary the distinction is correctly collapsed. The error handler for `OrderPlacementError` therefore covers this case today.

The risk is structural: if any future code path raises `PricingServiceUnavailableError` directly (e.g., a health-check endpoint, or middleware calling the provider), FastAPI will have no handler for it and will return a 500 with a leaking traceback. Since `PricingServiceUnavailableError` is a public domain exception, it is worth adding a handler for it now, or removing it from the public API if it is intentionally internal.

File: `order_service/api/app.py`, `order_service/domain/exceptions.py`

### 2.2 `unavailable_client` uses `raise_server_exceptions=False` instead of a dependency override

```python
@pytest.fixture()
def unavailable_client():
    app = create_app()
    unavailable = OrderService(UnavailablePricingProvider())
    app.dependency_overrides[get_order_service] = lambda: unavailable
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
```

`raise_server_exceptions=False` suppresses all unhandled exceptions from the server side, including ones that should never reach the client (programming errors, assertion failures in handlers). This is too broad a suppression. The fixture correctly uses a dependency override, so the error handler *should* catch the 503 before it becomes an unhandled exception. If the handler is working, `raise_server_exceptions=False` is not needed; if it is needed to make the test pass, that indicates the handler is not firing.

The correct pattern for testing a 503 is to rely purely on the dependency override and the registered error handler, with the default `raise_server_exceptions=True`. If the test fails without the flag, that is the bug to fix, not a reason to suppress exceptions.

File: `order_service/tests/test_api.py`, lines 29-34

---

## 3. Suggested Improvements

### 3.1 `get_order_service` should use `Annotated` injection (minor, FastAPI convention)

```python
# current
def get_order_service(request: Request) -> OrderService:
    return request.app.state.order_service
```

The current approach is correct and readable. A minor improvement for future-proofing: annotate the return type as `Annotated[OrderService, Depends(get_order_service)]` at the call site, or define a type alias `OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]` in `dependencies.py`. This is not blocking, just more idiomatic for larger FastAPI codebases.

### 3.2 `PlaceOrderRequest.quantity` has no validation constraint

`quantity: int` accepts 0 and negative values at the schema layer; the domain enforces the constraint later and returns a 400. This is fine architecturally (domain owns the rule), but the Pydantic model could use `quantity: int = Field(gt=0)` to return a more informative 422 and prevent the round-trip into the domain for obviously invalid input. Optional — keep it in the domain if you prefer a single enforcement point.

File: `order_service/api/schemas.py`

### 3.3 `OrderResponse.from_result` factory method on the schema model

The `from_result` classmethod on `OrderResponse` works, but it couples the Pydantic schema to the `OrderResult` dataclass. For a project this size it is acceptable. If the contract between the API layer and the service evolves differently, consider moving the mapping to the router (inline `OrderResponse(**result.__dict__)` or `model_validate(result)` with `from_attributes=True`). Not a change to make now — just something to watch as the schema diverges from the domain result.

### 3.4 `__main__.py` hardcodes host/port with no env-var escape hatch

```python
uvicorn.run("order_service.api.app:app", host="0.0.0.0", port=8000, reload=False)
```

Fine for the current milestone. Before Milestone 4 (Docker/Compose), consider reading `HOST` and `PORT` from env or accepting them as CLI args, to avoid a code change when deploying in different environments.

File: `order_service/__main__.py`

### 3.5 `test_lifespan_wires_order_service` does not clean up `app.state`

The lifespan test creates a `TestClient(app)` without overriding the dependency, so the full lifespan runs including `load_settings()`. This is intentional and is the right approach for this test. It relies on `PRICING_MODE=local` being set via `monkeypatch`, which is correct. No change needed, but a comment explaining why this test exists (vs. the other client fixture) would help future readers.

### 3.6 Test for `test_place_order_premium_discount` is a cross-cutting concern test

This is a good smoke test that the domain pricing logic wires through correctly. It does its job, but it is slightly misplaced in an API test file — it is really testing the `LocalPricingProvider` business rule through the HTTP layer. Acceptable at this stage; just worth noting if the test suite grows.

---

## 4. Final Verdict

**Approve with minor fixes.**

The implementation is clean, idiomatic, and correctly layered. The separation of concerns across `app.py`, `dependencies.py`, `schemas.py`, `error_handlers.py`, and the router is well-done — each file has a single responsibility and is easy to navigate. The test suite is solid: it covers happy paths, all expected error codes, schema validation (422), and lifespan wiring. These are the tests that actually matter.

The two issues to address before the milestone is fully done:

1. Either add a `PricingServiceUnavailableError` handler to `app.py`, or document explicitly that it is intentionally an internal exception that never escapes the service layer.
2. Remove `raise_server_exceptions=False` from `unavailable_client` and confirm the 503 test passes without it. If it does not pass, that points to a real handler registration bug worth fixing now.

Everything else in the suggestions section is optional improvement, not a blocker.

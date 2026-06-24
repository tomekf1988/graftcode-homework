# GraftCode SDK — Bugs Found During Implementation

Bugs discovered while building a two-service order/pricing system with Graftcode Gateway (gg) 1.3.0 on aarch64/Docker.

---

## Bug 1 — Vision WebSocket hardcoded to port 80

**Symptom**: Vision JS always connects to `ws://localhost/ws` (port 80), ignoring the host port mapping. If gg is mapped to any port other than 80 (e.g. `82:80`), the browser connects to whichever service owns port 80 on the host — not the intended service.

**Impact**: Makes it impossible to run two gg instances with working Vision on the same host without a reverse proxy. The second service's Vision silently talks to the wrong backend.

**Misleading side effect**: See Bug 3.

**Workaround**: Always map the WebSocket port to 80 on the host. Only one gg instance can use Vision at a time.

---

## Bug 2 — Nested hypertube initialization crash (gg-hosted service using graft client in inMemory mode)

**Symptom**: When a gg-hosted class internally instantiates a graft client configured for `host=inMemory`, hypertube tries to initialize a second runtime context inside gg's existing Python runtime. On any exception (including domain errors like `UnsupportedCustomerTypeError`), the error handler calls `HypertubeException()` without required arguments:

```
TypeError: HypertubeException.__init__() missing 2 required positional arguments: 'message' and 'traceback_str'
```

**Reproduction**:
1. gg hosts `OrderServiceGraft`
2. `OrderServiceGraft.__init__` creates `PricingServiceGraft(host="inMemory")`
3. Call any method → any exception from inside → TypeError

**Note**: The same graft client in inMemory mode works correctly when called from a plain Python script (outside gg). Domain errors are properly wrapped in `HypertubeException` with `.message` attribute. The conflict is specific to initialization inside an already-running gg Python runtime.

**Workaround**: Use remote mode (`host=ws://...`) inside gg-hosted services. InMemory mode works outside Docker via `make run-local`.

---

## Bug 3 — Misleading "No module named 'graft.X'" when Vision connects to wrong service

**Symptom**: Due to Bug 1, when Vision at port 83 connects to the service on port 80 (a different service), and a method is called that the wrong service doesn't know about, the error is:

```
ModuleNotFoundError: No module named 'graft.hello_graft'
```

**Impact**: The error looks like a Python import problem, not a connection problem. Debugging took several hours chasing non-existent import issues before identifying the root cause as the WebSocket port conflict.

**Root cause**: gg reports the module resolution failure when looking up `graft.<module_name>` in the wrong service's Python context.

---

## Bug 4 — Free-tier registry is ephemeral (package unavailable when gg is stopped)

**Symptom**: The graft client package install URL contains the gg instance GUID:

```
pip install --extra-index-url https://grft.dev/simple/<guid>__free graft-pypi-pricing-service-graft==0.1.0
```

The GUID changes on every gg restart. The registry URL becomes a 404 when the gg instance is stopped. `uv lock` fails because the registry is unavailable at lock time (gg not running).

**Impact**:
- `make setup` must be run while the corresponding gg container is running
- A fresh Docker build (`--no-cache`) after restarting gg will fail because the old GUID URL is dead
- Current Docker builds succeed only due to Docker layer caching
- `uv lock` cannot resolve the dependency at all

**Workaround**: Use `pip install` (not `uv`) during setup, and run it while gg is active. Document the URL in Makefile/Dockerfile from the active session.

**Note**: The project key (`--projectKey`) feature provides a stable permanent registry URL. This is a paid/registered feature.

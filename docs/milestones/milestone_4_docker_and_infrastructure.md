# Milestone 4 — Docker, Docker Compose, Makefile

## Status: pending

## Scope

- `order_service/Dockerfile` — same image for both LOCAL and REMOTE mode
- `pricing_service/Dockerfile` — installs `gg` (GraftCode Gateway), used in REMOTE only
- `docker-compose.yml` — LOCAL mode, single `order` container with `PRICING_MODE=local`
- `docker-compose.remote.yml` — REMOTE override, two containers
- `Makefile` — targets: `test`, `demo`, `run-local`, `run-remote`

## Notes

LOCAL mode: single container — Pricing runs in-process.
REMOTE mode: two containers — Pricing Service registers methods via `gg`.

## Details

See: `docs/plans/pre_graftcode_milestones.md` → Milestone 4.

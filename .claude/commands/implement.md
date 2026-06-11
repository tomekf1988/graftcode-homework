Read .claude/CLAUDE.md first.

Implement milestone: $ARGUMENTS

## Task tracking

At the start:
1. Read the milestone spec from docs/milestones/ (match by name or number)
2. Extract the scope items and acceptance criteria as tasks
3. Write them all to tasks/todo.md

During implementation:
- Move each task to tasks/in_progress.md when you start it
- Move each task to tasks/done.md when it is complete
- Never leave tasks/in_progress.md with stale entries — complete or revert them

## Agents

- Use python-dev agent for all backend work (models, migrations, repos, API, tests)
- Use react-dev agent for all frontend work (components, pages, hooks, streaming UI)

## Docker commands

Always use Docker — never run Python, pytest, or alembic directly on the host:
- `docker compose exec backend pytest` — run tests
- `docker compose exec backend alembic upgrade head` — run migrations manually
- `docker compose exec <service> <command>` — any other command
- `make up`, `make down`, `make logs` — for lifecycle

Tests must always run inside the container where the correct Python version,
virtualenv, and database connection are available.

## After implementation

1. Update the milestone doc (`docs/milestones/milestone_N_*.md`) to reflect what was actually built — actual decisions made, env var names, ports, deviations from the original spec, and any additions
2. Run `make down`
3. Run `docker compose up --build -d`
4. Run `docker compose logs --tail=50` to check for errors
5. If no ERROR/FATAL lines → startup OK; proceed
6. If errors found → fix and retry
7. Summarize completed work, technical decisions, and any tradeoffs
8. List remaining milestones

## Requirements

- Keep architecture simple, avoid overengineering
- Prefer readability over abstractions
- Add automated tests where reasonable
- Do not introduce unnecessary libraries or complex patterns

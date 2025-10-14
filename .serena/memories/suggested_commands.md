# Suggested Commands
- Environment setup: `just setup` (uv sync + optional .env).
- Run dev API: `just dev` (uv run uvicorn ...).
- Docker compose: `just up` / `just down` / `just rebuild`.
- Formatting & linting: `just format`, `just lint`.
- Testing: `just test` (all), or granular `just unit-test`, `just sdk-test`, `just intg-test`, `just e2e-test`; local quick pass `just local-test`.
- Demo workflow: `just demo` (runs `demo/example.py`).
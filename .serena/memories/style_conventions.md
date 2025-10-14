# Style & Conventions
- Python code formatted with Black (target py312) and linted by Ruff (E,F,I; ignores E501 for line length). Keep imports sorted (Ruff I).
- Use type hints throughout; async/await patterns common for clients; prefer Pydantic models for config/IO.
- Follow FastAPI best practices: route handlers in `api`, services encapsulate logic, nodes/graph implement LangGraph workflows.
- Documentation and dev-facing text written in English per repo rules. Keep agent-facing docs concise for token efficiency.
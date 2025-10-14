# Task Completion Checklist
- Run targeted tests via `just` recipes (e.g., `just unit-test`, `just sdk-test`) relevant to changes; include `just lint` or `just format` when touching Python code.
- Ensure FastAPI app still starts (`just dev`) if API changes.
- Update README/docs and version numbers when altering public interfaces or SDK behavior; align submodule updates with referenced versions.
- Summarize changes, note testing performed, and highlight any follow-up actions in final report.
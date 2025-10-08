#!/bin/sh

# Exit immediately if a command exits with a non-zero status ('e')
# or if an unset variable is used ('u').
set -eu

# --- Start Uvicorn server (or run another command) ---
# If arguments are passed to the script, execute them instead of the default server.
# This allows running commands like pytest.
if [ "$#" -gt 0 ]; then
    exec "$@"
else
    echo "Starting server on 0.0.0.0:8000..."
    # Use --reload in development, controlled by CONTAINER_ENV. Defaults to production behavior.
    if [ "${CONTAINER_ENV:-production}" = "development" ]; then
        exec uv run uvicorn ollama_deep_researcher.api.main:app \
            --host "0.0.0.0" \
            --port "8000" \
            --reload
    else
        exec uv run uvicorn ollama_deep_researcher.api.main:app \
            --host "0.0.0.0" \
            --port "8000"
    fi
fi

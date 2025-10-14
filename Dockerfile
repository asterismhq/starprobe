# syntax=docker/dockerfile:1.7-labs
# ==============================================================================
# Stage 1: Base
# - Base stage with uv setup and dependency files
# ==============================================================================
FROM python:3.12-slim as base

WORKDIR /app

# Install system dependencies including Git (required for Git-based dependencies)
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN --mount=type=cache,target=/root/.cache \
    pip install uv

# Copy dependency definition files
COPY pyproject.toml uv.lock ./


# ==============================================================================
# Stage 2: Production Dependencies
# - Creates a lean virtual environment with only production dependencies.
# ==============================================================================
FROM base as prod-deps

# Install only production dependencies
RUN --mount=type=cache,target=/root/.cache \
    uv sync --no-dev


# ==============================================================================
# Stage 3: Production
# - Creates the final, lightweight production image.
# - Copies the lean venv and only necessary application files.
# ==============================================================================
FROM python:3.12-slim AS production

# Install uv for running commands
RUN pip install uv

# Create a non-root user and group for security
RUN groupadd -r appgroup && useradd -r -g appgroup -d /home/appuser -m appuser

# Set the working directory
WORKDIR /app

# Grant ownership of the working directory to the non-root user
RUN chown appuser:appgroup /app

ENV PYTHONPATH="/app/src"

# Copy the lean virtual environment from the prod-deps stage
COPY --from=prod-deps --chown=appuser:appgroup /app/.venv ./.venv

# Set the PATH to include the venv's bin directory for simpler command execution
ENV PATH="/app/.venv/bin:${PATH}"

# Copy only the necessary application code and configuration, excluding tests
COPY --chown=appuser:appgroup src/ ./src
COPY --chown=appuser:appgroup pyproject.toml .
COPY --chown=appuser:appgroup entrypoint.sh .

# Grant execute permissions to the entrypoint script
RUN chmod +x entrypoint.sh

# Switch to the non-root user
USER appuser

# Expose the port the app runs on (will be mapped by Docker Compose)
EXPOSE 8000

# Healthcheck using only Python's standard library to avoid extra dependencies
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys, urllib.request; sys.exit(0) if urllib.request.urlopen('http://localhost:8000/health').getcode() == 200 else sys.exit(1)"

# Set the entrypoint script to be executed when the container starts
ENTRYPOINT ["/app/entrypoint.sh"]
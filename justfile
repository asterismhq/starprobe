# ==============================================================================
# justfile for FastAPI Project Automation
# ==============================================================================

set dotenv-load

PROJECT_NAME := env("OLM_D_RCH_PROJECT_NAME", "olm-d-rch")
HOST_IP := env("OLM_D_RCH_BIND_IP", "127.0.0.1")
DEV_PORT := env("OLM_D_RCH_DEV_PORT", "8001")

# default target
default: help

# Show available recipes
help:
    @echo "Usage: just [recipe]"
    @echo "Available recipes:"
    @just --list | tail -n +2 | awk '{printf "  \033[36m%-20s\033[0m %s\n", $1, substr($0, index($0, $2))}'

# ==============================================================================
# Environment Setup
# ==============================================================================

# Initialize project: install dependencies, create .env file and pull required Docker images
setup:
    @echo "Installing python dependencies with uv..."
    @uv sync
    @echo "Creating environment file..."
    @if [ ! -f .env ] && [ -f .env.example ]; then \
        echo "Creating .env from .env.example..."; \
        cp .env.example .env; \
        echo "✅ Environment file created (.env)"; \
    else \
        echo ".env already exists. Skipping creation."; \
    fi
    @echo "💡 You can customize .env for your specific needs:"

# ==============================================================================
# Development Environment Commands
# ==============================================================================

# Run local development server (no Docker)
dev:
    @echo "Starting local development server..."
    @uv run uvicorn olm_d_rch.api.main:app --reload --host {{HOST_IP}} --port {{DEV_PORT}}

# Start production-like environment with Docker Compose
up:
    @docker compose up -d

# Stop Docker Compose environment
down:
    @docker compose down --remove-orphans

# Rebuild and restart the Docker service
rebuild:
    @echo "Rebuilding and restarting service..."
    @docker compose down --remove-orphans
    @docker compose build --no-cache {{PROJECT_NAME}}

# ==============================================================================
# CODE QUALITY
# ==============================================================================

# Format code using Black and fix issues with Ruff
format:
	@uv run black .
	@uv run ruff check . --fix

# Perform static code analysis using Black and Ruff
lint:
  @uv run black --check .
  @uv run ruff check .

# ==============================================================================
# TESTING
# ==============================================================================

# Run all tests
test: unit-test intg-test build-test e2e-test 
    @echo "✅ All tests passed!"

local-test: 
    @just unit-test
    @just sdk-test
    @just intg-test
    @echo "✅ All local tests passed!"

# Run unit tests
unit-test:
    @echo "🚀 Running unit tests..."
    @uv run pytest tests/unit

# Run SDK tests
sdk-test:
    @echo "🚀 Running SDK tests..."
    @uv run pytest tests/sdk

# Run integration tests 
intg-test:
    @echo "🚀 Running integration tests..."
    @uv run pytest tests/intg

docker-test: 
    @just build-test
    @just e2e-test
    @echo "✅ All Docker tests passed!"

# Build Docker image for testing without leaving artifacts
build-test:
    @echo "Building Docker image for testing..."
    @TEMP_IMAGE_TAG=$(date +%s)-build-test; \
    docker build --target production --tag temp-build-test:$TEMP_IMAGE_TAG . && \
    echo "Build successful. Cleaning up temporary image..." && \
    docker rmi temp-build-test:$TEMP_IMAGE_TAG || true

# Run e2e tests
e2e-test:
    @echo "🚀 Running e2e tests..."
    @uv run pytest tests/e2e

# ==============================================================================
# CLEANUP
# ==============================================================================

# Remove __pycache__ and .venv to make project lightweight
clean:
  @echo "🧹 Cleaning up project..."
  @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
  @rm -rf .venv
  @rm -rf .pytest_cache
  @rm -rf .ruff_cache
  @rm -f test_db.sqlite3
  @echo "✅ Cleanup completed"

# ==============================================================================
# DEMO
# ==============================================================================

# Run demo script
demo:
    @uv run demo/example.py
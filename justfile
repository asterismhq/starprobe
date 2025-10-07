# ==============================================================================
# justfile for FastAPI Project Automation
# ==============================================================================

set dotenv-load 

PROJECT_NAME := env("PROJECT_NAME", "fastapi-sandbox")

DEV_PROJECT_NAME := PROJECT_NAME + "-dev"
TEST_PROJECT_NAME := PROJECT_NAME + "-test"

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

# Start development environment with Docker Compose
up:
  @docker-compose -f docker-compose.yml -f docker-compose.dev.override.yml up -d

# Stop development environment
down:
  @docker-compose down

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

# Run all tests in isolated Docker environment
test:
  @docker-compose -f docker-compose.yml -f docker-compose.test.override.yml run --rm research-api

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
run-demo:
    @uv run demo/example.py
# Starprobe API

## Overview

Starprobe API is an AI agent that autonomously conducts detailed research on a specified topic and generates a comprehensive report. It starts with initial research, identifies knowledge gaps, and iteratively refines the summary through additional investigations. It delegates LLM invocation to the Nexus API service.

## Architecture and Workflow

The agent's logic is built as a state machine using LangGraph. It repeats the following cycle:

1.  **Query Generation**: Creates initial search queries from the user's topic.
2.  **Web Research**: Performs searches using `DuckDuckGo` and extracts content with `ScrapingService`.
3.  **Summarization**: Integrates research results into the existing summary.
4.  **Evaluation and Reflection**: Assesses knowledge gaps in the summary and generates new search queries if necessary.
5.  **Completion Decision**: Decides whether to continue research (up to the maximum loop count) or generate the final report and end the process.

## Main Components

-   **`dependencies.py`**: Dependency injection that provides services and clients. Uses `USE_MOCK_*` env vars to toggle between real and mock implementations. Instantiates the nexus SDK directly with `response_format="langchain"`.
-   **Services (`services/`)**:
    -   `ResearchService`: Manages searching and scraping.
    -   `PromptService`: Generates LLM prompts.
    -   `ScrapingService`: Extracts content from URLs.
-   **Clients (`clients/`)**:
    -   `DdgsClient`: Performs DuckDuckGo web searches using the `ddgs` library.
-   **State (`state.py`)**:
    -   `SummaryState`: Shares information such as topics, queries, and summaries between states.

## Usage

### Running Demo Locally

-   Run `just demo`.
-   Change `research_topic` in `demo/example.py` to research any topic.
-   Results are saved to `demo/example.md`.

### Running via API

**Local Development (Recommended):**
-   Start local server: `just dev` (runs on port 8001)
-   Send POST request to `/research` endpoint

**Production-like Environment (Docker):**
-   Start container: `just up`
-   Send POST request to `/research` endpoint

**LLM Configuration:**
-   LLM invocation is delegated to the Nexus API service.
-   Configure the Nexus endpoint via `NEXUS_BASE_URL` (default: `http://localhost:8000`).
-   Backend selection (Ollama/MLX) is configured at the Nexus service level, not in this project.
-   Requires Nexus service to be running and accessible.

## Configuration Management

Non-sensitive configuration values are defined as defaults in `settings.py`. Only environment-specific values like API keys or port numbers should be in the `.env` file.

-   **Application & Deployment**: `.env` (ports, project names, etc.)
-   **Application & Testing**: `settings.py` (model names, timeouts, etc.)

## 📦 Submodules

This project uses Git submodules to manage external dependencies. Submodules are located in the `submodules/` directory and should never be edited directly. If changes are required, please contact the respective repository maintainers or request updates from the user.

### nexus (submodules/nexus)
Provides a unified interface for connecting to various Large Language Models, handling authentication, and managing API interactions as the Nexus for LLM integration.

## Development Notes

-   **nexus submodule**: We now edit `submodules/nexus` in tandem with this repo to keep SDK changes synchronized. Ensure version numbers stay aligned (`pyproject.toml` references the latest version).
-   **Dependencies**: Actual libraries used in production are installed from Git repositories specified in `pyproject.toml`. Keep the git reference updated when releasing a new nexus version.

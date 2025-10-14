# Ollama Deep Researcher Agent

## Overview

**Ollama Deep Researcher** is an AI agent that autonomously conducts detailed research on a specified topic and generates a comprehensive report. It starts with initial research, identifies knowledge gaps, and iteratively refines the summary through additional investigations. It delegates LLM invocation to the **Stella Connector** API service.

---

## Architecture and Workflow

The agent's logic is built as a state machine using **LangGraph**. It repeats the following cycle:

1.  **Query Generation**: Creates initial search queries from the user's topic.
2.  **Web Research**: Performs searches using `DuckDuckGo` and extracts content with `ScrapingService`.
3.  **Summarization**: Integrates research results into the existing summary.
4.  **Evaluation and Reflection**: Assesses knowledge gaps in the summary and generates new search queries if necessary.
5.  **Completion Decision**: Decides whether to continue research (up to the maximum loop count) or generate the final report and end the process.

---

## Main Components

-   **`dependencies.py`**: Dependency injection that provides services and clients. Uses `USE_MOCK_*` env vars to toggle between real and mock implementations.
-   **Services (`services/`)**:
    -   `ResearchService`: Manages searching and scraping.
    -   `PromptService`: Generates LLM prompts.
    -   `ScrapingService`: Extracts content from URLs.
-   **Clients (`clients/`)**:
    -   `StlConnClient`: LLM client from Stella Connector SDK (imported from `stl-conn` package).
    -   `DdgsClient`: Performs DuckDuckGo web searches using the `ddgs` library.
-   **State (`state.py`)**:
    -   `SummaryState`: Shares information such as topics, queries, and summaries between states.

---

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
-   LLM invocation is delegated to the Stella Connector API service.
-   Configure the Stella Connector endpoint via `STL_CONN_BASE_URL` (default: `http://localhost:8000`).
-   Backend selection (Ollama/MLX) is configured at the Stella Connector service level, not in this project.
-   Requires Stella Connector service to be running and accessible.

---

## Configuration Management

Non-sensitive configuration values are defined as defaults in `settings.py`. Only environment-specific values like API keys or port numbers should be in the `.env` file.

-   **Application & Deployment**: `.env` (ports, project names, etc.)
-   **Application & Testing**: `settings.py` (model names, timeouts, etc.)

---

## Development Notes

-   **Submodules are read-only**: Code in `submodules/` is for reference only. Do not modify submodule code.
-   **Dependencies**: Actual libraries used in production are installed from Git repositories specified in `pyproject.toml`, not from local submodules.

---

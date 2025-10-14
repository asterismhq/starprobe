# Ollama Deep Researcher Agent

## Overview

**Ollama Deep Researcher** is an AI agent that autonomously conducts detailed research on a specified topic and generates a comprehensive report. It starts with initial research, identifies knowledge gaps, and iteratively refines the summary through additional investigations. It primarily targets local LLM backends (Ollama by default, MLX on Apple Silicon) to minimize dependence on paid APIs.

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

-   **`container.py`**: A dependency container that selects production or mock services using `USE_MOCK_*` env vars and supplies LLM clients via `provide_llm_client(backend)`.
-   **Services (`services/`)**:
    -   `ResearchService`: Manages searching and scraping.
    -   `PromptService`: Generates LLM prompts.
    -   `ScrapingService`: Extracts content from URLs.
-   **Clients (`clients/`)**:
    -   `OllamaClient` / `MLXClient`: Implement the shared `LLMClientProtocol`.
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
-   Default backend is controlled by `OLM_D_RCH_LLM_BACKEND` (`ollama` or `mlx`).
-   Requests can override the backend by setting `"backend": "ollama"|"mlx"` in the payload.
-   For Ollama, run `ollama serve` and set `OLLAMA_HOST`. For MLX, ensure `mlx-lm` is available on Apple Silicon.

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

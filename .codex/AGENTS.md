# Ollama Deep Researcher Agent

## Overview

**Ollama Deep Researcher** is an AI agent that autonomously conducts detailed research on a specified topic and generates a comprehensive report. It starts with initial research, identifies knowledge gaps, and iteratively refines the summary through additional investigations. It is optimized for local LLMs running on **Ollama**, minimizing dependence on paid APIs.

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

-   **`container.py`**: A dependency container that switches between production and mock services based on the `DEBUG` environment variable.
-   **Services (`services/`)**:
    -   `ResearchService`: Manages searching and scraping.
    -   `PromptService`: Generates LLM prompts.
    -   `ScrapingService`: Extracts content from URLs.
-   **Clients (`clients/`)**:
    -   `OllamaClient`: Communicates with the Ollama LLM.
    -   `DuckDuckGoClient`: Performs web searches.
-   **State (`state.py`)**:
    -   `SummaryState`: Shares information such as topics, queries, and summaries between states.

---

## Usage

### Running Demo Locally

-   Run `just run-demo`.
-   Change `research_topic` in `demo/example.py` to research any topic.
-   Results are saved to `demo/example.md`.

### Running via API

-   Start the server with `just start-dev-server`.
-   Send a POST request to the `/research` endpoint with the following JSON body:
    ```json
    {"research_topic": "your topic to research"}
    ```

**Docker & Ollama Configuration**
-   The Ollama container is used only in CI. For local use, run `ollama serve`.
-   `OLLAMA_HOST` is `http://ollama:11434/` inside the container and `http://host.docker.internal:11434` locally.

---

## Configuration Management

To prevent unintended overwrites, non-sensitive configuration values are defined as defaults in `settings.py`. Only environment-specific values like API keys or port numbers should be described in the `.env` file.

-   **Application & Deployment**: `.env` (ports, project names, etc.)
-   **Application & Testing**: `settings.py` (model names, timeouts, etc.)
-   **Infrastructure**: Docker Compose files (environment sections, etc.)
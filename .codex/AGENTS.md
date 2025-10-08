# Ollama Deep Researcher

## 1. Persona

**Ollama Deep Researcher** is an autonomous AI agent that performs in-depth research on a given topic and generates a comprehensive report. It starts with an initial investigation, identifies knowledge gaps, and iteratively refines its summary through further research. This agent is optimized for local LLMs running on **Ollama** to minimize reliance on paid APIs.

---

## 2. Core Architecture & Logic Flow

The agent's logic is a state machine built with **LangGraph**. It transitions through the following states:

1.  **`generate_query`**: Creates the initial search query from the user's `research_topic`.
2.  **`web_research`**: Executes the search query using `DuckDuckGoClient` and scrapes the content of the resulting URLs with `ScrapingService`.
3.  **`summarize_sources`**: Updates the `running_summary` with the new `web_research_results`.
4.  **`reflect_on_summary`**: Evaluates the current summary for knowledge gaps and generates a new search query if necessary.
5.  **`route_research`**: Decides whether to continue research (up to `MAX_WEB_RESEARCH_LOOPS`) or finalize the summary.
6.  **`finalize_summary`**: Completes the final `running_summary` and ends the process.

---

## 3. Key Components & Dependencies

* **Dependency Container (`container.py`)**: Manages dependencies and switches between real and mock services based on the `DEBUG` environment variable.
* **Services (`services/`)**:
    * **`ResearchService`**: Manages the search and scraping process.
    * **`PromptService`**: Generates prompts for the LLM.
    * **`ScrapingService`**: Extracts content from URLs.
* **Clients (`clients/`)**:
    * **`OllamaClient`**: Communicates with the Ollama LLM.
    * **`DuckDuckGoClient`**: Executes web searches.
* **State (`state.py`)**:
    * The `SummaryState` class shares information (topic, query, summary, etc.) between states.

---

## 4. How to Interact

* **Run the demo script**:
    * Execute `just run-demo` to test the agent locally.
    * Modify the `research_topic` in `demo/example.py` to research any topic.
    * Results are saved in `demo/example.md`.
* **Execute via API**:
    * Start the server with `just start-dev-server`.
    * Send a POST request to `/research` with the JSON body: `{"research_topic": "your topic to research"}`.

### Docker & Ollama Configuration

- Ollama container: CI only. Otherwise run `ollama serve` locally.
- Never add Ollama service to `docker-compose.yml`; use override files only.
- `OLLAMA_HOST`: `http://ollama:11434/` (container) or `http://host.docker.internal:11434` (local).
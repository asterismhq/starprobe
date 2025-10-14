# Ollama Deep Researcher API

Ollama Deep Researcher is a fully local web research and summarization API service that leverages pluggable local LLM backends (Ollama by default, MLX on Apple Silicon). Given a topic, it autonomously generates web search queries, collects and summarizes search results, and iteratively conducts additional research to fill knowledge gaps, ultimately providing a final summary and reference sources.

## 🏗️ Architecture Overview

The project introduces a Dependency Injection (DI) container called `DependencyContainer` to manage dependencies. The project is primarily composed of components such as `graph`, `nodes`, `services`, and `clients`.

## What's New

- **stl-conn SDK v1.2.0** is now consumed directly: LangChain message inputs and tool binding are handled in the SDK, allowing this project to drop its local adapter wrapper.

### Stella Connector Integration

The application now consumes the **stl-conn SDK v1.2.0** directly. The LangChain adapter layer that previously lived in this repo has been removed because the SDK now:

- Accepts LangChain message objects (`AIMessage`, `HumanMessage`, etc.) without extra serialization.
- Exposes `bind_tools()` on both real and mock clients so LangChain tool calling can be chained natively.
- Automatically wraps payloads under the expected `{"input": ...}` structure while forwarding bound tools.

## 🚀 Quick Start

### Local Development (Recommended)

1. **Clone and setup:**

    ```shell
    git clone https://github.com/langchain-ai/olm-d-rch.git
    cd olm-d-rch
    just setup
    ```

2. **Start Ollama:**

    ```shell
    ollama serve
    ```

3. **Run the service:**

    ```shell
    just dev
    ```

4. **Verify the service:**

   ```shell
   curl http://localhost:8001/health
   ```

### Docker Deployment

1. **Build and run:**

    ```shell
    docker build -t olm-d-rch-api .
    docker run --rm -it -p 8000:8000 \
      -e OLLAMA_HOST="http://host.docker.internal:11434" \
      -e OLM_D_RCH_OLLAMA_MODEL="llama3.2:3b" \
      olm-d-rch-api
    ```

2. **Or use docker compose:**

    ```shell
    just up
    ```

## 🎯 Running the Demo

```shell
just demo
```

This executes `demo/example.py` and saves results to `demo/example.md`.

## ⚙️ API Usage

Once the service is running, the following endpoints are available.

### Perform Research

  * **Endpoint:** `POST /research`
  * **Description:** Performs detailed research on the specified query and returns a ready-to-use Markdown article.
  * **Request Body:**
    ```json
    {
      "query": "YOUR_RESEARCH_QUERY",
      "backend": "ollama"
    }
    ```
    - `query` (string, required): The topic or search query to investigate. Must be at least 1 character long.
    - `backend` (string, optional): LLM backend to use for this request. Supported values are `ollama` and `mlx`. When omitted, the server uses the default backend from configuration.
  * **Example using `curl`:**
    ```shell
    curl -X POST http://localhost:8000/research \
    -H "Content-Type: application/json" \
    -d '{"query": "The future of renewable energy"}'
    ```
  * **Response (on success):**
    ```json
    {
      "success": true,
      "article": "# Sample Article\n...",
      "metadata": {
        "sources": [
          "https://example.com/source1",
          "https://example.com/source2"
        ],
        "source_count": 2
      },
      "diagnostics": [],
      "processing_time": 12.34,
      "error_message": null
    }
    ```
    - `success` (boolean): Indicates whether the research completed successfully.
    - `article` (string or null): The generated Markdown article that can be persisted directly.
    - `metadata` (object or null): Additional structured data such as source listings or counts.
    - `diagnostics` (array of strings): Warnings or informational messages collected during execution.
    - `error_message` (string or null): Error details if the research failed.

  * **Example using `curl` with MLX backend override:**
    ```shell
    curl -X POST http://localhost:8000/research \
    -H "Content-Type: application/json" \
    -d '{"query": "Foundation models optimized for Apple Silicon", "backend": "mlx"}'
    ```
  * **Response (on failure/timeout):**
    ```json
    {
        "success": false,
        "article": null,
        "metadata": null,
        "diagnostics": [],
        "error_message": "Research request exceeded 5-minute timeout"
    }
    ```

### Selecting an LLM Backend

- Set `OLM_D_RCH_LLM_BACKEND` in your environment to define the default backend (`ollama` or `mlx`).
- Override the backend for a single request by providing the optional `backend` field in the `POST /research` payload.
- When using the MLX backend, ensure you are on Apple Silicon with [`mlx-lm`](https://pypi.org/project/mlx-lm/) installed or enable `USE_MOCK_MLX=true` for testing.

### Health Check

  * **Endpoint:** `GET /health`
  * **Description:** Checks the service status. Useful for load balancers, etc.
  * **Example using `curl`:**
    ```shell
    curl http://localhost:8000/health
    ```
  * **Response:**
    ```json
    {
      "status": "ok"
    }
    ```
    - `status` (string): The health status of the service, typically "ok".

## 🛠️ Configuration via Environment Variables

The application's behavior can be controlled via the following environment variables at container startup.

### API Configuration

  * `OLM_D_RCH_BIND_IP`: IP address to bind the API server to. Default is `127.0.0.1`.
  * `OLM_D_RCH_BIND_PORT`: Port to bind the API server to. Default is `8000`.
  * `OLM_D_RCH_PROJECT_NAME`: Name of the project. Default is `olm-d-rch`.

### LLM Backend Configuration

  * `OLM_D_RCH_LLM_BACKEND`: Default backend used when a request does not specify one. Valid options are `ollama` and `mlx`. Default is `ollama`.

### Ollama Configuration

  * `OLLAMA_HOST`: (Required when using the Ollama backend) The endpoint URL for the Ollama API.
  * `OLM_D_RCH_OLLAMA_MODEL`: The name of the Ollama model to use for research. Default is `llama3.2:3b`.

### MLX Configuration

  * `OLM_D_RCH_MLX_MODEL`: Default MLX model identifier. Recommended default is `mlx-community/Llama-3.1-8B-Instruct-4bit`.
  * `USE_MOCK_MLX`: When set to `true`, the MLX mock client is used instead of the real implementation (helpful for CI or when MLX is unavailable).

### Workflow Configuration

  * `max_web_research_loops`: Number of research iterations to perform. Default is `3`.
  * `strip_thinking_tokens`: Whether to strip `<think>` tokens from model responses. Default is `true`.
  * `use_tool_calling`: Use tool calling instead of JSON mode for structured output. Default is `false`.
  * `max_tokens_per_source`: Maximum number of tokens to include for each source's content. Default is `1000`.

### Scraping Configuration

  * `SCRAPING_TIMEOUT_CONNECT`: Timeout for connecting to scraping targets in seconds. Default is `30`.
  * `SCRAPING_TIMEOUT_READ`: Timeout for reading from scraping targets in seconds. Default is `90`.

### DuckDuckGo Search Configuration

The service uses DuckDuckGo for web searches via the [`ddgs`](https://pypi.org/project/ddgs/) Python library. The following optional environment variables allow you to customize search behavior:

  * `DDGS_REGION`: Region code for DuckDuckGo search (e.g., `wt-wt` for global, `us-en` for US). Default is `wt-wt`.
  * `DDGS_SAFESEARCH`: SafeSearch level for DuckDuckGo. Options are `off`, `moderate`, or `strict`. Default is `moderate`.
  * `DDGS_MAX_RESULTS`: Maximum number of results to fetch from DuckDuckGo per query. Default is `10`.

### Mock Configuration

For testing and development, you can enable mock implementations for various components:

  * `USE_MOCK_OLLAMA`: Use mock Ollama client instead of real implementation. Default is `false`.
  * `USE_MOCK_MLX`: Use mock MLX client instead of real implementation. Default is `false`.
  * `USE_MOCK_SEARCH`: Use mock search client instead of real DuckDuckGo search. Default is `false`.
  * `USE_MOCK_SCRAPING`: Use mock scraping service instead of real web scraping. Default is `false`.

## SDK

This repository includes a Python SDK for interacting with the olm-d-rch API.

### Installation

To install the SDK, add it as a dependency using Poetry:

```bash
poetry install --extras sdk
```

### Usage

```python
from olm_d_rch_sdk import ResearchApiClient

client = ResearchApiClient(base_url="http://localhost:8001")
response = client.research(topic="Example research topic")
print(response.article)
```

## 🧪 Testing

The project includes comprehensive test coverage across multiple test types:

### Test Organization

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
  - `services/`: Tests for all service classes (PromptService, ResearchService, SearchService, ScrapingService, TextProcessingService)
  - `clients/`: Tests for client classes (OllamaClient, MLXClient, DdgsClient)
- **Mock Tests** (`tests/mock/`): Tests for mock implementations and dependency container
- **Integration Tests** (`tests/intg/`): End-to-end tests with real workflows

### Running Tests

```shell
# Run all tests (unit, mock, integration, and build)
just test

# Run only unit tests (no external dependencies required)
just unit-test

# Run only mock tests
just mock-test

# Run only integration tests (requires Ollama)
just intg-test

# Or use pytest directly for more control
pytest tests/unit/ -v
pytest tests/ --cov=src/ollama_deep_researcher --cov-report=html
```

## Troubleshooting

### Manual Verification

To verify the service is working correctly with DuckDuckGo search:

1. **Start the service** using Docker or locally
2. **Send a test research request** to `/research`:
   ```shell
   curl -X POST http://localhost:8000/research \
   -H "Content-Type: application/json" \
   -d '{"query": "quantum computing applications"}'
   ```
3. **Monitor the logs** to confirm DuckDuckGo search executes successfully
4. **Verify the response** contains sources with DuckDuckGo search result URLs

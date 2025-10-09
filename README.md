# Ollama Deep Researcher API

Ollama Deep Researcher is a fully local web research and summarization API service that leverages LLMs hosted by Ollama. Given a topic, it autonomously generates web search queries, collects and summarizes search results, and iteratively conducts additional research to fill knowledge gaps, ultimately providing a final summary and reference sources.

## 🏗️ Architecture Overview

The project introduces a Dependency Injection (DI) container called `DependencyContainer` to manage dependencies. The `RESEARCH_API_DEBUG` flag allows switching between production implementations and mock implementations at the DI container level. The project is primarily composed of components such as `graph`, `nodes`, `services`, and `clients`.

## 🚀 Quick Start

This service is designed to run as a Docker container.

1. **Clone the repository:**

    ```shell
    git clone https://github.com/langchain-ai/ollama-deep-researcher.git
    cd ollama-deep-researcher
    ```

2. **Build the Docker image:**

    ```shell
    docker build -t ollama-deep-researcher-api .
    ```

3. **Run the Docker container:**

    To run the service, Ollama must be accessible over the network. The following command is an example of connecting to Ollama running on the host machine.

    ```shell
    docker run --rm -it -p 8000:8000 \
      -e OLLAMA_HOST="http://host.docker.internal:11434" \
      -e RESEARCH_API_OLLAMA_MODEL="llama3.2:3b" \
      ollama-deep-researcher-api
    ```

      * `OLLAMA_HOST`: Specifies the endpoint of the Ollama service.
      * `RESEARCH_API_OLLAMA_MODEL`: Specifies the model name to use.

4. **Verify the service is running:**

   You can send a request to the `/health` endpoint to confirm the API is running. This is the simplest way to check if the container has started successfully.

   ```shell
   curl http://localhost:8000/health
   ```
   *Note: If you changed the port using the `RESEARCH_API_BIND_PORT` environment variable (e.g., to `8001`), replace `8000` with your chosen port.*

   A successful response will look like this:
   ```json
   {"status":"ok"}
   ```

## 🎯 Running the Demo

You can run the demo script using the `just run-demo` command. This executes `demo/example.py` and saves the results in Markdown format to `demo/example.md`.

## ⚙️ API Usage

Once the service is running, the following endpoints are available.

### Perform Research

  * **Endpoint:** `POST /api/v1/research`
  * **Description:** Performs detailed research on the specified topic.
  * **Request Body:**
    ```json
    {
      "topic": "YOUR_RESEARCH_TOPIC"
    }
    ```
    - `topic` (string, required): The research topic to investigate. Must be at least 1 character long.
  * **Example using `curl`:**
    ```shell
    curl -X POST http://localhost:8000/api/v1/research \
    -H "Content-Type: application/json" \
    -d '{"topic": "The future of renewable energy"}'
    ```
  * **Response (on success):**
    ```json
    {
      "success": true,
      "summary": "## Summary\n...",
      "sources": [
        "https://example.com/source1",
        "https://example.com/source2"
      ],
      "error_message": null
    }
    ```
    - `success` (boolean): Indicates whether the research completed successfully.
    - `summary` (string or null): The generated research summary in Markdown format.
    - `sources` (array of strings): List of source URLs used in the research.
    - `error_message` (string or null): Error details if the research failed.
  * **Response (on failure/timeout):**
    ```json
    {
        "success": false,
        "summary": null,
        "sources": [],
        "error_message": "Research request exceeded 5-minute timeout"
    }
    ```

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

  * `OLLAMA_HOST`: (Required) The endpoint URL for the Ollama API.
  * `RESEARCH_API_OLLAMA_MODEL`: The name of the Ollama model to use for research. Default is `llama3.2:3b`.
  * `SCRAPING_TIMEOUT_CONNECT`: Timeout for connecting to scraping targets. Default is 30 seconds.
  * `SCRAPING_TIMEOUT_READ`: Timeout for reading from scraping targets. Default is 90 seconds.
  * `RESEARCH_API_DEBUG`: If set to `true`, the application will use mock objects instead of connecting to external services like Ollama server, allowing for testing without actual dependencies.

### DuckDuckGo Search Configuration (Optional)

The service uses DuckDuckGo for web searches via the [`ddgs`](https://pypi.org/project/ddgs/) Python library. The following optional environment variables allow you to customize search behavior:

  * `DDGS_REGION`: Region code for DuckDuckGo search (e.g., `wt-wt` for global, `us-en` for US). Default is `wt-wt`.
  * `DDGS_SAFESEARCH`: SafeSearch level for DuckDuckGo. Options are `off`, `moderate`, or `strict`. Default is `moderate`.
  * `DDGS_MAX_RESULTS`: Maximum number of results to fetch from DuckDuckGo per query. Default is `10`.

## 🧪 Testing

The project includes comprehensive test coverage across multiple test types:

### Test Organization

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
  - `services/`: Tests for all service classes (PromptService, ResearchService, SearchService, ScrapingService, TextProcessingService)
  - `clients/`: Tests for client classes (OllamaClient, DdgsClient)
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
2. **Send a test research request** to `/api/v1/research`:
   ```shell
   curl -X POST http://localhost:8000/api/v1/research \
   -H "Content-Type: application/json" \
   -d '{"topic": "quantum computing applications"}'
   ```
3. **Monitor the logs** to confirm DuckDuckGo search executes successfully
4. **Verify the response** contains sources with DuckDuckGo search result URLs
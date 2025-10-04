# Ollama Deep Researcher API

Ollama Deep Researcher is a fully local web research and summarization API service that leverages LLMs hosted by Ollama. Given a topic, it autonomously generates web search queries, collects and summarizes search results, and iteratively conducts additional research to fill knowledge gaps, ultimately providing a final summary and reference sources.

## 🏗️ Architecture Overview

The project introduces a Dependency Injection (DI) container called `DependencyContainer` to manage dependencies. The `DEBUG` flag allows switching between production implementations and mock implementations at the DI container level. The project is primarily composed of components such as `graph`, `nodes`, `services`, and `clients`.

## 🚀 Quick Start

This service is designed to run as a Docker container.

1. **Clone the repository:**

    ```shell
    git clone https://github.com/langchain-ai/local-deep-researcher.git
    cd local-deep-researcher
    ```

2. **Build the Docker image:**

    ```shell
    docker build -t ollama-deep-researcher-api .
    ```

3. **Run the Docker container:**

    To run the service, Ollama must be accessible over the network. The following command is an example of connecting to Ollama running on the host machine.

    ```shell
    docker run --rm -it -p 8000:8000 \
      -e OLLAMA_BASE_URL="http://host.docker.internal:11434" \
      -e LLM_MODEL="llama3.2" \
      ollama-deep-researcher-api
    ```

      * `OLLAMA_BASE_URL`: Specifies the endpoint of the Ollama service.
      * `LLM_MODEL`: Specifies the model name to use.

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

## 🛠️ Configuration via Environment Variables

The application's behavior can be controlled via the following environment variables at container startup.

  * `OLLAMA_BASE_URL`: (Required) The endpoint URL for the Ollama API. Default is `http://localhost:11434/`.
  * `LLM_MODEL`: (Required) The name of the Ollama model to use for research. Default is `llama3.2:3b`.
  * `SCRAPING_TIMEOUT_CONNECT`: Timeout for connecting to scraping targets. Default is 10 seconds.
  * `SCRAPING_TIMEOUT_READ`: Timeout for reading from scraping targets. Default is 30 seconds.
  * `DEBUG`: If set to `true`, the application will use mock objects instead of connecting to external services like Ollama server, allowing for testing without actual dependencies.

## 🧪 Testing

The project includes both mock tests and integration tests. You can run specific test suites using commands like `just mock-test` for mock tests and `just intg-test` for integration tests.
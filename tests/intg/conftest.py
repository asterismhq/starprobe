import os
import subprocess
import sys
import time
from typing import AsyncGenerator

import httpx
import pytest
from dotenv import load_dotenv

# Load .env file to get port configuration
load_dotenv()

TEST_HOST = os.getenv("OLM_D_RCH_BIND_IP", "127.0.0.1")
TEST_PORT = int(os.getenv("OLM_D_RCH_PORT", "8080"))


@pytest.fixture
def api_config():
    """Provide API configuration for integration tests."""
    return {
        "base_url": f"http://{TEST_HOST}:{TEST_PORT}",
        "research_url": f"http://{TEST_HOST}:{TEST_PORT}/research",
        "health_url": f"http://{TEST_HOST}:{TEST_PORT}/health",
    }


@pytest.fixture
async def http_client(api_config) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an async HTTP client for making requests to the API."""
    async with httpx.AsyncClient(
        base_url=api_config["base_url"], timeout=300.0
    ) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def start_server():
    process = None
    try:
        # Start server in subprocess instead of thread for proper cleanup
        # Prepare environment variables for subprocess
        env = os.environ.copy()
        env["USE_MOCK_OLLAMA"] = "True"
        env["USE_MOCK_MLX"] = "True"
        env["USE_MOCK_SEARCH"] = "True"
        env["USE_MOCK_SCRAPING"] = "True"

        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "olm_d_rch.api.main:app",
                "--host",
                TEST_HOST,
                "--port",
                str(TEST_PORT),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

        # Wait for server to be ready by polling health endpoint
        max_attempts = 10
        attempt = 0
        health_url = f"http://{TEST_HOST}:{TEST_PORT}/health"
        while attempt < max_attempts:
            try:
                response = httpx.get(health_url, timeout=1.0)
                if response.status_code == 200:
                    break
            except httpx.RequestError:
                pass
            time.sleep(0.5)
            attempt += 1
        else:
            if process:
                process.terminate()
            raise RuntimeError("Server did not start within expected time")

        yield

    finally:
        # Cleanup: terminate the server process
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

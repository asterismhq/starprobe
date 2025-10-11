"""
E2E test specific fixtures.
This file contains the e2e_setup fixture that manages the Docker Compose environment for E2E tests.
"""

import os
import subprocess
import time
from typing import AsyncGenerator, Generator

import httpx
import pytest


@pytest.fixture
async def http_client(api_config) -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Fixture to provide an async HTTP client for making requests to the API.

    This fixture creates an httpx.AsyncClient with appropriate timeout settings
    for testing against the running Docker Compose services.
    """
    async with httpx.AsyncClient(
        base_url=api_config["base_url"], timeout=300.0
    ) as client:
        yield client


@pytest.fixture
def api_config():
    """
    Fixture to provide consistent API configuration for E2E tests.

    Returns configuration with fixed endpoint URLs and model name
    to ensure consistent testing across all E2E tests.
    """
    host_port = os.getenv("TEST_PORT", "8002")
    model_name = os.getenv("OLM_D_RCH_OLLAMA_MODEL", "llama3.2:3b").split(",")[0]

    return {
        "base_url": f"http://localhost:{host_port}",
        "research_url": f"http://localhost:{host_port}/research",
        "health_url": f"http://localhost:{host_port}/health",
        "model_name": model_name,
    }


@pytest.fixture(scope="session", autouse=True)
def e2e_setup() -> Generator[None, None, None]:
    """
    Manages the lifecycle of the application for end-to-end testing.
    This fixture is automatically invoked for all tests in the 'e2e/api' directory.
    """
    host_bind_ip = os.getenv("HOST_BIND_IP", "127.0.0.1")
    test_port = os.getenv("TEST_PORT", "8002")
    health_url = f"http://{host_bind_ip}:{test_port}/health"

    # Define compose commands
    compose_up_command = [
        "docker",
        "compose",
        "-f",
        "docker-compose.yml",
        "-f",
        "docker-compose.test.override.yml",
        "--project-name",
        "olm-d-rch-test",
        "up",
        "-d",
        "--build",
    ]
    compose_down_command = [
        "docker",
        "compose",
        "-f",
        "docker-compose.yml",
        "-f",
        "docker-compose.test.override.yml",
        "--project-name",
        "olm-d-rch-test",
        "down",
        "-v",
    ]

    def wait_for_health_check(url: str, timeout_seconds: int = 30) -> bool:
        """Wait for the application to be healthy."""
        start_time = time.time()
        attempt = 0
        while time.time() - start_time < timeout_seconds:
            attempt += 1
            print(f"Health check attempt {attempt} at {url}...")
            try:
                response = httpx.get(url, timeout=5.0)
                if 200 <= response.status_code < 300:
                    print(f"✅ Health check passed at {url}.")
                    return True
                else:
                    print(
                        f"Health check failed with status {response.status_code}, retrying..."
                    )
            except httpx.RequestError as e:
                print(f"Health check failed with error: {e}, retrying...")
            time.sleep(2)
        print(f"❌ Health check timed out after {timeout_seconds} seconds.")
        return False

    try:
        print("\nStarting Docker Compose services for E2E testing...")
        result = subprocess.run(compose_up_command, capture_output=False, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to start services.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

        print(f"Waiting for application to be healthy at {health_url}...")
        if not wait_for_health_check(health_url):
            # If health check fails, print logs before raising error
            logs_command = [
                "docker",
                "compose",
                "-f",
                "docker-compose.yml",
                "-f",
                "docker-compose.test.override.yml",
                "--project-name",
                "olm-d-rch-test",
                "logs",
            ]
            log_result = subprocess.run(logs_command, capture_output=True, text=True)
            raise RuntimeError(
                f"Application failed to become healthy within timeout.\nLogs:\n{log_result.stdout}\n{log_result.stderr}"
            )

        print("✅ E2E test environment is ready.")
        yield

    finally:
        print("\nStopping Docker Compose services...")
        cleanup_result = subprocess.run(
            compose_down_command, capture_output=True, text=True
        )
        if cleanup_result.returncode != 0:
            print(f"Warning: Failed during cleanup: {cleanup_result.stderr}")
        print("E2E test cleanup completed.")

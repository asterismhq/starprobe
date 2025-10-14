import asyncio
import os
from pprint import pprint

from dotenv import load_dotenv

from olm_d_rch.dependencies import (
    _create_llm_client,
    _create_prompt_service,
    _create_research_service,
    _create_scraping_service,
    _create_search_client,
    get_app_settings,
    get_ddgs_settings,
    get_mlx_settings,
    get_ollama_settings,
    get_scraping_settings,
    get_workflow_settings,
)
from olm_d_rch.graph import build_graph

load_dotenv()


async def main(output_file: str = "demo/example.md"):
    """
    Main function to perform deep research locally.
    """
    # Enter the research topic you want to try here
    research_topic = "Current state of AI technology in Japan and future prospects"

    print(f"Starting research on the topic '{research_topic}'...")

    # Get services using dependency injection
    backend = os.getenv("OLM_D_RCH_LLM_BACKEND")
    app_settings = get_app_settings()
    ollama_settings = get_ollama_settings()
    mlx_settings = get_mlx_settings()
    workflow_settings = get_workflow_settings()

    llm_client = _create_llm_client(
        backend or app_settings.llm_backend, app_settings, ollama_settings, mlx_settings
    )
    prompt_service = _create_prompt_service(workflow_settings)
    research_service = _create_research_service(
        workflow_settings,
        _create_search_client(get_ddgs_settings()),
        _create_scraping_service(get_scraping_settings()),
    )

    # Build the configuration the same way as the API server
    ollama_model = os.getenv("OLM_D_RCH_OLLAMA_MODEL", "llama3.2:3b")
    ollama_host = os.getenv("OLLAMA_HOST")
    mlx_model = os.getenv(
        "OLM_D_RCH_MLX_MODEL", "mlx-community/Llama-3.1-8B-Instruct-4bit"
    )

    if backend == "mlx":
        configurable_settings = {"mlx_model": mlx_model}
    else:
        if not ollama_host:
            raise RuntimeError(
                "OLLAMA_HOST must be set in the environment to run the demo"
            )
        configurable_settings = {
            "ollama_model": ollama_model,
            "ollama_host": ollama_host,
        }

    config = {"configurable": configurable_settings}

    try:
        # Build graph with injected services
        graph = build_graph(
            prompt_service, research_service, llm_client, backend=backend
        )

        # Execute the graph (research process) asynchronously
        result = await graph.ainvoke({"research_topic": research_topic}, config=config)

        print("\n===== Research Results =====")
        # Print the results in a formatted way
        pprint(result)
        print("====================")

        # Save results to markdown file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.get("article", "No article available"))
            f.write(f"\n\n**Success:** {result.get('success', False)}\n")
            if result.get("error_message"):
                f.write(f"\n**Error:** {result['error_message']}\n")

        print(f"Results saved to {output_file}")

    except Exception as e:
        import traceback

        print(f"\nAn error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    # asyncio.run() is available in Python 3.7 and later
    asyncio.run(main())

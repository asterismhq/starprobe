import asyncio
from pprint import pprint

from dotenv import load_dotenv

from starprobe.dependencies import (
    _create_llm_client,
    _create_prompt_service,
    _create_research_service,
    _create_scraping_service,
    _create_search_client,
    get_ddgs_settings,
    get_nexus_settings,
    get_scraping_settings,
    get_workflow_settings,
)
from starprobe.graph import build_graph

load_dotenv()


async def main(output_file: str = "demo/example.md"):
    """
    Main function to perform deep research locally.
    """
    # Enter the research topic you want to try here
    research_topic = "Current state of AI technology in Japan and future prospects"

    print(f"Starting research on the topic '{research_topic}'...")

    # Get services using dependency injection
    nexus_settings = get_nexus_settings()
    workflow_settings = get_workflow_settings()

    llm_client = _create_llm_client(nexus_settings)
    prompt_service = _create_prompt_service(workflow_settings)
    research_service = _create_research_service(
        workflow_settings,
        _create_search_client(get_ddgs_settings()),
        _create_scraping_service(get_scraping_settings()),
    )

    # Build the configuration the same way as the API server
    config = {}

    try:
        # Build graph with injected services
        graph = build_graph(prompt_service, research_service, llm_client)

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

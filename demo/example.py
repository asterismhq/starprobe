import asyncio
import os
from pprint import pprint

from dotenv import load_dotenv

from ollama_deep_researcher.graph import build_graph
from ollama_deep_researcher.settings import OllamaDeepResearcherSettings

load_dotenv()


async def main(output_file: str = "demo/example.md"):
    """
    Main function to perform deep research locally.
    """
    # Enter the research topic you want to try here
    research_topic = "Current state of AI technology in Japan and future prospects"

    print(f"Starting research on the topic '{research_topic}'...")

    # Build the configuration the same way as the API server
    ollama_model = os.getenv("RESEARCH_API_OLLAMA_MODEL", "llama3.2:3b")
    ollama_host = os.getenv("OLLAMA_HOST")
    # Let Pydantic handle parsing the DEBUG env var from the environment
    settings = OllamaDeepResearcherSettings(
        ollama_host=ollama_host,
        ollama_model=ollama_model,
    )
    debug = settings.debug

    # Check OLLAMA_HOST only if not in debug mode
    if not debug and not ollama_host:
        raise RuntimeError("OLLAMA_HOST must be set in the environment to run the demo")

    settings = settings.model_copy(
        update={
            "ollama_model": ollama_model,
            "ollama_host": ollama_host,
            "debug": debug,
        }
    )

    config = {
        "configurable": {
            "ollama_model": ollama_model,
            "ollama_host": ollama_host,
            "debug": debug,
        }
    }

    try:
        # Build graph
        graph = build_graph(settings=settings)

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

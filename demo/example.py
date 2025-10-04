import asyncio
import os
from pprint import pprint

from dotenv import load_dotenv

from ollama_deep_researcher.graph import build_graph

load_dotenv()


async def main(output_file: str = "demo/example.md"):
    """
    Main function to perform deep research locally.
    """
    # Enter the research topic you want to try here
    research_topic = "Current state of AI technology in Japan and future prospects"

    print(f"Starting research on the topic '{research_topic}'...")

    # Build the configuration the same way as the API server
    # If environment variables are not set, default values will be used
    local_llm = os.getenv("LLM_MODEL", "llama3.2:3b")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/")
    config = {
        "configurable": {
            "local_llm": local_llm,
            "ollama_base_url": ollama_base_url,
            # Other settings can be added as needed
            # "search_api": "duckduckgo",
            # "max_web_research_loops": 3,
        }
    }

    try:
        # Build graph
        graph = build_graph()

        # Execute the graph (research process) asynchronously
        result = await graph.ainvoke({"research_topic": research_topic}, config=config)

        print("\n===== Research Results =====")
        # Print the results in a formatted way
        pprint(result)
        print("====================")

        # Save results to markdown file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Research Results\n\n")
            f.write(f"**Topic:** {research_topic}\n\n")
            running_summary = result.get("running_summary", "No summary available")
            f.write(running_summary)
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

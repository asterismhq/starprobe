import asyncio
import os
from pprint import pprint

from dotenv import load_dotenv

from ollama_deep_researcher.graph import graph
from ollama_deep_researcher.settings import OllamaClient

load_dotenv()


async def main():
    """
    Main function to perform deep research locally.
    """
    # Enter the research topic you want to try here
    research_topic = "Current state of AI technology in Japan and future prospects"

    print(f"Starting research on the topic '{research_topic}'...")

    # Build the configuration the same way as the API server
    # If environment variables are not set, default values will be used
    local_llm = os.getenv("LLM_MODEL", "qwen3:4b")
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
    # Add LLM client to config
    # For simplicity, assume not using tool calling in demo
    config["llm_client"] = OllamaClient(
        config["configurable"],
        base_url=ollama_base_url,
        model=local_llm,
        temperature=0,
        format="json",  # Assuming JSON mode for demo
    )

    try:
        # Execute the graph (research process) asynchronously
        result = await graph.ainvoke({"research_topic": research_topic}, config=config)

        print("\n===== Research Results =====")
        # Print the results in a formatted way
        pprint(result)
        print("====================")

    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    # asyncio.run() is available in Python 3.7 and later
    asyncio.run(main())

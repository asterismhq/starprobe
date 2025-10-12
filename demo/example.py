import asyncio
import os
from pprint import pprint

from dotenv import load_dotenv

from olm_d_rch.graph import build_graph

load_dotenv()


async def main(output_file: str = "demo/example.md"):
    """
    Main function to perform deep research locally.
    """
    # Enter the research topic you want to try here
    research_topic = "Current state of AI technology in Japan and future prospects"

    print(f"Starting research on the topic '{research_topic}'...")

    # Build the configuration the same way as the API server
    backend = os.getenv("OLM_D_RCH_LLM_BACKEND")
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
        # Build graph
        graph = build_graph(backend=backend)

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

"""
CLI entry point for the novel-writing agent.

Usage:
    python main.py "Your novel premise here"
    python main.py                             # interactive prompt
"""

import io
import logging
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding before any output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from graph import build_graph
from memory import save_memory
import config

# -- Logging ----------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(stream=sys.stderr)],
)
logger = logging.getLogger(__name__)


# -- Banner -----------------------------------------------------------------

BANNER = """
+==============================================================+
|                                                              |
|    NOVEL WRITER AGENT                                        |
|                                                              |
|    Multi-agent romance novel generator                       |
|    Powered by free LLM APIs via OpenRouter                   |
|                                                              |
+==============================================================+
"""


def main():
    print(BANNER)

    # -- Validate API key --------------------------------------------------
    if not config.OPENROUTER_API_KEY:
        logger.error(
            "OPENROUTER_API_KEY not set. "
            "Copy .env.example to .env and add your key.\n"
            "   Get a free key at: https://openrouter.ai/keys"
        )
        sys.exit(1)

    # -- Get user prompt ---------------------------------------------------
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        print("Describe the romance novel you'd like to generate:")
        print("(e.g., 'A second-chance romance between a firefighter")
        print(" and a pastry chef in a small coastal town')\n")
        user_request = input("Your idea: ").strip()

    if not user_request:
        logger.error("No prompt provided. Exiting.")
        sys.exit(1)

    # -- Show config -------------------------------------------------------
    logger.info("[CONFIG] Model:    %s", config.DEFAULT_MODEL)
    logger.info("[CONFIG] Chapters: %d", config.CHAPTER_COUNT)
    logger.info("[CONFIG] Words/ch: %d", config.TARGET_WORDS_PER_CHAPTER)
    logger.info("[CONFIG] Gemini:   %s", "enabled" if config.GEMINI_API_KEY else "disabled")
    print()

    # -- Build and run the graph -------------------------------------------
    logger.info("[START] Novel generation pipeline starting...")
    logger.info("[START] Prompt: %s", user_request[:100] + ("..." if len(user_request) > 100 else ""))
    print()

    graph = build_graph()

    initial_state = {
        "user_request": user_request,
    }

    start_time = datetime.now()

    try:
        # Stream events so we can see progress
        final_state = None
        for event in graph.stream(initial_state, {"recursion_limit": 200}):
            # Each event is a dict with one key (the node name)
            for node_name, node_output in event.items():
                status = node_output.get("status", "")
                if status:
                    logger.info("   [%s] -> %s", node_name, status)
                final_state = {**initial_state, **(final_state or {}), **node_output}

    except KeyboardInterrupt:
        logger.warning("\nGeneration interrupted by user.")
        sys.exit(130)
    except Exception as exc:
        logger.error("Pipeline failed: %s", exc, exc_info=True)
        sys.exit(1)

    # -- Save memory -------------------------------------------------------
    if final_state and "memory" in final_state:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        memory_path = Path(config.OUTPUT_DIR) / f"novel_{timestamp}.json"
        save_memory(final_state["memory"], memory_path)
        logger.info("[MEMORY] Story memory saved: %s", memory_path)

    # -- Summary -----------------------------------------------------------
    elapsed = datetime.now() - start_time

    print()
    print("=" * 60)
    print("  GENERATION COMPLETE")
    print("=" * 60)

    if final_state:
        output_path = final_state.get("output_path", "")
        chapters = final_state.get("final_chapters", [])
        total_words = sum(len(ch.split()) for ch in chapters)

        print(f"  Output:    {output_path}")
        print(f"  Chapters:  {len(chapters)}")
        print(f"  Words:     {total_words:,}")
        print(f"  Time:      {elapsed}")

    print("=" * 60)
    print()


if __name__ == "__main__":
    main()

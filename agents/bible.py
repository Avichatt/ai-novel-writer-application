"""
Story Bible compiler.

Assembles a single reference document from the concept, characters,
and outline. This is pure Python — NO LLM call, saving API quota.
"""

import logging

from state import NovelState
from memory import create_initial_memory

logger = logging.getLogger(__name__)


def story_bible(state: NovelState) -> dict:
    """LangGraph node: compile the story bible (no LLM call)."""
    logger.info("[BIBLE] Assembling story bible...")

    bible = f"""\
{'=' * 60}
                     STORY BIBLE
{'=' * 60}

--------------------------------------------------------------
CONCEPT
--------------------------------------------------------------
{state['concept']}

--------------------------------------------------------------
CHARACTERS
--------------------------------------------------------------
{state['characters']}

--------------------------------------------------------------
CHAPTER OUTLINE
--------------------------------------------------------------
{state['outline']}

{'=' * 60}
"""

    # Initialize chapter-loop state
    memory = create_initial_memory()

    logger.info("[BIBLE] Story Bible compiled (0 API calls).")
    return {
        "story_bible": bible,
        "current_chapter": 1,
        "chapter_plans": [],
        "chapters": [],
        "qa_reports": [],
        "revision_needed": [],
        "revised_chapters": [],
        "final_chapters": [],
        "memory": memory,
        "status": "bible_ready",
    }

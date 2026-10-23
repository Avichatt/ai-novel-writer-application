"""
Chapter Planner agent.

Creates a detailed scene-by-scene plan for the current chapter,
incorporating memory context from previous chapters.
"""

import logging

from llm import invoke_with_fallback
from state import NovelState
from memory import get_context_for_chapter
import config

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """\
You are a meticulous romance novel chapter planner.

STORY BIBLE (reference — do NOT repeat this, just use it):
{story_bible_excerpt}

CHAPTER OUTLINE ENTRY:
{outline_excerpt}

STORY MEMORY — WHAT HAS HAPPENED SO FAR:
{memory_context}

You are planning CHAPTER {chapter_num} of {chapter_count}.

Create a detailed scene-by-scene plan for this chapter. Include:

1. OPENING — how the chapter starts (hook the reader in the first paragraph)
2. SCENES — 3-5 scenes with:
   - Setting & atmosphere
   - Characters present
   - What happens (action + dialogue beats)
   - Emotional undercurrent
   - Sensory details to include
3. ROMANTIC PROGRESSION — specific moments that advance the romance
4. CHARACTER DEVELOPMENT — how the POV character grows or resists growth
5. CHAPTER ENDING — a hook or emotional beat that makes the reader turn the page
6. TARGET WORD COUNT: ~{words_per_chapter} words

IMPORTANT CONTINUITY NOTES:
- Reference specific events from previous chapters where relevant
- Maintain consistent character voice and behavior
- Don't repeat scenes or conversations that already happened
- Advance the plot — every chapter must MOVE THE STORY FORWARD
"""


def _extract_chapter_outline(outline: str, chapter_num: int) -> str:
    """Pull the relevant chapter section from the full outline."""
    lines = outline.split("\n")
    start = None
    end = None

    for i, line in enumerate(lines):
        upper = line.upper().strip()
        if f"CHAPTER {chapter_num}" in upper or f"CHAPTER [{chapter_num}]" in upper:
            start = i
        elif start is not None and (
            "CHAPTER " in upper
            and f"CHAPTER {chapter_num}" not in upper
        ):
            end = i
            break

    if start is not None:
        return "\n".join(lines[start:end])
    # Fallback: return the whole outline (short enough for free models)
    return outline


def chapter_planner(state: NovelState) -> dict:
    """LangGraph node: plan the current chapter."""
    ch = state["current_chapter"]
    total = state["chapter_count"]
    logger.info("[PLANNER] Planning chapter %d/%d...", ch, total)

    # Keep the bible excerpt short to save tokens
    bible_excerpt = state["story_bible"][:3000]
    outline_excerpt = _extract_chapter_outline(state["outline"], ch)
    memory_context = get_context_for_chapter(state["memory"], ch)

    prompt = PROMPT_TEMPLATE.format(
        story_bible_excerpt=bible_excerpt,
        outline_excerpt=outline_excerpt,
        memory_context=memory_context,
        chapter_num=ch,
        chapter_count=total,
        words_per_chapter=config.TARGET_WORDS_PER_CHAPTER,
    )

    plan = invoke_with_fallback(prompt, role="planner")

    plans = list(state.get("chapter_plans", []))
    plans.append(plan)

    logger.info("[PLANNER] Chapter %d plan ready.", ch)
    return {"chapter_plans": plans, "status": f"chapter_{ch}_planned"}

"""
Chapter Writer agent.

Generates the actual prose for one chapter based on the chapter plan,
story bible, and memory context.
"""

import logging

from llm import invoke_with_fallback
from state import NovelState
from memory import get_context_for_chapter
import config

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """\
You are an acclaimed romance novelist known for vivid prose, authentic \
dialogue, and deeply emotional storytelling.

CHARACTERS (reference):
{characters_excerpt}

CHAPTER PLAN:
{chapter_plan}

STORY MEMORY — PREVIOUS EVENTS:
{memory_context}

Write CHAPTER {chapter_num}: following the plan above.

WRITING REQUIREMENTS:
- Target ~{words_per_chapter} words
- Write in third-person {pov_note}
- Open with a hook — drop the reader into the scene immediately
- Use vivid sensory details (sight, sound, smell, touch, taste)
- Balance action, dialogue, and internal thought
- Show emotion through physical reactions, not just telling
- Dialogue should sound natural and reveal character
- Include at least one moment of romantic tension
- End with a hook or emotional beat that propels the reader forward
- Use scene breaks (marked with ***) between distinct scenes

STYLE GUIDELINES:
- Vary sentence length for rhythm
- Use strong verbs — avoid excessive adverbs
- Ground abstract emotions in concrete physical sensations
- Let subtext do the heavy lifting in romantic scenes
- Don't over-explain — trust the reader

DO NOT:
- Start with "Chapter N" as a heading (the system adds that)
- Include author notes or meta-commentary
- Repeat information the reader already knows
- Use clichéd phrases like "electricity shot through her" unless subverted

Write the complete chapter now. Begin directly with the prose.
"""


def chapter_writer(state: NovelState) -> dict:
    """LangGraph node: write the current chapter's prose."""
    ch = state["current_chapter"]
    total = state["chapter_count"]
    logger.info("[WRITER] Writing chapter %d/%d...", ch, total)

    chapter_plan = state["chapter_plans"][ch - 1]
    memory_context = get_context_for_chapter(state["memory"], ch)

    # Keep character excerpt concise
    characters_excerpt = state["characters"][:2000]

    # Simple POV note
    pov_note = "limited POV" if ch % 2 == 1 else "limited POV (alternate perspective)"

    prompt = PROMPT_TEMPLATE.format(
        characters_excerpt=characters_excerpt,
        chapter_plan=chapter_plan,
        memory_context=memory_context,
        chapter_num=ch,
        words_per_chapter=config.TARGET_WORDS_PER_CHAPTER,
        pov_note=pov_note,
    )

    chapter_text = invoke_with_fallback(prompt, role="writer")

    chapters = list(state.get("chapters", []))
    chapters.append(chapter_text)

    word_count = len(chapter_text.split())
    logger.info("[WRITER] Chapter %d written (%d words).", ch, word_count)
    return {"chapters": chapters, "status": f"chapter_{ch}_written"}

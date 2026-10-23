"""
Conditional Revision agent.

Only invoked when the QA agent flags critical issues.
Rewrites the chapter addressing specific problems while
preserving what works.
"""

import logging

from llm import invoke_with_fallback
from state import NovelState

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """\
You are a romance novel revision specialist. Your job is to improve a chapter \
based on specific editorial feedback while preserving the author's voice and \
everything that already works.

ORIGINAL CHAPTER {chapter_num}:
{chapter_text}

QA REPORT / EDITORIAL FEEDBACK:
{qa_report}

REVISION INSTRUCTIONS:
1. Fix ALL critical issues identified in the QA report
2. Preserve the overall plot progression and key scenes
3. Maintain character voice and POV consistency
4. Keep approximately the same word count (~{word_count} words)
5. Strengthen any weak areas noted in the quality scores
6. Do NOT add new plot elements or scenes unless the QA report specifically
   says content is missing

Return the COMPLETE revised chapter. Begin directly with the prose — no \
preamble, no author notes.
"""


def reviser(state: NovelState) -> dict:
    """LangGraph node: revise a chapter that failed QA."""
    ch = state["current_chapter"]
    logger.info("[REVISER] Revising chapter %d...", ch)

    chapter_text = state["chapters"][ch - 1]
    qa_report = state["qa_reports"][ch - 1]
    word_count = len(chapter_text.split())

    prompt = PROMPT_TEMPLATE.format(
        chapter_num=ch,
        chapter_text=chapter_text,
        qa_report=qa_report,
        word_count=word_count,
    )

    revised = invoke_with_fallback(prompt, role="reviser")

    revised_chapters = list(state.get("revised_chapters", []))
    revised_chapters.append(revised)

    new_word_count = len(revised.split())
    logger.info("[REVISER] Chapter %d revised (%d -> %d words).", ch, word_count, new_word_count)
    return {"revised_chapters": revised_chapters, "status": f"chapter_{ch}_revised"}


def skip_revision(state: NovelState) -> dict:
    """LangGraph node: skip revision when QA passed."""
    ch = state["current_chapter"]
    logger.info("[REVISER] Chapter %d passed QA - skipping revision.", ch)

    revised_chapters = list(state.get("revised_chapters", []))
    revised_chapters.append("")  # Empty string = no revision needed

    return {"revised_chapters": revised_chapters, "status": f"chapter_{ch}_no_revision"}

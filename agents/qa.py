"""
Combined QA agent — Romance Editor + Continuity Checker in one call.

This saves an API call per chapter by merging two checks.
Returns a structured QA report and a revision-needed flag.
"""

import logging

from llm import invoke_with_fallback
from state import NovelState
from memory import get_context_for_chapter

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """\
You are a senior romance editor performing a combined quality and continuity \
review of a novel chapter.

STORY BIBLE (excerpt):
{story_bible_excerpt}

CHAPTER PLAN:
{chapter_plan}

STORY MEMORY — WHAT HAPPENED BEFORE:
{memory_context}

CHAPTER {chapter_num} TEXT:
{chapter_text}

Perform TWO analyses and return a structured report:

═══════════════════════════════════════════
PART 1: ROMANCE QUALITY CHECK
═══════════════════════════════════════════

Rate each on a scale of 1-10 and provide brief notes:

- EMOTIONAL DEPTH: [1-10] — Are the characters' feelings authentic and layered?
- ROMANTIC TENSION: [1-10] — Is there genuine push-pull between protagonists?
- DIALOGUE QUALITY: [1-10] — Does dialogue sound natural and reveal character?
- PACING: [1-10] — Does the chapter flow well and maintain reader engagement?
- SENSORY WRITING: [1-10] — Are scenes grounded in vivid sensory detail?
- CHARACTER VOICE: [1-10] — Is the POV character's voice distinctive?

═══════════════════════════════════════════
PART 2: CONTINUITY CHECK
═══════════════════════════════════════════

Check for:
- CHARACTER CONSISTENCY: Any out-of-character behavior?
- TIMELINE ERRORS: Any impossible sequences of events?
- SETTING CONSISTENCY: Any location/detail contradictions?
- PLOT THREAD TRACKING: Any dropped threads or loose ends?
- FACTUAL CONSISTENCY: Names, ages, occupations, physical descriptions correct?

═══════════════════════════════════════════
VERDICT
═══════════════════════════════════════════

OVERALL SCORE: [average of the 6 scores above, to 1 decimal]
REVISION NEEDED: [YES or NO]
CRITICAL ISSUES: [list only issues that MUST be fixed, or "None"]
SUGGESTIONS: [optional improvements, not mandatory]
"""


def qa_agent(state: NovelState) -> dict:
    """LangGraph node: combined romance + continuity QA for current chapter."""
    ch = state["current_chapter"]
    logger.info("[QA] Reviewing chapter %d...", ch)

    chapter_text = state["chapters"][ch - 1]
    chapter_plan = state["chapter_plans"][ch - 1]
    memory_context = get_context_for_chapter(state["memory"], ch)
    bible_excerpt = state["story_bible"][:2000]

    prompt = PROMPT_TEMPLATE.format(
        story_bible_excerpt=bible_excerpt,
        chapter_plan=chapter_plan,
        memory_context=memory_context,
        chapter_num=ch,
        chapter_text=chapter_text,
    )

    report = invoke_with_fallback(prompt, role="qa")

    # Parse whether revision is needed
    needs_revision = "REVISION NEEDED: YES" in report.upper()

    qa_reports = list(state.get("qa_reports", []))
    qa_reports.append(report)

    revision_flags = list(state.get("revision_needed", []))
    revision_flags.append(needs_revision)

    status = "needs_revision" if needs_revision else "qa_passed"
    logger.info(
        "[QA] Complete for chapter %d - %s",
        ch,
        "REVISION NEEDED" if needs_revision else "PASSED",
    )
    return {
        "qa_reports": qa_reports,
        "revision_needed": revision_flags,
        "status": f"chapter_{ch}_{status}",
    }

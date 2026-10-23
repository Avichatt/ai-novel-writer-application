"""
Final Editor agent.

Performs a single pass over the complete manuscript for polish,
consistency, and overall quality. This is ONE API call for the
entire book to stay within free-tier limits.
"""

import logging

from llm import invoke_with_fallback
from state import NovelState

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """\
You are a senior fiction editor performing a final polish pass on a \
completed romance novel manuscript.

STORY CONCEPT:
{concept}

FULL MANUSCRIPT:
{manuscript}

Perform a FINAL EDITORIAL PASS. For each chapter, provide:

CHAPTER [N]:
- OPENING: Is the hook strong? Suggest improvement if needed.
- ENDING: Does it compel the reader forward? Suggest improvement if needed.
- PROSE QUALITY: Flag any awkward sentences or repetitive phrasing.
- PACING NOTE: Any sections that drag or rush?

OVERALL MANUSCRIPT:
- ARC COMPLETION: Do both protagonists complete their character arcs?
- ROMANCE SATISFACTION: Is the HEA/HFN earned and emotionally satisfying?
- CONSISTENCY: Any remaining continuity issues across chapters?
- THEME: Is the central theme woven consistently throughout?
- FINAL VERDICT: [READY FOR EXPORT / NEEDS MINOR TWEAKS]
- TOP 3 STRENGTHS: What this manuscript does best
- TOP 3 AREAS FOR IMPROVEMENT: What a human author would want to refine

Be constructive and specific. This is the LAST editorial pass before \
the manuscript is exported.
"""


def final_editor(state: NovelState) -> dict:
    """LangGraph node: final editorial review of the complete manuscript."""
    logger.info("[FINAL_EDITOR] Reviewing complete manuscript...")

    # Assemble the best version of each chapter
    final_chapters: list[str] = []
    chapters = state.get("chapters", [])
    revised = state.get("revised_chapters", [])

    for i in range(len(chapters)):
        # Use revised version if it exists and is non-empty
        if i < len(revised) and revised[i]:
            final_chapters.append(revised[i])
        else:
            final_chapters.append(chapters[i])

    # Build manuscript text
    manuscript_parts: list[str] = []
    for i, ch_text in enumerate(final_chapters, 1):
        manuscript_parts.append(f"=== CHAPTER {i} ===\n\n{ch_text}")

    manuscript = "\n\n".join(manuscript_parts)

    # Truncate if needed (free models have limited context windows)
    # Send first and last 2 chapters in full, summarize middle ones
    if len(final_chapters) > 6:
        condensed_parts: list[str] = []
        for i, ch_text in enumerate(final_chapters, 1):
            if i <= 2 or i >= len(final_chapters) - 1:
                condensed_parts.append(f"=== CHAPTER {i} ===\n\n{ch_text}")
            else:
                # Truncate middle chapters to ~500 words
                words = ch_text.split()
                preview = " ".join(words[:500])
                condensed_parts.append(
                    f"=== CHAPTER {i} (truncated for review) ===\n\n{preview}..."
                )
        manuscript = "\n\n".join(condensed_parts)

    prompt = PROMPT_TEMPLATE.format(
        concept=state["concept"][:1000],
        manuscript=manuscript,
    )

    report = invoke_with_fallback(prompt, role="editor")

    logger.info("[FINAL_EDITOR] Final editorial review complete.")
    return {
        "final_chapters": final_chapters,
        "status": "final_edit_complete",
    }

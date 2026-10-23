"""
Outline Architect agent.

Produces a detailed chapter-by-chapter outline with beats,
POV, locations, and emotional arcs.
"""

import logging

from llm import invoke_with_fallback
from state import NovelState
import config

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """\
You are a commercial romance story architect. You structure novels that \
keep readers turning pages and deliver deeply satisfying emotional payoffs.

CONCEPT:
{concept}

CHARACTERS:
{characters}

Create a detailed {chapter_count}-chapter outline.

The story MUST include these romance-novel beats (place them where they \
naturally fit across the chapters):

1. Compelling opening that establishes the protagonist's ordinary world
2. Meet-cute or inciting incident that throws the protagonists together
3. Forced proximity or reason they must keep interacting
4. Growing attraction (physical and emotional)
5. Escalating emotional intimacy and vulnerability
6. Romantic complication (external obstacle or internal fear)
7. Midpoint — acknowledgment of feelings (to self or other)
8. Deepening relationship + rising external stakes
9. Major obstacle / betrayal / misunderstanding
10. Dark moment — all seems lost for the relationship
11. Climactic choice — protagonist must face their wound/fear
12. Grand gesture or revelation
13. Happily Ever After (HEA) or Happy For Now (HFN)

For EVERY chapter provide:

CHAPTER [N]: [Title]
- POV: [whose perspective]
- LOCATION: [primary setting]
- OBJECTIVE: [what this chapter accomplishes for the plot]
- CONFLICT: [what tension drives this chapter]
- ROMANTIC BEAT: [where are we on the romance arc]
- EMOTIONAL BEAT: [internal character development]
- KEY SCENES: [2-3 bullet points of what happens]
- TURNING POINT: [how this chapter changes the story]
- APPROXIMATE WORD COUNT: ~{words_per_chapter}
- ENDS WITH: [chapter-ending hook to keep readers going]
"""


def outline_agent(state: NovelState) -> dict:
    """LangGraph node: produce the full chapter outline."""
    logger.info("[OUTLINER] Structuring the novel...")

    prompt = PROMPT_TEMPLATE.format(
        concept=state["concept"],
        characters=state["characters"],
        chapter_count=config.CHAPTER_COUNT,
        words_per_chapter=config.TARGET_WORDS_PER_CHAPTER,
    )

    outline = invoke_with_fallback(prompt, role="outliner")

    logger.info("[OUTLINER] Outline complete.")
    return {
        "outline": outline,
        "chapter_count": config.CHAPTER_COUNT,
        "status": "outline_ready",
    }

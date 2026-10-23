"""
Story Strategist agent.

Takes the user's raw request and produces a structured story concept
including title, hook, premise, tropes, target audience, and genre.
"""

import logging

from llm import invoke_with_fallback
from state import NovelState
import config

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """\
You are a professional romance acquisitions editor with 20 years of experience \
at a major publishing house.

Your job is to take a raw user idea and turn it into a commercially viable \
romance novel concept.

USER REQUEST:
{user_request}

TARGET LENGTH: {chapter_count} chapters, ~{words_per_chapter} words each

Create a detailed, compelling concept. Return EXACTLY this format:

TITLE: [catchy, marketable title]
SUBTITLE: [optional tagline]
HOOK: [one-sentence hook that would go on the back cover]
PREMISE: [2-3 sentence premise]
TROPES: [comma-separated list of romance tropes used]
SUBGENRE: [e.g., contemporary, historical, romantic suspense, paranormal]
TARGET AUDIENCE: [demographic]
HEAT LEVEL: [sweet / warm / steamy]
TONE: [e.g., witty, angsty, heartwarming, dark]
SETTING: [time and place]
RECOMMENDED CHAPTER COUNT: {chapter_count}
CENTRAL CONFLICT: [the main obstacle keeping the protagonists apart]
EMOTIONAL STAKES: [what each protagonist stands to lose]

Focus on:
- Commercial readability and strong emotional stakes
- A clear, compelling central conflict
- Tropes that work well together
- A setting that enhances the romance
"""


def story_strategist(state: NovelState) -> dict:
    """LangGraph node: generate the story concept."""
    logger.info("[STRATEGIST] Developing story concept...")

    prompt = PROMPT_TEMPLATE.format(
        user_request=state["user_request"],
        chapter_count=config.CHAPTER_COUNT,
        words_per_chapter=config.TARGET_WORDS_PER_CHAPTER,
    )

    concept = invoke_with_fallback(prompt, role="strategist")

    logger.info("[STRATEGIST] Concept developed.")
    return {"concept": concept, "status": "concept_ready"}

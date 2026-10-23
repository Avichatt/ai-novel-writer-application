"""
Character Designer agent.

Creates detailed protagonist and supporting character profiles
with arcs, wounds, and romantic needs.
"""

import logging

from llm import invoke_with_fallback
from state import NovelState

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """\
You are a professional romance character designer. Your characters must feel \
real, flawed, and deeply compelling.

BOOK CONCEPT:
{concept}

Design the following characters in rich detail:

## 1. HERO (male protagonist)
## 2. HEROINE (female protagonist)
## 3. SUPPORTING CHARACTERS (2-3 key secondary characters)

For BOTH protagonists, provide:

- Full name
- Age
- Physical description (distinctive, memorable details)
- Occupation & professional life
- Personality (strengths and flaws)
- Backstory (key formative experiences)
- External goal (what they want in the plot)
- Emotional wound (the deep hurt driving their behavior)
- Fear (what they're afraid will happen again)
- False belief (the lie they tell themselves)
- Romantic need (what they need from a partner but can't admit)
- Character arc (how they'll change by the end)
- Voice/speech patterns (how they talk — formal, sarcastic, gentle, etc.)
- Key relationships (family, friends, rivals)

For SUPPORTING CHARACTERS, provide:
- Name, age, role in the story
- Personality sketch
- How they catalyze or complicate the romance

Make the protagonists' emotional wounds DIRECTLY relevant to the central \
conflict. Their flaws should create realistic obstacles to love.
"""


def character_agent(state: NovelState) -> dict:
    """LangGraph node: design the cast of characters."""
    logger.info("[CHARACTERS] Designing characters...")

    prompt = PROMPT_TEMPLATE.format(concept=state["concept"])
    characters = invoke_with_fallback(prompt, role="characters")

    logger.info("[CHARACTERS] Characters designed.")
    return {"characters": characters, "status": "characters_ready"}

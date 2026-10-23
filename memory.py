"""
Python-managed story memory.

Maintains structured state about characters, locations, timeline,
relationship arcs, and plot threads — entirely in Python, no LLM calls.

This saves API quota and gives deterministic, parseable state.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path


def create_initial_memory() -> dict:
    """Return a fresh story-memory dictionary."""
    return {
        "characters": {},
        "locations": set(),
        "timeline": [],
        "relationship": {
            "attraction": 0,
            "trust": 0,
            "intimacy": 0,
            "conflict": 0,
        },
        "plot_threads": [],
        "promises": [],
        "secrets": [],
        "chapter_summaries": [],
    }


# ── Context builder ──────────────────────────────────────────────────────────

def get_context_for_chapter(memory: dict, chapter_num: int) -> str:
    """
    Build a concise context string for the LLM based on what
    happened so far.  Keeps token count low by only including
    the last 2-3 chapter summaries and the current relationship state.
    """
    parts: list[str] = []

    # Relationship status
    rel = memory.get("relationship", {})
    if any(v != 0 for v in rel.values()):
        parts.append("RELATIONSHIP STATUS:")
        for key, val in rel.items():
            bar = "█" * val + "░" * (10 - val)
            parts.append(f"  {key.title():12s} [{bar}] {val}/10")

    # Recent chapter summaries (last 3 max)
    summaries = memory.get("chapter_summaries", [])
    recent = summaries[max(0, len(summaries) - 3):]
    if recent:
        parts.append("\nRECENT EVENTS:")
        for s in recent:
            parts.append(f"  • {s}")

    # Active plot threads
    threads = memory.get("plot_threads", [])
    if threads:
        parts.append("\nACTIVE PLOT THREADS:")
        for t in threads:
            parts.append(f"  • {t}")

    # Unresolved secrets
    secrets = memory.get("secrets", [])
    if secrets:
        parts.append("\nUNRESOLVED SECRETS:")
        for s in secrets:
            parts.append(f"  • {s}")

    # Known locations
    locations = memory.get("locations", set())
    if locations:
        locs = sorted(locations) if isinstance(locations, set) else locations
        parts.append(f"\nKNOWN LOCATIONS: {', '.join(locs)}")

    return "\n".join(parts) if parts else "(No prior context — this is chapter 1.)"


# ── Memory update (pure Python, no LLM) ──────────────────────────────────────

def update_memory_from_chapter(
    memory: dict,
    chapter_text: str,
    chapter_num: int,
    qa_report: str = "",
) -> dict:
    """
    Parse the chapter text and QA report to update memory.

    This uses lightweight heuristics — not an LLM call.
    For a production system you might upgrade to NLP extraction.
    """
    memory = copy.deepcopy(memory)

    # ── Chapter summary (first meaningful paragraph, truncated) ───────────
    paragraphs = [p.strip() for p in chapter_text.split("\n\n") if len(p.strip()) > 40]
    summary = paragraphs[0][:200] + "…" if paragraphs else f"Chapter {chapter_num} written."
    memory["chapter_summaries"].append(f"Ch {chapter_num}: {summary}")

    # ── Timeline entry ────────────────────────────────────────────────────
    memory["timeline"].append({
        "chapter": chapter_num,
        "word_count": len(chapter_text.split()),
    })

    # ── Relationship arc progression (simple heuristic) ───────────────────
    text_lower = chapter_text.lower()

    attraction_signals = ["attraction", "desire", "chemistry", "drawn to",
                          "beautiful", "handsome", "pulse quicken", "heart race"]
    trust_signals      = ["trust", "confide", "honest", "vulnerable", "safe with",
                          "opened up", "relied on"]
    intimacy_signals   = ["kiss", "embrace", "held her", "held him", "made love",
                          "tender", "whisper", "caress"]
    conflict_signals   = ["argue", "fight", "betray", "lied", "storm out",
                          "slammed", "couldn't forgive", "furious"]

    def _score(signals: list[str]) -> int:
        return min(sum(1 for s in signals if s in text_lower), 2)

    rel = memory["relationship"]
    rel["attraction"] = min(10, rel["attraction"] + _score(attraction_signals))
    rel["trust"]      = min(10, rel["trust"] + _score(trust_signals))
    rel["intimacy"]   = min(10, rel["intimacy"] + _score(intimacy_signals))

    conflict_delta = _score(conflict_signals)
    if conflict_delta:
        rel["conflict"] = min(10, rel["conflict"] + conflict_delta)
        rel["trust"]    = max(0, rel["trust"] - 1)

    # ── Locations (very simple extraction) ────────────────────────────────
    # Look for patterns like "at the [Place]", "in the [Place]", etc.
    location_patterns = re.findall(
        r'(?:at|in|inside|outside|near)\s+the\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        chapter_text,
    )
    if isinstance(memory["locations"], set):
        memory["locations"].update(location_patterns[:5])
    else:
        memory["locations"] = set(location_patterns[:5])

    return memory


# ── Serialization ─────────────────────────────────────────────────────────────

def _serialize(obj):
    """JSON-serialize sets as sorted lists."""
    if isinstance(obj, set):
        return sorted(obj)
    raise TypeError(f"Cannot serialize {type(obj)}")


def save_memory(memory: dict, path: str | Path) -> None:
    """Persist memory to a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, default=_serialize)


def load_memory(path: str | Path) -> dict:
    """Load memory from a JSON file, or return fresh memory."""
    path = Path(path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            mem = json.load(f)
        # Restore sets
        if "locations" in mem and isinstance(mem["locations"], list):
            mem["locations"] = set(mem["locations"])
        return mem
    return create_initial_memory()

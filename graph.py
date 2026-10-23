"""
LangGraph workflow definition.

Builds the complete novel-writing pipeline as a StateGraph:

  START → strategist → characters → outliner → bible
        → [chapter_loop: planner → writer → qa → (reviser?) → memory_update] × N
        → final_editor → export → END
"""

import logging

from langgraph.graph import StateGraph, END

from state import NovelState
from memory import update_memory_from_chapter
from export import export_docx

from agents.strategist import story_strategist
from agents.characters import character_agent
from agents.outliner import outline_agent
from agents.bible import story_bible
from agents.planner import chapter_planner
from agents.writer import chapter_writer
from agents.qa import qa_agent
from agents.reviser import reviser, skip_revision
from agents.final_editor import final_editor

logger = logging.getLogger(__name__)


# ── Helper nodes ──────────────────────────────────────────────────────────────

def memory_update(state: NovelState) -> dict:
    """
    Update story memory from the latest chapter (pure Python, no LLM).
    Then advance the chapter counter.
    """
    ch = state["current_chapter"]
    logger.info("[MEMORY] Updating memory for chapter %d...", ch)

    # Use revised version if available, otherwise original
    revised = state.get("revised_chapters", [])
    chapters = state.get("chapters", [])

    if ch - 1 < len(revised) and revised[ch - 1]:
        chapter_text = revised[ch - 1]
    else:
        chapter_text = chapters[ch - 1]

    qa_report = ""
    qa_reports = state.get("qa_reports", [])
    if ch - 1 < len(qa_reports):
        qa_report = qa_reports[ch - 1]

    memory = update_memory_from_chapter(
        state["memory"], chapter_text, ch, qa_report
    )

    logger.info("[MEMORY] Updated. Advancing to chapter %d.", ch + 1)
    return {
        "memory": memory,
        "current_chapter": ch + 1,
        "status": f"chapter_{ch}_complete",
    }


def export_node(state: NovelState) -> dict:
    """Export the final manuscript to DOCX."""
    logger.info("[EXPORT] Exporting manuscript...")

    filepath = export_docx(
        chapters=state["final_chapters"],
        concept=state["concept"],
    )

    logger.info("[EXPORT] Complete: %s", filepath)
    return {"output_path": str(filepath), "status": "exported"}


# ── Conditional edges ─────────────────────────────────────────────────────────

def should_revise(state: NovelState) -> str:
    """Route to reviser or skip based on QA verdict."""
    ch = state["current_chapter"]
    flags = state.get("revision_needed", [])

    if ch - 1 < len(flags) and flags[ch - 1]:
        return "revise"
    return "skip"


def should_continue_loop(state: NovelState) -> str:
    """Route back to planner or exit the chapter loop."""
    ch = state["current_chapter"]
    total = state["chapter_count"]

    if ch <= total:
        return "next_chapter"
    return "done"


# ── Graph builder ─────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    """
    Construct the complete LangGraph workflow.

    Returns a compiled StateGraph ready to invoke.
    """
    graph = StateGraph(NovelState)

    # ── Setup phase ───────────────────────────────────────────────────────
    graph.add_node("strategist", story_strategist)
    graph.add_node("characters", character_agent)
    graph.add_node("outliner", outline_agent)
    graph.add_node("bible", story_bible)

    # ── Chapter loop ──────────────────────────────────────────────────────
    graph.add_node("planner", chapter_planner)
    graph.add_node("writer", chapter_writer)
    graph.add_node("qa", qa_agent)
    graph.add_node("reviser", reviser)
    graph.add_node("skip_revision", skip_revision)
    graph.add_node("memory_update", memory_update)

    # ── Final phase ───────────────────────────────────────────────────────
    graph.add_node("final_editor", final_editor)
    graph.add_node("export", export_node)

    # ── Edges: setup phase ────────────────────────────────────────────────
    graph.set_entry_point("strategist")
    graph.add_edge("strategist", "characters")
    graph.add_edge("characters", "outliner")
    graph.add_edge("outliner", "bible")
    graph.add_edge("bible", "planner")          # enter chapter loop

    # ── Edges: chapter loop ───────────────────────────────────────────────
    graph.add_edge("planner", "writer")
    graph.add_edge("writer", "qa")

    # Conditional: revise or skip?
    graph.add_conditional_edges(
        "qa",
        should_revise,
        {
            "revise": "reviser",
            "skip": "skip_revision",
        },
    )

    graph.add_edge("reviser", "memory_update")
    graph.add_edge("skip_revision", "memory_update")

    # Conditional: next chapter or done?
    graph.add_conditional_edges(
        "memory_update",
        should_continue_loop,
        {
            "next_chapter": "planner",
            "done": "final_editor",
        },
    )

    # ── Edges: final phase ────────────────────────────────────────────────
    graph.add_edge("final_editor", "export")
    graph.add_edge("export", END)

    return graph.compile()

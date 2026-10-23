"""
LangGraph state schema for the novel-writing pipeline.

NovelState is a TypedDict that flows through every node in the graph.
All agents read from and write to this shared state.
"""

from typing import TypedDict


class NovelState(TypedDict, total=False):
    """
    Shared state for the novel-writing LangGraph pipeline.

    Fields are populated progressively as the pipeline runs:
      1. user_request  → set by CLI
      2. concept       → set by strategist
      3. characters    → set by character agent
      4. outline       → set by outliner
      5. story_bible   → set by bible compiler
      6. chapters[]    → set by writer (one entry per chapter)
      …and so on.
    """

    # ── Input ─────────────────────────────────────────────────────────────────
    user_request: str

    # ── Setup phase ───────────────────────────────────────────────────────────
    concept: str         # story concept / logline / tropes
    characters: str      # detailed character profiles
    outline: str         # full chapter-by-chapter outline
    story_bible: str     # compiled reference document

    # ── Chapter loop control ──────────────────────────────────────────────────
    chapter_count: int        # total chapters to write
    current_chapter: int      # 1-indexed chapter being processed

    # ── Chapter loop outputs (lists indexed by chapter number - 1) ────────────
    chapter_plans: list[str]       # detailed plan for each chapter
    chapters: list[str]            # raw prose for each chapter
    qa_reports: list[str]          # QA feedback for each chapter
    revision_needed: list[bool]    # whether each chapter needs revision
    revised_chapters: list[str]    # revised prose (empty string if no revision)

    # ── Final output ──────────────────────────────────────────────────────────
    final_chapters: list[str]      # polished chapters after final edit

    # ── Memory ────────────────────────────────────────────────────────────────
    memory: dict                   # Python-managed story memory (see memory.py)

    # ── Status / metadata ─────────────────────────────────────────────────────
    status: str                    # current pipeline status for logging
    output_path: str               # path to the generated DOCX

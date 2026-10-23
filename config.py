"""
Centralized configuration for the novel-writer pipeline.

All settings are loaded from environment variables (via .env)
with sensible defaults for the free-tier workflow.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──────────────────────────────────────────────────────────────────

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Provider URLs ─────────────────────────────────────────────────────────────

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ── Model Selection ──────────────────────────────────────────────────────────
# Each agent role can have its own model override.
# Falls back to LLM_MODEL, which defaults to the OpenRouter free router.

DEFAULT_MODEL = os.getenv("LLM_MODEL", "openrouter/free")

MODELS = {
    "strategist": os.getenv("STRATEGY_MODEL", DEFAULT_MODEL),
    "characters": os.getenv("CHARACTER_MODEL", DEFAULT_MODEL),
    "outliner":   os.getenv("OUTLINER_MODEL", DEFAULT_MODEL),
    "planner":    os.getenv("PLANNER_MODEL", DEFAULT_MODEL),
    "writer":     os.getenv("WRITER_MODEL", DEFAULT_MODEL),
    "qa":         os.getenv("QA_MODEL", DEFAULT_MODEL),
    "reviser":    os.getenv("REVISER_MODEL", DEFAULT_MODEL),
    "editor":     os.getenv("EDITOR_MODEL", DEFAULT_MODEL),
}

# ── Fallback model chains ────────────────────────────────────────────────────
# When the primary model fails, try these in order.

OPENROUTER_FALLBACK_MODELS = [
    "openrouter/free",
    "google/gemma-3-1b-it:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "google/gemma-3-27b-it:free",
]

# ── Generation Parameters ────────────────────────────────────────────────────

TEMPERATURE    = float(os.getenv("TEMPERATURE", "0.8"))
MAX_TOKENS     = int(os.getenv("MAX_TOKENS", "5000"))
MAX_RETRIES    = int(os.getenv("MAX_RETRIES", "3"))

# ── Story Parameters ─────────────────────────────────────────────────────────

CHAPTER_COUNT           = int(os.getenv("CHAPTER_COUNT", "10"))
TARGET_WORDS_PER_CHAPTER = int(os.getenv("TARGET_WORDS_PER_CHAPTER", "1500"))

# ── Output ────────────────────────────────────────────────────────────────────

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

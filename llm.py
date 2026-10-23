"""
LLM factory with automatic fallback and retry logic.

Provides:
  - get_llm(role)             → ChatOpenAI instance for a specific agent role
  - invoke_with_fallback(...) → resilient invocation across multiple models
"""

import logging
import time

from langchain_openai import ChatOpenAI

import config

logger = logging.getLogger(__name__)


# ── Factory ───────────────────────────────────────────────────────────────────

def get_llm(
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> ChatOpenAI:
    """
    Build a ChatOpenAI instance pointing at OpenRouter.

    Parameters
    ----------
    model : str, optional
        Model identifier (e.g. "openrouter/free").
        Defaults to config.DEFAULT_MODEL.
    temperature : float, optional
        Sampling temperature. Defaults to config.TEMPERATURE.
    max_tokens : int, optional
        Max output tokens. Defaults to config.MAX_TOKENS.
    """
    return ChatOpenAI(
        model=model or config.DEFAULT_MODEL,
        base_url=config.OPENROUTER_BASE_URL,
        api_key=config.OPENROUTER_API_KEY,
        temperature=temperature if temperature is not None else config.TEMPERATURE,
        max_tokens=max_tokens or config.MAX_TOKENS,
    )


def get_llm_for_role(role: str) -> ChatOpenAI:
    """
    Return a ChatOpenAI tuned for a specific agent role.
    Uses the model override from config.MODELS[role].
    """
    model = config.MODELS.get(role, config.DEFAULT_MODEL)
    return get_llm(model=model)


# ── Gemini fallback (optional) ────────────────────────────────────────────────

def _get_gemini_llm():
    """
    Build a Gemini LLM if the API key is available.
    Returns None if no key is configured.
    """
    if not config.GEMINI_API_KEY:
        return None
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=config.GEMINI_API_KEY,
            temperature=config.TEMPERATURE,
            max_output_tokens=config.MAX_TOKENS,
        )
    except ImportError:
        logger.warning(
            "langchain-google-genai not installed — Gemini fallback disabled"
        )
        return None


# ── Resilient invocation ──────────────────────────────────────────────────────

def invoke_with_fallback(
    prompt: str,
    role: str = "writer",
    max_retries: int | None = None,
) -> str:
    """
    Invoke an LLM with automatic model fallback and exponential backoff.

    Tries:
      1. The role-specific model from config.MODELS
      2. Each model in config.OPENROUTER_FALLBACK_MODELS
      3. Gemini (if API key is present)

    Returns the model's text response.
    Raises RuntimeError if every provider fails.
    """
    retries = max_retries or config.MAX_RETRIES
    last_error: Exception | None = None

    # Build the ordered list of (label, llm) pairs to try
    candidates: list[tuple[str, object]] = []

    # Primary model for this role
    primary_model = config.MODELS.get(role, config.DEFAULT_MODEL)
    candidates.append((primary_model, get_llm(model=primary_model)))

    # OpenRouter fallbacks (skip if same as primary)
    for fb_model in config.OPENROUTER_FALLBACK_MODELS:
        if fb_model != primary_model:
            candidates.append((fb_model, get_llm(model=fb_model)))

    # Gemini fallback
    gemini = _get_gemini_llm()
    if gemini:
        candidates.append(("gemini-2.0-flash", gemini))

    # Try each candidate with retries
    for model_label, llm_instance in candidates:
        for attempt in range(retries):
            try:
                logger.info(
                    "Invoking %s (attempt %d/%d) for role '%s'",
                    model_label, attempt + 1, retries, role,
                )
                result = llm_instance.invoke(prompt)
                logger.info("Success with %s for role '%s'", model_label, role)
                return result.content

            except Exception as exc:
                last_error = exc
                wait = min(2 ** attempt, 30)  # cap at 30 s
                logger.warning(
                    "%s attempt %d failed (%s). Retrying in %ds…",
                    model_label, attempt + 1, exc, wait,
                )
                time.sleep(wait)

        logger.warning("All retries exhausted for %s", model_label)

    raise RuntimeError(
        f"All LLM providers failed for role '{role}'. Last error: {last_error}"
    )

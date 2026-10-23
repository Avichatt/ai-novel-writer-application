# 📖 Novel Writer — Multi-Agent System

A LangGraph-powered novel-writing pipeline that uses **free LLM APIs** (OpenRouter + Gemini fallback) to generate full-length romance novels chapter by chapter.

## Features

- **9 specialized agents** — strategist, character designer, outliner, story bible, chapter planner, writer, QA editor, reviser, final editor
- **Free-tier optimized** — ~37 API calls per 10-chapter book (under OpenRouter's 50/day free limit)
- **Automatic fallback** — OpenRouter → specific free models → Gemini, with exponential backoff
- **Python-managed memory** — no LLM calls wasted on state tracking
- **DOCX export** — professional manuscript formatting

## Quick Start

### 1. Clone & install

```bash
cd novel-writer
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

Get a free key at [openrouter.ai/keys](https://openrouter.ai/keys).

### 3. Generate a novel

```bash
python main.py "Write a second-chance romance between a firefighter and a pastry chef in a small coastal town"
```

Or run interactively:

```bash
python main.py
```

### 4. Find your output

Generated files appear in `output/`:

```
output/
├── novel_YYYYMMDD_HHMMSS.docx    # The manuscript
└── novel_YYYYMMDD_HHMMSS.json    # Story memory / metadata
```

## Architecture

```
USER PROMPT → Story Strategist → Character Agent → Outline Agent → Story Bible
                                                                        │
                                                                        ▼
                                                              ┌─────────────────┐
                                                              │  CHAPTER LOOP   │
                                                              │  Planner        │
                                                              │  Writer         │
                                                              │  QA Agent       │
                                                              │  Reviser (cond) │
                                                              │  Memory Update  │
                                                              └────────┬────────┘
                                                                       │
                                                              Final Editor → DOCX
```

## Configuration

All settings are configurable via `.env`:

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | *(required)* | Your OpenRouter API key |
| `GEMINI_API_KEY` | *(optional)* | Google Gemini API key for fallback |
| `LLM_MODEL` | `openrouter/free` | Default model for all agents |
| `STRATEGY_MODEL` | `$LLM_MODEL` | Model for story strategist |
| `WRITER_MODEL` | `$LLM_MODEL` | Model for chapter writer |
| `EDITOR_MODEL` | `$LLM_MODEL` | Model for QA & final editor |
| `CHAPTER_COUNT` | `10` | Number of chapters to generate |
| `TARGET_WORDS_PER_CHAPTER` | `1500` | Target word count per chapter |

## API Call Budget

| Phase | Calls |
|---|---|
| Setup (strategist + characters + outliner) | 3 |
| Per chapter (planner + writer + QA) | 3 × N |
| Revisions (conditional, ~30% of chapters) | ~3 |
| Final editor | 1 |
| **Total for 10 chapters** | **~37** |

## License

MIT

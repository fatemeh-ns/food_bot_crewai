# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

This is a small Python CrewAI food-ordering assistant. The app runs an interactive terminal chat, uses an OpenRouter-backed OpenAI-compatible LLM, and exposes two CrewAI tools for recommending food and placing orders against a local SQLite database.

## Setup and common commands

```powershell
# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the interactive food agent
python -m app.main

# Run the CrewAI tool-calling benchmark
python benchmark_crewai.py

# Basic syntax/import check; there is no automated test suite in this repo yet
python -m compileall app benchmark_crewai.py
```

Runtime configuration:
- `OPENROUTER_API_KEY` must be available in the environment or in `.env` for LLM calls.
- The code disables CrewAI telemetry with `CREWAI_DISABLE_TELEMETRY=true` in both runtime entry points.
- `.env`, `*.db`, `*.log`, and `__pycache__/` are ignored by git. `food.db` and `orders.log` are local runtime artifacts.

## Architecture

- `app/main.py` is the interactive CLI entry point. It loads `.env`, keeps an in-memory `chat_history`, builds a new CrewAI `Task` for each user message, runs a single-agent `Crew`, prints the result, and stores the last exchanges for context.
- `app/agent.py` defines the production `food_agent`. The LLM is configured as `openai/gpt-4o-mini` through OpenRouter (`https://openrouter.ai/api/v1`) with temperature `0`. The agent is given both food tools and is instructed to support Persian and English.
- `app/tools/recommend_tool.py` defines the `recommend_food` CrewAI tool. It queries the `foods` table with optional filters for `max_price`, `vegetarian`, and `spicy`, then returns JSON with Persian text when no matches are found.
- `app/tools/reserve_tool.py` defines the `reserve_food` CrewAI tool. It inserts an order into the `orders` table and appends a JSON line to `orders.log`; the returned JSON reports a pending order.
- `app/db.py` centralizes SQLite connection creation with `sqlite3.connect("food.db")`. Because this is a relative path, commands should normally be run from the repository root unless the connection path is changed.
- `benchmark_crewai.py` is a standalone benchmark that duplicates LLM setup and compares an agent with tools against an agent without tools for a fixed Persian food-preference prompt.

The local SQLite schema expected by the tools is:
- `foods(id, name, category, price, calories, spicy, vegetarian)`
- `orders(id, food_id, user_name, status, created_at)`

## Implementation notes

- Tool return values are JSON strings, not Python objects. Preserve `ensure_ascii=False` when returning Persian text.
- `reserve_food` has a side effect in both SQLite and `orders.log`; avoid running it in tests or benchmarks unless an order side effect is intended.
- There is duplicated LLM/agent setup between `app/agent.py` and `benchmark_crewai.py`; update both if changing model/provider configuration, or refactor to share configuration first.

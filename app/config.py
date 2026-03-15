"""Centralised configuration loaded from environment variables."""
from __future__ import annotations

import os
from pathlib import Path


# ── Data paths ──────────────────────────────────────────────────────────────
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
DATA_DIR.mkdir(exist_ok=True)

RAW_FILE   = DATA_DIR / "errors_raw.jsonl"
DIAG_FILE  = DATA_DIR / "errors_diag.jsonl"
STATE_FILE = DATA_DIR / "dashboard_state.json"

# ── LLM provider ─────────────────────────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "llama_cpp").strip().lower()
LLM_TIMEOUT  = int(os.getenv("LLM_TIMEOUT", "180"))

# llama.cpp / local OpenAI-compatible server
LLAMA_BASE_URL   = os.getenv("LLAMA_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
LLAMA_MODEL_NAME = os.getenv("LLAMA_MODEL_NAME", "Qwen2.5-7B-Instruct-Q4_K_M.gguf")

# OpenAI / compatible cloud providers
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL    = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def active_model_name() -> str:
    """Return the model identifier for the currently configured provider."""
    return OPENAI_MODEL if LLM_PROVIDER == "openai" else LLAMA_MODEL_NAME

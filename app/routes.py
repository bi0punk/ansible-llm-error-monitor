"""FastAPI application and route definitions."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app import config, state, worker
from app.config import RAW_FILE
from app.dashboard import DASHBOARD_HTML
from app.llm import build_error_title
from app.models import ErrorPayload
from app.storage import append_jsonl, read_jsonl

app = FastAPI(title="Ansible LLM Error Monitor", version="2.0.0")


@app.on_event("startup")
def _startup():
    from app.config import STATE_FILE
    from app.storage import save_state

    if not STATE_FILE.exists():
        save_state(state.get())
    worker.start()


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> dict[str, Any]:
    llm_ok, llm_detail = False, None
    try:
        if config.LLM_PROVIDER == "openai":
            headers = {"Authorization": f"Bearer {config.OPENAI_API_KEY}"} if config.OPENAI_API_KEY else {}
            r = requests.get(f"{config.OPENAI_BASE_URL}/models", headers=headers, timeout=10)
        else:
            r = requests.get(f"{config.LLAMA_BASE_URL}/v1/models", timeout=10)
        llm_ok     = r.ok
        llm_detail = r.json()
    except Exception as exc:
        llm_detail = {"error": str(exc)}

    return {
        "ok":             True,
        "llm_provider":   config.LLM_PROVIDER,
        "llm_model":      config.active_model_name(),
        "llm_ok":         llm_ok,
        "llm_detail":     llm_detail,
        "queue_size":     state.analysis_queue.qsize(),
    }


# ── Ingest ────────────────────────────────────────────────────────────────────

@app.post("/api/ingest-error")
def ingest_error(payload: ErrorPayload) -> dict[str, Any]:
    raw_record = {
        "received_at": datetime.utcnow().isoformat() + "Z",
        "title":       build_error_title(payload),
        "payload":     payload.model_dump(),
    }
    append_jsonl(RAW_FILE, raw_record)
    state.set_latest_raw(raw_record)
    state.analysis_queue.put({"payload": payload.model_dump()})
    state.set_queued(payload)

    return {
        "ok":        True,
        "queued":    True,
        "queue_size": state.analysis_queue.qsize(),
        "title":     build_error_title(payload),
    }


# ── Dashboard data ────────────────────────────────────────────────────────────

@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    return state.get()


@app.get("/api/history")
def history(limit: int = 50) -> dict[str, Any]:
    from app.config import DIAG_FILE
    records = read_jsonl(DIAG_FILE, limit=limit)
    return {"count": len(records), "records": records}


# ── UI ────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return DASHBOARD_HTML

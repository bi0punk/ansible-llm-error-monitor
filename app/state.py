"""Dashboard state management: read, update, mutate with thread safety."""
from __future__ import annotations

import queue
from collections.abc import Callable
from datetime import datetime
from typing import Any

from app import config
from app.models import ErrorPayload
from app.storage import get_state_lock, load_state, save_state

# Shared analysis queue – imported here so all modules share the same object
analysis_queue: queue.Queue[dict[str, Any]] = queue.Queue()


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _default() -> dict[str, Any]:
    return {
        "system": {
            "status": "idle",
            "queue_size": 0,
            "last_update": _now(),
            "current_task_label": None,
            "last_error_message": None,
            "llm_provider": config.LLM_PROVIDER,
            "llm_model": config.active_model_name(),
            "total_analyzed": 0,
            "total_errors": 0,
        },
        "latest_raw": None,
        "latest_result": None,
        "recent_results": [],   # last 10 diagnoses for history panel
    }


def get() -> dict[str, Any]:
    with get_state_lock():
        return load_state(_default())


def update(mutator: Callable[[dict[str, Any]], dict[str, Any] | None]) -> dict[str, Any]:
    with get_state_lock():
        current = load_state(_default())
        updated = mutator(current) or current
        sys = updated["system"]
        sys["queue_size"]   = analysis_queue.qsize()
        sys["last_update"]  = _now()
        sys["llm_provider"] = config.LLM_PROVIDER
        sys["llm_model"]    = config.active_model_name()
        save_state(updated)
        return updated


# ── Named mutators ────────────────────────────────────────────────────────────

def set_analyzing(payload: ErrorPayload) -> None:
    from app.llm import build_error_title

    def _mutate(s: dict) -> dict:
        s["system"]["status"] = "analyzing"
        s["system"]["current_task_label"] = build_error_title(payload)
        s["system"]["last_error_message"] = None
        return s

    update(_mutate)


def set_done(payload: ErrorPayload, diag: dict[str, Any]) -> None:
    def _mutate(s: dict) -> dict:
        idle = analysis_queue.qsize() == 0
        s["system"]["status"] = "idle" if idle else "queued"
        s["system"]["current_task_label"] = None if idle else s["system"].get("current_task_label")
        s["system"]["last_error_message"] = None
        s["system"]["total_analyzed"] = s["system"].get("total_analyzed", 0) + 1
        s["latest_result"] = diag

        # Keep rolling history of last 10
        recent: list = s.get("recent_results", [])
        recent.append(diag)
        s["recent_results"] = recent[-10:]
        return s

    update(_mutate)


def set_error(payload: ErrorPayload, error_msg: str) -> None:
    from app.llm import build_error_title

    def _mutate(s: dict) -> dict:
        s["system"]["status"] = "error"
        s["system"]["current_task_label"] = build_error_title(payload)
        s["system"]["last_error_message"] = error_msg
        s["system"]["total_errors"] = s["system"].get("total_errors", 0) + 1
        return s

    update(_mutate)


def set_queued(payload: ErrorPayload) -> None:
    from app.llm import build_error_title

    def _mutate(s: dict) -> dict:
        if s["system"]["status"] != "analyzing":
            s["system"]["status"] = "queued"
        s["system"]["current_task_label"] = build_error_title(payload)
        s["system"]["last_error_message"] = None
        return s

    update(_mutate)


def set_latest_raw(raw_record: dict[str, Any]) -> None:
    def _mutate(s: dict) -> dict:
        s["latest_raw"] = raw_record
        return s

    update(_mutate)

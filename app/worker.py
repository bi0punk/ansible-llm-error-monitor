"""Background worker: consumes the analysis queue and calls the LLM."""
from __future__ import annotations

import threading
from datetime import datetime
from typing import Any

from app import state
from app.config import DIAG_FILE
from app.llm import diagnose
from app.models import ErrorPayload
from app.storage import append_jsonl


def _process(item: dict[str, Any]) -> None:
    payload = ErrorPayload(**item["payload"])
    try:
        state.set_analyzing(payload)
        result = diagnose(payload)

        diag_record = {
            "received_at":    datetime.utcnow().isoformat() + "Z",
            "fingerprint":    payload.fingerprint,
            "host":           payload.host,
            "task":           payload.task,
            "title":          result["title"],
            "natural_report": result["natural_report"],
            "analyzed_at":    result["analyzed_at"],
            "provider":       result["provider"],
            "model":          result["model"],
            "severity":       result.get("severity"),
            "confidence":     result.get("confidence"),
        }
        append_jsonl(DIAG_FILE, diag_record)
        state.set_done(payload, diag_record)

    except Exception as exc:
        state.set_error(payload, str(exc))
    finally:
        state.analysis_queue.task_done()


def _loop() -> None:
    while True:
        item = state.analysis_queue.get()
        _process(item)


def start() -> threading.Thread:
    """Spawn and return the daemon worker thread."""
    t = threading.Thread(target=_loop, daemon=True, name="llm-worker")
    t.start()
    return t

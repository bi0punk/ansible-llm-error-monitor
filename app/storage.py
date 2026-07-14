"""Thin persistence helpers: JSONL append and JSON state read/write."""
from __future__ import annotations

import contextlib
import json
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any

from app.config import STATE_FILE

_state_lock = threading.Lock()


# ── JSONL helpers ─────────────────────────────────────────────────────────────

def append_jsonl(path: Path, data: dict[str, Any]) -> None:
    import fcntl
    line = json.dumps(data, ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(line)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def read_jsonl(path: Path, limit: int = 50) -> list[dict[str, Any]]:
    """Return the last *limit* records from a JSONL file (most recent last)."""
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    records = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        with contextlib.suppress(json.JSONDecodeError):
            records.append(json.loads(line))
    return records[-limit:]


# ── JSON state file ──────────────────────────────────────────────────────────

def load_state(default: dict[str, Any]) -> dict[str, Any]:
    if not STATE_FILE.exists():
        return deepcopy(default)
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return deepcopy(default)


def save_state(data: dict[str, Any]) -> None:
    import os
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(STATE_FILE)


def get_state_lock() -> threading.Lock:
    return _state_lock

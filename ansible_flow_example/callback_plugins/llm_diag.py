# callback_plugins/llm_diag.py
from __future__ import annotations

import json
import os
import time
import hashlib
from typing import Any

from ansible.plugins.callback import CallbackBase

try:
    import requests
except ImportError:
    requests = None


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "llm_diag"
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self) -> None:
        super().__init__()
        self.endpoint = os.getenv("LLM_DIAG_BACKEND", "http://127.0.0.1:8090/api/ingest-error")
        self.timeout = float(os.getenv("LLM_DIAG_TIMEOUT", "5"))

    def _fingerprint(self, payload: dict[str, Any]) -> str:
        raw = json.dumps(
            {
                "host": payload.get("host"),
                "task": payload.get("task"),
                "event_type": payload.get("event_type"),
                "msg": payload.get("msg"),
                "rc": payload.get("rc"),
            },
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    def _build_payload(self, result, event_type: str) -> dict[str, Any]:
        host = result._host.get_name() if result._host else None
        task = result._task.get_name() if result._task else None
        raw = result._result if isinstance(result._result, dict) else {"raw_result": str(result._result)}

        payload = {
            "event_type": event_type,
            "host": host,
            "task": task,
            "action": getattr(result._task, "action", None) if result._task else None,
            "msg": raw.get("msg"),
            "stderr": raw.get("stderr"),
            "stdout": raw.get("stdout"),
            "exception": raw.get("exception"),
            "rc": raw.get("rc"),
            "changed": raw.get("changed"),
            "failed": raw.get("failed"),
            "unreachable": raw.get("unreachable"),
            "timestamp": int(time.time()),
            "raw_result": raw,
        }
        payload["fingerprint"] = self._fingerprint(payload)
        return payload

    def _send(self, payload: dict[str, Any]) -> None:
        if requests is None:
            self._display.warning("requests no está instalado en el nodo controlador")
            return
        try:
            requests.post(self.endpoint, json=payload, timeout=self.timeout)
        except Exception as exc:
            self._display.warning(f"No se pudo enviar error al backend LLM: {exc}")

    def v2_runner_on_failed(self, result, ignore_errors=False):
        payload = self._build_payload(result, "runner_on_failed")
        payload["ignore_errors"] = ignore_errors
        self._send(payload)

    def v2_runner_on_unreachable(self, result):
        payload = self._build_payload(result, "runner_on_unreachable")
        self._send(payload)

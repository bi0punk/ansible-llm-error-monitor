"""LLM client: prompt building and provider-agnostic inference call."""
from __future__ import annotations

import re
from typing import Any

import requests

from app import config
from app.models import ErrorPayload


# ── Prompt helpers ────────────────────────────────────────────────────────────

def build_error_title(payload: ErrorPayload) -> str:
    parts = []
    if payload.event_type:
        parts.append(payload.event_type.replace("_", " ").upper())
    if payload.task:
        parts.append(payload.task)
    if payload.host:
        parts.append(f"host {payload.host}")
    return " · ".join(parts) if parts else "Error sin título"


_PROMPT_TEMPLATE = """\
Eres un analista senior de incidentes Ansible/SRE.

Tu tarea es SOLO diagnosticar el error en lenguaje natural claro, técnico y profesional.
No ejecutes acciones.
No sugieras automatizaciones.
No inventes contexto que no esté presente.
No respondas en JSON.
No respondas en viñetas excesivas.
No repitas el payload completo.

Debes responder con este formato exacto en español:

Título: <una línea breve y profesional>

Resumen:
<un párrafo breve explicando qué falló>

Diagnóstico:
<uno o dos párrafos explicando la causa más probable en lenguaje natural>

Validaciones recomendadas:
1. ...
2. ...
3. ...

Severidad: <low|medium|high|critical>
Confianza: <0.0 a 1.0>

Datos del error:
{payload_json}
"""


def _build_prompt(payload: ErrorPayload) -> str:
    return _PROMPT_TEMPLATE.format(payload_json=payload.model_dump_json(indent=2))


# ── Low-level HTTP call ───────────────────────────────────────────────────────

def _call_openai_compat(base_url: str, model: str, api_key: str | None, messages: list[dict]) -> str:
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
    }

    resp = requests.post(
        f"{base_url}/chat/completions",
        json=body,
        headers=headers,
        timeout=config.LLM_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


# ── Public interface ──────────────────────────────────────────────────────────

def _parse_severity(text: str) -> str | None:
    m = re.search(r"Severidad:\s*(low|medium|high|critical)", text, re.IGNORECASE)
    return m.group(1).lower() if m else None


def _parse_confidence(text: str) -> float | None:
    m = re.search(r"Confianza:\s*([0-9]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
    return float(m.group(1)) if m else None


def diagnose(payload: ErrorPayload) -> dict[str, Any]:
    """Run LLM diagnosis and return a structured result dict."""
    messages = [
        {
            "role": "system",
            "content": "Eres un analista técnico senior. Responde en español, claro, natural y profesional.",
        },
        {"role": "user", "content": _build_prompt(payload)},
    ]

    if config.LLM_PROVIDER == "openai":
        if not config.OPENAI_API_KEY:
            raise RuntimeError("LLM_PROVIDER=openai pero OPENAI_API_KEY no está definido")
        content = _call_openai_compat(
            base_url=config.OPENAI_BASE_URL,
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY,
            messages=messages,
        )
    elif config.LLM_PROVIDER == "llama_cpp":
        content = _call_openai_compat(
            base_url=f"{config.LLAMA_BASE_URL}/v1",
            model=config.LLAMA_MODEL_NAME,
            api_key=None,
            messages=messages,
        )
    else:
        raise RuntimeError(f"Proveedor LLM no soportado: {config.LLM_PROVIDER}")

    from datetime import datetime
    return {
        "title":          build_error_title(payload),
        "natural_report": content,
        "analyzed_at":    datetime.utcnow().isoformat() + "Z",
        "provider":       config.LLM_PROVIDER,
        "model":          config.active_model_name(),
        "severity":       _parse_severity(content),
        "confidence":     _parse_confidence(content),
    }

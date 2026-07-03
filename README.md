# Ansible LLM Error Monitor v2

[![CI](https://github.com/bi0punk/ansible-llm-error-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/bi0punk/ansible-llm-error-monitor/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Real-time Ansible error ingestion with LLM-powered diagnosis — modular, production-ready.

## Tabla de contenidos

- [Stack](#stack)
- [Arquitectura](#arquitectura)
- [Quick start](#quick-start)
- [Variables de entorno](#environment-variables)
- [API endpoints](#api-endpoints)
- [Envío de error de prueba](#sending-a-test-error)
- [Tests](#tests)
- [CI](#ci)
- [Datos](#data-files-in-data)
- [Ejemplo de flujo Ansible](#ejemplo-de-flujo-ansible)
- [Licencia](#licencia)

## Stack

- Python 3.12+
- FastAPI + Uvicorn
- Pydantic v2 (modelos)
- requests (LLM HTTP)
- LLM providers: llama.cpp (local) u OpenAI-compatible
- Persistencia: JSONL + JSON state (sin DB)
- Calidad: ruff (lint), pytest

## Arquitectura

```
ansible_monitor/
├── main.py              ← Entrypoint (uvicorn)
├── requirements.txt
└── app/
    ├── __init__.py
    ├── config.py        ← All env-var configuration in one place
    ├── models.py        ← Pydantic data models (ErrorPayload, DiagRecord)
    ├── storage.py       ← JSONL append + JSON state R/W helpers
    ├── llm.py           ← Prompt building + provider-agnostic LLM call
    ├── state.py         ← Thread-safe dashboard state manager + queue
    ├── worker.py        ← Background daemon: dequeues → diagnoses → persists
    ├── routes.py        ← FastAPI app, all HTTP endpoints
    └── dashboard.py     ← Dashboard HTML (single const string)
```

## Quick start

```bash
pip install -r requirements.txt
uvicorn main:app --reload
# Open http://localhost:8000
```

## Environment variables

| Variable          | Default                          | Description                         |
|-------------------|----------------------------------|-------------------------------------|
| `LLM_PROVIDER`    | `llama_cpp`                      | `llama_cpp` or `openai`             |
| `LLAMA_BASE_URL`  | `http://127.0.0.1:8080`          | llama.cpp server URL                |
| `LLAMA_MODEL_NAME`| `Qwen2.5-7B-Instruct-Q4_K_M.gguf`| Model file name                    |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1`      | OpenAI-compatible base URL          |
| `OPENAI_API_KEY`  | *(empty)*                        | API key for OpenAI provider         |
| `OPENAI_MODEL`    | `gpt-4.1-mini`                   | Model identifier                    |
| `LLM_TIMEOUT`     | `180`                            | Seconds before LLM request times out|
| `DATA_DIR`        | `./data`                         | Directory for JSONL/JSON files      |

## API endpoints

| Method | Path                | Description                              |
|--------|---------------------|------------------------------------------|
| `GET`  | `/`                 | Live dashboard UI                        |
| `GET`  | `/health`           | Backend + LLM connectivity check        |
| `POST` | `/api/ingest-error` | Receive an Ansible error payload         |
| `GET`  | `/api/dashboard`    | Current state (polled by UI every 2s)   |
| `GET`  | `/api/history`      | Last N diagnosed errors (`?limit=50`)   |

## Sending a test error

```bash
curl -X POST http://localhost:8000/api/ingest-error \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "runner_on_failed",
    "host": "web-prod-01",
    "task": "Install nginx package",
    "action": "ansible.builtin.apt",
    "msg": "No package matching \"nginx\" found",
    "rc": 1,
    "failed": true,
    "fingerprint": "abc123"
  }'
```

## Data files (in `./data/`)

- `errors_raw.jsonl`  — every raw inbound payload
- `errors_diag.jsonl` — every completed LLM diagnosis
- `dashboard_state.json` — live dashboard state (overwritten on every update)

## Tests

```bash
DATA_DIR=/tmp/ansible-monitor-data LLM_PROVIDER=none pytest -q
```

Smoke tests (`tests/test_smoke.py`): health, ingest-error (POST), dashboard + history. Usan `LLM_PROVIDER=none` (sin LLM real) y `DATA_DIR` efímero.

## CI

GitHub Actions (`.github/workflows/ci.yml`) sobre Python 3.12:

- **lint** — `ruff check .`
- **test** — `pytest -q` con `DATA_DIR=/tmp/...` + `LLM_PROVIDER=none` (no requiere LLM real).

## Ejemplo de flujo Ansible

El directorio `ansible_flow_example/` contiene un playbook de demostración con:
- callback plugin (`llm_diag.py`) que POSTea errores al monitor.
- inventario, group_vars, roles demo.
- scripts para simular fallos (`run_fail_assert.sh`, `run_fail_command.sh`, `run_ok.sh`).

Ver `ansible_flow_example/README.md` para detalles.

## Licencia

MIT — ver [LICENSE](LICENSE).

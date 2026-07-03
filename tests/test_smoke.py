"""Smoke tests para ansible-llm-error-monitor API (sin LLM real)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("LLM_PROVIDER", "none")
    import importlib

    import app.config as config
    importlib.reload(config)
    import app.storage as storage
    importlib.reload(storage)
    import app.state as state
    importlib.reload(state)
    import app.llm as llm
    importlib.reload(llm)
    import app.routes as routes
    importlib.reload(routes)
    import main as mainmod
    importlib.reload(mainmod)

    with TestClient(mainmod.app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True


def test_ingest_error(client):
    payload = {
        "host": "web1",
        "task": "Install nginx",
        "action": "apt",
        "msg": "Failed to install",
        "stderr": "E: Unable to locate package nginx",
        "failed": True,
        "rc": 1,
        "timestamp": 1709510400,
    }
    r = client.post("/api/ingest-error", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True
    assert body["queued"] is True
    assert "title" in body


def test_dashboard_and_history(client):
    client.post("/api/ingest-error", json={"host": "h1", "task": "t1", "failed": True, "msg": "boom"})
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert "system" in data
    r = client.get("/api/history")
    assert r.status_code == 200
    data = r.json()
    assert "records" in data
    assert isinstance(data["records"], list)
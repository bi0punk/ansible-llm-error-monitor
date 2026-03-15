"""Pydantic data models shared across the application."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorPayload(BaseModel):
    event_type:   str | None = None
    host:         str | None = None
    task:         str | None = None
    action:       str | None = None
    msg:          str | None = None
    stderr:       str | None = None
    stdout:       str | None = None
    exception:    str | None = None
    rc:           int | None = None
    changed:      bool | None = None
    failed:       bool | None = None
    unreachable:  bool | None = None
    timestamp:    int | None = None
    fingerprint:  str | None = None
    ignore_errors: bool | None = None
    raw_result:   dict[str, Any] = Field(default_factory=dict)


class DiagRecord(BaseModel):
    received_at:    str
    fingerprint:    str | None
    host:           str | None
    task:           str | None
    title:          str
    natural_report: str
    analyzed_at:    str
    provider:       str
    model:          str
    severity:       str | None = None
    confidence:     float | None = None

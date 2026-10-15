"""Deterministic recorded trajectories in iFixAi's capture format (schema 1).

Events have readable IDs ("approval", "refund") and fixed times, so every mutant is the same file on
every run. A trajectory is edited as plain data, then validated by iFixAi's own Pydantic models: a
mutant that iFixAi's schema rejects never reaches the audit.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ifixai.trajectory.integrity import canonical_digest
from ifixai.trajectory.models import TraceCapture

TRACE_ID = "a0d17a0d17a0d17a0d17a0d17a0d17a0"
TENANT = "demo-tenant"
COLLECTOR = "local-observer"
START_NS = 100


def digest(value: Any) -> str:
    """iFixAi's canonical SHA-256 of a JSON value, as its recorder computes argument digests."""
    return canonical_digest(value)


# Fields of a payload that refer to another event by its ID.
_REFERENCES = ("approval_id", "delegation_id", "grant_id", "parent_grant_id")


@dataclass
class Event:
    id: str
    payload: dict[str, Any]
    parents: tuple[str, ...] | None = None  # None: the previous event, as iFixAi's recorder does
    time_ns: int | None = None  # None: one nanosecond after the previous event


@dataclass
class Trace:
    events: list[Event] = field(default_factory=list)
    complete: bool = True
    collector_id: str = COLLECTOR
    tenant_id: str = TENANT
    declared_events: int | None = None  # None: the true count, as an honest recorder declares

    def copy(self) -> Trace:
        return copy.deepcopy(self)

    def index(self, event_id: str) -> int:
        for i, event in enumerate(self.events):
            if event.id == event_id:
                return i
        raise KeyError(event_id)

    def get(self, event_id: str) -> Event:
        return self.events[self.index(event_id)]

    def add(self, event: Event, after: str | None = None) -> Trace:
        at = len(self.events) if after is None else self.index(after) + 1
        self.events.insert(at, event)
        return self

    def remove(self, event_id: str) -> Trace:
        del self.events[self.index(event_id)]
        return self

    def set(self, event_id: str, **fields: Any) -> Trace:
        """Change payload fields of one event; None removes a field."""
        payload = self.get(event_id).payload
        for key, value in fields.items():
            if value is None:
                payload.pop(key, None)
            else:
                payload[key] = value
        return self

    def rows(self) -> list[dict[str, Any]]:
        """The events as iFixAi's JSONL rows, ending with the end event the recorder seals with."""
        rows: list[dict[str, Any]] = []
        time = START_NS - 1
        for i, event in enumerate(self.events):
            time = event.time_ns if event.time_ns is not None else time + 1
            parents = (
                event.parents if event.parents is not None else ((rows[-1]["event_id"],) if rows else ())
            )
            rows.append(
                {
                    "event_id": event.id,
                    "trace_id": TRACE_ID,
                    "tenant_id": self.tenant_id,
                    "sequence": i + 1,
                    "time_ns": time,
                    "parents": list(parents),
                    "payload": copy.deepcopy(event.payload),
                }
            )
        count = len(rows) + 1
        rows.append(
            {
                "event_id": "end",
                "trace_id": TRACE_ID,
                "tenant_id": self.tenant_id,
                "sequence": count,
                "time_ns": time + 1,
                "parents": [rows[-1]["event_id"]] if rows else [],
                "payload": {
                    "kind": "end",
                    "complete": self.complete,
                    "declared_events": self.declared_events or count,
                },
            }
        )
        return rows

    def header(self) -> dict[str, Any]:
        return {
            "schema_version": "1",
            "trace_id": TRACE_ID,
            "tenant_id": self.tenant_id,
            "collector_id": self.collector_id,
            "capture_complete": self.complete,
            "source_format": "jsonl",
        }

    def capture(self) -> TraceCapture:
        """Validated by iFixAi's models; raises if the schema rejects the trajectory."""
        return TraceCapture.model_validate({**self.header(), "events": self.rows()})

    def jsonl(self) -> str:
        self.capture()
        return "\n".join(json.dumps(row, ensure_ascii=False) for row in [self.header(), *self.rows()]) + "\n"

    def hexified(self) -> Trace:
        """The same trajectory with 16-hex event IDs, which OTLP span IDs require."""
        names = {event.id: f"{i + 1:016x}" for i, event in enumerate(self.events)}
        out = self.copy()
        for event in out.events:
            event.id = names[event.id]
            if event.parents is not None:
                event.parents = tuple(names[p] for p in event.parents)
            for key in _REFERENCES:
                if key in event.payload and event.payload[key] in names:
                    event.payload[key] = names[event.payload[key]]
            for citation in event.payload.get("citations", ()):
                citation["source_event_id"] = names.get(
                    citation["source_event_id"], citation["source_event_id"]
                )
        return out

    def otlp(self) -> dict[str, Any]:
        """An OTLP JSON export in the shape of iFixAi's own example (examples/trajectory_assurance.py)."""
        capture = self.hexified().capture()
        rows = [event.model_dump(mode="json") for event in capture.events]
        names = {row["event_id"]: f"{i + 1:016x}" for i, row in enumerate(rows)}  # the end event too
        attributes = [
            {"key": "ifixai.tenant_id", "value": {"stringValue": capture.tenant_id}},
            {"key": "ifixai.collector_id", "value": {"stringValue": capture.collector_id}},
            {"key": "ifixai.capture_complete", "value": {"boolValue": capture.capture_complete}},
        ]
        spans = []
        for row in rows:
            row = {**row, "event_id": names[row["event_id"]], "parents": [names[p] for p in row["parents"]]}
            spans.append(
                {
                    "traceId": row["trace_id"],
                    "spanId": row["event_id"],
                    "parentSpanId": row["parents"][0] if row["parents"] else "",
                    "name": "explicit recorded semantic event",
                    "kind": 1,
                    "startTimeUnixNano": str(row["time_ns"]),
                    "endTimeUnixNano": str(row["time_ns"]),
                    "attributes": [{"key": "ifixai.event", "value": {"stringValue": json.dumps(row)}}],
                }
            )
        return {
            "resourceSpans": [
                {
                    "resource": {"attributes": attributes},
                    "scopeSpans": [{"scope": {"name": "local-trajectory-observer"}, "spans": spans}],
                }
            ]
        }

    def write(self, path: Path, fmt: str = "jsonl") -> Path:
        if fmt == "otlp":
            path.write_text(json.dumps(self.otlp(), indent=1), encoding="utf-8")
        else:
            path.write_text(self.jsonl(), encoding="utf-8")
        return path

"""
Domain Layer — Domain Events

Events raised by domain entities to communicate state changes.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=_utcnow)

    @property
    def event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    email: str = ""
    role: str = "user"


@dataclass(frozen=True)
class UserDeactivated(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    reason: str = ""


@dataclass(frozen=True)
class UserLoggedIn(DomainEvent):
    user_id: uuid.UUID = field(default_factory=uuid.uuid4)
    ip_address: str = ""


@dataclass(frozen=True)
class ProjectCreated(DomainEvent):
    project_id: uuid.UUID = field(default_factory=uuid.uuid4)
    owner_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""


@dataclass(frozen=True)
class ProjectArchived(DomainEvent):
    project_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class PipelineCreated(DomainEvent):
    pipeline_id: uuid.UUID = field(default_factory=uuid.uuid4)
    project_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""


@dataclass(frozen=True)
class PipelineActivated(DomainEvent):
    pipeline_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class PipelineExecutionStarted(DomainEvent):
    execution_id: uuid.UUID = field(default_factory=uuid.uuid4)
    pipeline_id: uuid.UUID = field(default_factory=uuid.uuid4)
    triggered_by: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class PipelineExecutionCompleted(DomainEvent):
    execution_id: uuid.UUID = field(default_factory=uuid.uuid4)
    pipeline_id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: str = ""
    duration_seconds: float | None = None
    error: str | None = None


class EventBus:
    """Simple in-process event bus for domain events."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Any]] = {}

    def subscribe(self, event_type: str, handler: Any) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(event.event_type, []):
            await handler(event)

    async def publish_many(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)

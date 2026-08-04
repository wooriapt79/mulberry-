"""Governed safety-event workflow for the Mulberry WiFi Sense research MVP.

This module never contacts emergency services or external messaging systems.
It converts an uncalibrated simulation/model score into an auditable candidate
event and requires an explicit human decision before local dispatch simulation.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Optional


class ConsentState(str, Enum):
    REQUESTED = "requested"
    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ApprovalState(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class DetectionCandidate:
    event_id: str
    event_type: str
    simulation_score: float
    score_is_calibrated_probability: bool
    location: str
    observed_at: str
    consent_state: ConsentState
    approval_state: ApprovalState = ApprovalState.PENDING


@dataclass(frozen=True)
class AuditRecord:
    event_id: str
    action: str
    actor_id: str
    reason: str
    occurred_at: str
    previous_hash: str
    record_hash: str


class SafetyWorkflow:
    """Consent-gated, human-approved local research workflow."""

    def __init__(self) -> None:
        self.consent_state = ConsentState.REQUESTED
        self.candidates: dict[str, DetectionCandidate] = {}
        self.audit_log: list[AuditRecord] = []

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def set_consent(self, state: ConsentState, actor_id: str, reason: str) -> None:
        if state == ConsentState.REQUESTED:
            raise ValueError("requested is the initial state, not a human decision")
        self.consent_state = state
        self._audit("consent.updated", "consent", actor_id, reason)

    def create_candidate(
        self, event_type: str, simulation_score: float, location: str
    ) -> DetectionCandidate:
        if self.consent_state != ConsentState.GRANTED:
            raise PermissionError("active sensing requires granted consent")
        if not 0.0 <= simulation_score <= 1.0:
            raise ValueError("simulation_score must be between 0 and 1")
        candidate = DetectionCandidate(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            simulation_score=simulation_score,
            score_is_calibrated_probability=False,
            location=location,
            observed_at=self._now(),
            consent_state=self.consent_state,
        )
        self.candidates[candidate.event_id] = candidate
        self._audit(candidate.event_id, "candidate.created", "edge-simulator", "review required")
        return candidate

    def decide(
        self,
        event_id: str,
        approved: bool,
        actor_id: str,
        reason: str,
        dispatch_simulator: Optional[Callable[[DetectionCandidate], None]] = None,
    ) -> DetectionCandidate:
        candidate = self.candidates[event_id]
        if candidate.approval_state != ApprovalState.PENDING:
            raise RuntimeError("candidate has already been decided")
        state = ApprovalState.APPROVED if approved else ApprovalState.REJECTED
        decided = DetectionCandidate(**{**asdict(candidate), "consent_state": candidate.consent_state, "approval_state": state})
        self.candidates[event_id] = decided
        self._audit(event_id, f"candidate.{state.value}", actor_id, reason)
        if approved and dispatch_simulator is not None:
            dispatch_simulator(decided)
            self._audit(event_id, "dispatch.simulated", actor_id, "local simulation only")
        return decided

    def _audit(self, event_id: str, action: str, actor_id: str, reason: str) -> None:
        previous_hash = self.audit_log[-1].record_hash if self.audit_log else "GENESIS"
        body = {
            "event_id": event_id,
            "action": action,
            "actor_id": actor_id,
            "reason": reason,
            "occurred_at": self._now(),
            "previous_hash": previous_hash,
        }
        record_hash = hashlib.sha256(
            json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        self.audit_log.append(AuditRecord(**body, record_hash=record_hash))

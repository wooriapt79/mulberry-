"""Governed safety-event workflow for the Mulberry WiFi Sense research MVP.

This module never contacts emergency services or external messaging systems.
It converts an uncalibrated simulation/model score into an auditable candidate
event and requires an authenticated Steward Human decision before local
dispatch simulation.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
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


class StewardAuthorizer:
    """Minimal MVP verifier for registered Steward Human identities.

    Production deployments must replace this shared-secret verifier with Agent
    Passport or an equivalent signed identity and role assertion.
    """

    def __init__(self, credentials: dict[str, str]) -> None:
        if not credentials:
            raise ValueError("at least one Steward Human must be registered")
        self._credential_hashes = {
            actor_id: hashlib.sha256(secret.encode("utf-8")).digest()
            for actor_id, secret in credentials.items()
        }

    def verify(self, actor_id: str, credential: str) -> bool:
        expected = self._credential_hashes.get(actor_id)
        if expected is None:
            return False
        supplied = hashlib.sha256(credential.encode("utf-8")).digest()
        return hmac.compare_digest(expected, supplied)


class SafetyWorkflow:
    """Consent-gated, authenticated-human-approved local research workflow."""

    def __init__(
        self,
        steward_authorizer: StewardAuthorizer,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self.steward_authorizer = steward_authorizer
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self.consent_state = ConsentState.REQUESTED
        self.consent_granted_at: Optional[datetime] = None
        self.consent_expires_at: Optional[datetime] = None
        self.candidates: dict[str, DetectionCandidate] = {}
        self.audit_log: list[AuditRecord] = []

    def _now_datetime(self) -> datetime:
        now = self._clock()
        if now.tzinfo is None:
            raise ValueError("clock must return a timezone-aware datetime")
        return now.astimezone(timezone.utc)

    def _now(self) -> str:
        return self._now_datetime().isoformat()

    def set_consent(
        self,
        state: ConsentState,
        actor_id: str,
        reason: str,
        valid_for: Optional[timedelta] = None,
    ) -> None:
        if state in (ConsentState.REQUESTED, ConsentState.EXPIRED):
            raise ValueError("requested and expired are system-managed states")
        if state == ConsentState.GRANTED:
            if valid_for is None or valid_for <= timedelta(0):
                raise ValueError("granted consent requires a positive validity period")
            self.consent_granted_at = self._now_datetime()
            self.consent_expires_at = self.consent_granted_at + valid_for
        else:
            self.consent_granted_at = None
            self.consent_expires_at = None
        self.consent_state = state
        self._audit("consent", "consent.updated", actor_id, reason)

    def _require_active_consent(self) -> None:
        if self.consent_state != ConsentState.GRANTED:
            raise PermissionError("active sensing requires granted consent")
        if self.consent_expires_at is None or self._now_datetime() >= self.consent_expires_at:
            self.consent_state = ConsentState.EXPIRED
            self._audit("consent", "consent.expired", "system-clock", "validity period elapsed")
            raise PermissionError("consent has expired")

    def create_candidate(
        self, event_type: str, simulation_score: float, location: str
    ) -> DetectionCandidate:
        self._require_active_consent()
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
        actor_credential: str,
        reason: str,
        dispatch_simulator: Optional[Callable[[DetectionCandidate], None]] = None,
    ) -> DetectionCandidate:
        if not self.steward_authorizer.verify(actor_id, actor_credential):
            self._audit(event_id, "approval.denied", actor_id, "invalid Steward credential")
            raise PermissionError("actor is not an authenticated Steward Human")
        candidate = self.candidates[event_id]
        if candidate.approval_state != ApprovalState.PENDING:
            raise RuntimeError("candidate has already been decided")
        state = ApprovalState.APPROVED if approved else ApprovalState.REJECTED
        decided = DetectionCandidate(
            **{**asdict(candidate), "consent_state": candidate.consent_state, "approval_state": state}
        )
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

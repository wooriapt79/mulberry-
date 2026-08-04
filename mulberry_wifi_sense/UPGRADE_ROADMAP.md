# Mulberry WiFi Sense — Evidence-gated Roadmap

**Status:** governed simulation MVP  
**Goal:** one auditable vertical PoC before feature expansion

## Gate 0 — Governance baseline

- Explicit consent states: requested, granted, denied, revoked, expired.
- Candidate events remain pending until a Steward Human decides.
- Simulation scores are never presented as calibrated probabilities.
- No live 119, external message, or medical action.
- Schema and hash-linked audit records cover every transition.

Exit evidence: all safety-workflow tests pass and a sample event can be reconstructed end to end.

## Gate 1 — Single-room real CSI PoC

Fix one hardware combination before making compatibility claims:

- ESP32 CSI sender/receiver nodes.
- Raspberry Pi 5 Edge processor.
- One consented indoor test space.
- Versioned raw/de-identified sample data and reproduction instructions.

Measure presence/movement/sudden-change repeatability, false-positive rate, latency, packet loss, and environmental sensitivity. Existing WiFi AP compatibility, wall penetration, AP count, and ±2 m positioning remain hypotheses until measured.

## Gate 2 — Calibrated safety-event research

- Establish train/validation/test separation and scenario labels.
- Compare rule baseline with 1D-CNN/LSTM only after data quality review.
- Calibrate scores and publish confusion matrix, precision/recall, false alarms per hour, and confidence intervals.
- Keep fall output named `fall_suspected` until field and domain validation support stronger language.

## Gate 3 — Gateway and durable audit

- Validate event schema against Mulberry Event Schema Specification.
- Route candidates through the Mulberry Agent Gateway.
- Persist consent, decision, reason, model/sensor version, and audit-chain head.
- Test offline operation, retries, duplicate events, revocation, and tamper detection.

## Gate 4 — Spatial visualization

Only after Gates 1–3:

- Probability heat maps and uncertainty display.
- BIM/GIS/3D partner integration.
- Offline-capable responder dashboard.
- Positioning targets derived from measured data, not fixed promises.

## Separate high-risk track — personal identification

WhoFi/personal identification requires its own privacy impact assessment, lawful basis, consent model, retention limits, re-identification testing, and security review. Hashing alone is not anonymization. It is not part of the vertical safety PoC.

## Future public-safety integration

The research sequence is:

```text
candidate generation → human review → approved dispatch candidate → audited hand-off
```

Automatic 119 reporting based only on a score threshold is removed. Any future public-safety connection requires separate legal, operational, security, and agency approval and must be introduced through a disabled-by-default adapter.

## Immediate next deliverable

Demonstrate one event from consent to audit using real CSI, and publish a short result table containing hardware versions, room layout, scenario count, false positives, latency, failure cases, and limitations.

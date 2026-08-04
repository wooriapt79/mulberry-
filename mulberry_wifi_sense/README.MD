# Mulberry WiFi Sense
## Privacy-first Spatial Safety Research MVP

Mulberry WiFi Sense explores whether WiFi Channel State Information (CSI) can support privacy-conscious observations of presence, movement, and possible safety events without cameras.

> AI proposes. Humans decide. Every transition is recorded.

## Current truth

This directory is a research simulation, not an emergency-response or medical product. Random CSI and rule thresholds are used in the legacy Python/UI demos. Values such as `0.97` are **uncalibrated simulation scores**, not validated probability, accuracy, or a basis for automatic dispatch.

See [STATUS.md](STATUS.md) for the boundary between implemented, simulated, planned, and paused work.

## Governed event flow

```text
Explicit consent
  → CSI observation
  → candidate safety event
  → sensor/context review
  → Steward Human approval or rejection
  → local dispatch simulation (approved only)
  → hash-linked audit record
```

No live 119 reporting, external messaging, medical diagnosis, or physical dispatch is implemented. The binding research policy is in [governance/HUMAN_APPROVAL_POLICY.md](governance/HUMAN_APPROVAL_POLICY.md).

## v0.2 reference implementation

- `safety_workflow.py`: consent states, candidate events, human decisions, and audit chain.
- `schemas/wifi_sensing_event.schema.json`: candidate-event contract.
- `tests/test_safety_workflow.py`: consent, approval, dispatch-simulation, and duplicate-decision tests.
- `kbin-wifi-sensing-mvp-20260314.py`: legacy consolidated simulation; not the governed production path.
- `demo_ui.html`: concept demo; all positions, identities, and scores are simulated.

Run the safety workflow tests from this directory:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Scope order

The first hardware PoC should fix one test setup:

```text
ESP32 CSI nodes → Raspberry Pi 5 Edge → one indoor room
```

Validate presence, movement, sudden change/stillness, repeatability, false positives, latency, consent enforcement, and audit completeness before attempting positioning, 3D integration, or personal identification.

## Privacy and WhoFi boundary

SHA-256 hashing does not automatically anonymize a stable biometric signature. Personal identification is therefore a separate high-risk research track and is paused in the governed v0.2 path. Prefer anonymous presence, occupancy count, movement state, and same-session tracking.

## Team roles

- KODA: CSI collection, signal processing, edge validation.
- TRANG Manager: scenarios, false-positive analysis, field validation.
- Helix: consent, privacy, safety governance.
- KeBin: event schema, Gateway integration, audit and traceability.
- Luna: human guidance and approved communication interfaces.

## Disclaimer

Do not use this repository to replace emergency responders or medical professionals, claim certified measurements, or trigger live emergency action. Human verification is required.

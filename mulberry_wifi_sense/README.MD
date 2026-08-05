# Mulberry WiFi Sense
## Privacy-first Spatial Safety Research MVP

Mulberry WiFi Sense explores whether WiFi Channel State Information (CSI) can support privacy-conscious observations of presence, movement, and possible safety events without cameras.

> AI proposes. Authenticated humans decide. Every transition is recorded.

## Current truth

This directory is a research simulation, not an emergency-response or medical product. Random CSI and rule thresholds are used in the legacy Python/UI demos. Values such as `0.97` are **uncalibrated simulation scores**, not validated probability, accuracy, or a basis for automatic dispatch.

See [STATUS.md](STATUS.md) for the boundary between implemented, simulated, planned, disabled, and paused work.

## Governed event flow

```text
Time-bounded explicit consent
  → CSI observation
  → candidate safety event
  → sensor/context review
  → authenticated Steward Human approval or rejection
  → local dispatch simulation (approved only)
  → hash-linked audit record
```

No live 119 reporting, external messaging, medical diagnosis, or physical dispatch is implemented. The binding research policy is in [governance/HUMAN_APPROVAL_POLICY.md](governance/HUMAN_APPROVAL_POLICY.md).

## v0.2 reference implementation

- `safety_workflow.py`: time-bounded consent, candidate events, Steward verification, decisions, and audit chain.
- `schemas/wifi_sensing_event.schema.json`: candidate-event contract.
- `tests/test_safety_workflow.py`: consent expiry, approval authentication, dispatch simulation, and decision tests.
- `tests/test_legacy_safety_boundaries.py`: proves WhoFi, legacy APIs, and emergency triggers remain disabled.
- `kbin-wifi-sensing-mvp-20260314.py`: legacy consolidated simulation with high-risk/external paths hard-disabled.
- `demo_ui.html`: concept demo; all positions, identities, and scores are simulated.

Run tests from this directory:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Enforced legacy boundary

The legacy file declares `WHOFI_ENABLED = False` and `LEGACY_EXTERNAL_ACTIONS_ENABLED = False`. While disabled:

- WhoFi enrollment and identification raise `PermissionError` before feature collection or storage.
- All legacy API sends and emergency trigger methods raise `PermissionError`.
- The executable legacy demo performs no sensing, identity, API, or emergency workflow.

Re-enabling these constants is not an approved extension path. A future implementation requires a separate reviewed design and must connect through the governed workflow.

## Scope order

The first hardware PoC should fix one test setup:

```text
ESP32 CSI nodes → Raspberry Pi 5 Edge → one indoor room
```

Validate presence, movement, sudden change/stillness, repeatability, false positives, latency, consent enforcement, and audit completeness before attempting positioning, 3D integration, or personal identification.

## Privacy and WhoFi boundary

SHA-256 hashing does not anonymize a stable biometric signature. Personal identification is a separate high-risk research track and is disabled in v0.2. Prefer anonymous presence, occupancy count, movement state, and same-session tracking.

## Team roles

- KODA: CSI collection, signal processing, edge validation.
- TRANG Manager: scenarios, false-positive analysis, field validation.
- Helix: consent, privacy, safety governance.
- KeBin: event schema, Gateway integration, audit and traceability.
- Luna: human guidance and approved communication interfaces.

## Disclaimer

Do not use this repository to replace emergency responders or medical professionals, claim certified measurements, or trigger live emergency action. Authenticated human verification is required.

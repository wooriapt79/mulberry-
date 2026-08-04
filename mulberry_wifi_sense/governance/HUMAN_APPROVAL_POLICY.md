# Human Approval Policy — Research MVP

## Binding rule

WiFi sensing output is a **candidate safety event**, not a confirmed emergency. No external notification, emergency-service request, medical conclusion, or physical dispatch may occur without a recorded human decision.

## Required flow

1. Confirm active, unexpired consent.
2. Create a candidate event with sensor context and an uncalibrated simulation/model score.
3. Place the event in `pending` state.
4. A designated Steward Human reviews the event and records `approved` or `rejected`, actor, time, and reason.
5. Only an approved event may enter a separate dispatch adapter. This repository contains simulation only and no live adapter.
6. Append every transition to a hash-linked audit record.

## Prohibited in this MVP

- Automatic 119 reporting based on a numeric threshold.
- Presenting a fixed score such as `0.97` as validated accuracy or probability.
- Collecting while consent is denied, revoked, expired, or only requested.
- Treating a SHA-256 biometric hash as anonymization.
- Live personal identification or external messaging.

## Emergency exception

Any future exception must be separately approved through legal, privacy, public-safety, and field-operation review. It is not implemented by this policy.

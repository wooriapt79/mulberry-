# Human Approval Policy — Research MVP

## Binding rule

WiFi sensing output is a **candidate safety event**, not a confirmed emergency. No external notification, emergency-service request, medical conclusion, or physical dispatch may occur without a recorded decision by an authenticated Steward Human.

## Required flow

1. Record explicit consent with `granted_at` and `expires_at`.
2. Re-evaluate consent immediately before candidate creation; the system changes elapsed consent to `expired` and blocks collection.
3. Create a candidate event with sensor context and an uncalibrated simulation/model score.
4. Place the event in `pending` state.
5. Verify the Steward Human against the registered authority source before accepting `approved` or `rejected`.
6. Record actor, time, reason, and decision.
7. Only an approved event may enter a separate dispatch adapter. This repository contains local simulation only and no live adapter.
8. Append every transition, including denied approval attempts and automatic expiry, to a hash-linked audit record.

## Steward authentication boundary

The v0.2 reference uses `StewardAuthorizer` with registered actor IDs and test credentials. Plain actor strings are not sufficient. Production must replace the MVP verifier with Agent Passport or an equivalent signed identity-and-role assertion; credentials must not be committed to the repository.

## Prohibited in this MVP

- Automatic 119 reporting based on a numeric threshold.
- Presenting a fixed score such as `0.97` as validated accuracy or probability.
- Collecting while consent is denied, revoked, expired, or only requested.
- Treating a SHA-256 biometric hash as anonymization.
- Live personal identification, external API transmission, or external messaging.
- Re-enabling legacy emergency, API, or WhoFi paths to bypass this policy.

## Emergency exception

Any future exception must be separately approved through legal, privacy, public-safety, and field-operation review. It is not implemented by this policy.

# Implementation Status

| Capability | Status | Evidence / limitation |
|---|---|---|
| CSI input | Simulation | Random 64-value frames; no hardware capture evidence yet |
| Motion/fall classification | Simulation | Rule thresholds; no calibrated probability or validated accuracy |
| Consent | v0.2 reference implementation | `granted_at` and `expires_at`; automatic pre-candidate expiry blocks sensing |
| Human approval | v0.2 reference implementation | Registered Steward actor plus credential verification; invalid attempts are blocked and audited |
| Audit | v0.2 reference implementation | In-memory hash-linked records; persistence not implemented |
| Dispatch | Simulation only | Callback runs only after authenticated approval; no 119/API/message integration |
| WhoFi identification | Disabled | `WHOFI_ENABLED = False`; enrollment, identification, legacy demo, and external transmission are blocked |
| Legacy external action | Disabled | `LEGACY_EXTERNAL_ACTIONS_ENABLED = False`; API and emergency trigger paths refuse execution |
| Real CSI PoC | Planned | Fix one ESP32 + Raspberry Pi 5 + single-room setup first |

## Security boundary

The current Steward verifier is suitable only for a closed research MVP. Production requires Agent Passport or equivalent signed authentication, role authorization, credential rotation, persistent audit storage, and replay protection.

## Next evidence gate

Collect a small, consented ESP32 CSI dataset in one room and demonstrate one end-to-end event: collection → candidate → authenticated human decision → audit record. Report false positives, latency, sensor failures, and environment changes before expanding scope.

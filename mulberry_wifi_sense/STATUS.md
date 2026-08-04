# Implementation Status

| Capability | Status | Evidence / limitation |
|---|---|---|
| CSI input | Simulation | Random 64-value frames; no hardware capture evidence yet |
| Motion/fall classification | Simulation | Rule thresholds; no calibrated probability or validated accuracy |
| Consent | v0.2 reference implementation | Five explicit states; sensing candidate creation is blocked unless granted |
| Human approval | v0.2 reference implementation | Pending/approved/rejected with actor and reason |
| Audit | v0.2 reference implementation | In-memory hash-linked records; persistence not implemented |
| Dispatch | Simulation only | Callback runs only after approval; no 119/API/message integration |
| WhoFi identification | High-risk research, paused | Hashing does not eliminate biometric or tracking risk |
| Real CSI PoC | Planned | Fix one ESP32 + Raspberry Pi 5 + single-room setup first |

## Next evidence gate

Collect a small, consented ESP32 CSI dataset in one room and demonstrate one end-to-end event: collection → candidate → human decision → audit record. Report false positives, latency, sensor failures, and environment changes before expanding scope.

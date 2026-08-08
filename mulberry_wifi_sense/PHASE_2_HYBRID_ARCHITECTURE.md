# Phase 2: Hybrid Distributed Architecture
**Approved by CEO re.eul — 2026-08-08**

---

## Overview

Phase 2 evolves the single-room PoC into a **distributed, hybrid architecture** that leverages existing home WiFi infrastructure while maintaining Mulberry's governance principles.

**Core Principle**: *Lightweight local sensing + centralized human approval*

---

## Architecture

### Previous (Phase 1)
```
[ESP32 nodes] → [Raspberry Pi 5 Edge] → [Central Steward]
```

### Phase 2: Hybrid Distributed (CEO's Vision)
```
[Home WiFi Router + ESP32]  ← Already exists in most homes
       ↓ (Local CSI collection)
[Lightweight Edge / Cloud Sync]
       ↓ (Candidate event)
[Central Steward Server]  ← Human approval stays here
       ↓ (Authenticated decision)
[Audit & Record]
```

---

## Deployment Model

### Option A: Home WiFi Router + ESP32
- **Sensors**: Multi-room ESP32 nodes in each household
- **Router**: Existing home WiFi (any OpenWrt, Broadcom, or Qualcomm-based)
- **CSI Source**: Native WiFi chipset (no firmware mod required for most routers)
- **Edge Processing**: Optional lightweight Pi Zero or relay to cloud
- **Cost per home**: ~$20-50 (ESP32s only; router already owned)

### Option B: Pure ESP32 + WiFi
- **Sensors**: ESP32 collect + forward CSI
- **Transmission**: Direct to gateway or cloud via existing home WiFi
- **Minimal Edge**: Cloud processes, returns candidate
- **Cost per home**: ~$15-30

---

## ESP32 Independence: What's Possible, What Isn't

### ✅ What ESP32 Can Do Alone
- CSI data collection
- Local signal processing
- Rule-based candidate generation
- Offline storage (SPIFFS)
- Network sync when available

### ❌ What ESP32 Cannot Do Alone
- **Authenticated human approval** ← Must stay centralized
- Tamper-proof audit chain
- Multi-party authorization
- Revocation enforcement

### ✅ Hybrid Advantage
```
[ESP32: Propose locally]
        ↓
[Cloud/Steward: Decide centrally]
        ↓
[Both audit the decision]
```

**Preserves governance**: "AI proposes. Authenticated humans decide. Every transition recorded."

---

## Offline & Resilience

### Scenario: Network Loss
```
[ESP32 continues CSI collection]
    ↓ (Local storage)
[Stores events in SPIFFS]
    ↓ (Network restored)
[Syncs to cloud]
    ↓
[Steward reviews & approves]
```

**Benefit**: Households remain protected even during internet outages.

---

## Deployment Sequence for Phase 2

| Week | Milestone | Owner |
|------|-----------|-------|
| 1-2 | Validate WiFi router CSI extraction (3 model families) | KODA |
| 3-4 | Build hybrid PoC: Home router + 3x ESP32 + cloud sync | KODA + KeBin |
| 5-6 | Real CSI dataset collection (one test home, 2 weeks) | TRANG Manager |
| 7-8 | End-to-end: collection → candidate → Steward approval → audit | TRANG + Helix |
| 9-10 | Measure: false positives, latency, sensor failure, env. changes | TRANG Manager |
| 11-12 | Pilot: 5 homes in Mulberry service area | TRANG Manager |

---

## Data Governance

### Consent & Approval (Unchanged)
- Time-bounded explicit consent (via Steward UI)
- Candidate events await human review before any action
- Revocation blocks further sensing until renewed consent

### New: Offline Audit Trail
- ESP32 logs local decisions to SPIFFS
- Cloud receives sync + validates chain when online
- If offline decision was made: Steward reviews + signs audit record retroactively

---

## Integration with Mulberry Ecosystem

### Event Schema
- Existing `wifi_sensing_event.schema.json` used as-is
- Add optional `offline_collected_at` timestamp for offline events

### Gateway
- Route candidates through existing Mulberry Agent Gateway
- Steward actor validates offline events before approval

### Luna Integration
- Luna UI displays pending candidates from all homes
- Luna routes approved decisions back to ESP32 (via push or polling)

---

## Security & Privacy

### Trusted Elements
- Steward credential verification (Phase 3 upgrade: Agent Passport)
- Audit chain hash-linked (Phase 3 upgrade: durable storage)

### WiFi CSI Privacy
- SHA-256 hashing of MAC addresses (not anonymization, but obfuscation)
- No personal identification in Phase 2
- WhoFi remains disabled

### Offline Risk
- ESP32 SPIFFS is local only; no cloud backup of raw data until approved
- If device stolen: no personally identifiable data at rest

---

## Comparison: Phase 1 vs Phase 2

| Aspect | Phase 1 (Single Room) | Phase 2 (Hybrid Distributed) |
|--------|----------------------|------------------------------|
| **Scope** | 1 room, 1 Rpi5 | Multiple homes |
| **Hardware** | ESP32 + Rpi5 | ESP32 + existing router |
| **Offline** | No | Yes (SPIFFS) |
| **Steward** | Central | Central (unchanged) |
| **Deployment Cost** | ~$200 | ~$30 per home |
| **Scalability** | Limited | **High** |
| **Data Source** | Simulation → Real CSI | Real CSI from day 1 |

---

## Mulberry Strategic Fit

✅ **Leverage existing infrastructure** — WiFi routers already in homes  
✅ **Low cost barrier** — ESP32 affordable at scale  
✅ **Privacy by design** — Processing local before central decision  
✅ **Governance preserved** — Steward approval still required  
✅ **Service area ready** — Deploy to Mulberry's food-desert communities  
✅ **Offline resilient** — Works even during ISP outage  

---

## Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| **Router CSI varies** | Validate 5+ models before broad pilot |
| **Offline data accumulation** | SPIFFS size limit (4MB); archive strategy |
| **Consent across homes** | Single sign-on + legal agreement (Phase 2) |
| **WiFi interference** | Measure false-positive rate in real homes |

---

## Next Gate Entry Criteria

**Gate 1 (Phase 2 completion)**:
- ✅ Real CSI from 3+ router models + ESP32 hybrid
- ✅ One end-to-end event: offline collect → cloud sync → Steward approve → audit sign
- ✅ Latency, false positives, sensor failures, environment changes measured
- ✅ 5-home pilot completed in Mulberry service area
- ✅ Offline sync and approval workflow tested

**Then**: Gate 2 (calibration) with real data.

---

**Document Version**: 1.0  
**Approved**: CEO re.eul, 2026-08-08  
**Next Review**: End of Phase 2 pilot  

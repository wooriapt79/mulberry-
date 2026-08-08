# Phase 2: Privacy-First MAC Address Strategy
**Approved by CEO re.eul — 2026-08-08**

---

## Problem Statement

WiFi CSI collection in a home environment captures signals from **every connected device**:

```
[Home WiFi Signals]
  ├─ User's smartphone (AA:BB:CC:DD:EE:FF)
  ├─ Family member's tablet (11:22:33:44:55:66)
  ├─ SmartTV (FF:EE:DD:CC:BB:AA)
  ├─ IoT cameras/thermostats (various)
  └─ ESP32 sensor (77:66:55:44:33:22)
```

**Question**: How do we know whose movement signal is whose? And how do we prevent re-identification?

---

## Current PHASE_2 Approach: Insufficient

### What We Do Now
- SHA-256 hash MAC addresses
- Extract CSI patterns
- Claim "No personal identification in Phase 2"

### The Gap
- Hashing is **obfuscation, not anonymization**
- A stable hashed MAC remains a stable biometric identifier
- Multiple signals from same MAC → same person (linkable)
- No device registration → no consent clarity

---

## Proposed Solution: Device Registration + Filtering

### Step 1: Home Setup — Device Registration

When a household enrolls in WiFi Sense pilot:

```
[User onboarding]
    ↓
List all WiFi-connected devices:
    ├─ Smartphone (Manufacturer: Apple, Model: iPhone 14)
    │   └─ MAC hash: a3f8d2e1c9... [User consents to monitor ✓]
    ├─ Tablet (Manufacturer: Samsung, Model: Tab S7)
    │   └─ MAC hash: b4g7e2d9k0... [User consents to monitor ✓]
    ├─ SmartTV (Manufacturer: LG, Model: OLED55)
    │   └─ MAC hash: c5h6f1j8m2... [EXCLUDED — static device]
    ├─ Thermostat (Manufacturer: Nest)
    │   └─ MAC hash: d7i4a3b5n1... [EXCLUDED — IoT device]
    └─ ESP32 Sensor
        └─ MAC hash: e2j9c4k1p6... [SELF — sensor itself]
    ↓
[Steward reviews & approves]
    ↓
[Device whitelist created]
```

---

### Step 2: CSI Analysis — Device Type Inference

When ESP32 and router collect CSI, automatically classify signals:

```
[Incoming CSI Signal]
    ↓
MAC Hash = a3f8d2e1c9... (User's iPhone)
    ↓
Feature extraction:
    ├─ RSSI stability: Varies (3-8 dB swings)
    ├─ Frequency response: Broadband (smartphone antenna)
    ├─ Movement correlation: High (user moves, signal changes)
    ├─ Activity pattern: Temporal (morning, evening, variable)
    └─ Signal periodicity: Non-periodic
    ↓
Classification: "MOBILE_DEVICE — likely person"
    ↓
[Proceed to movement analysis]
```

**vs.**

```
[Incoming CSI Signal]
MAC Hash = c5h6f1j8m2... (SmartTV)
    ↓
Feature extraction:
    ├─ RSSI stability: Very stable (±0.5 dB)
    ├─ Frequency response: Narrow (limited antenna)
    ├─ Movement correlation: None (stationary)
    ├─ Activity pattern: Nocturnal (evening only)
    └─ Signal periodicity: High (video refresh)
    ↓
Classification: "STATIC_DEVICE — exclude"
    ↓
[Ignore from movement detection]
```

---

### Step 3: Filtering Rules

**Automatically excluded signals**:
1. **Router self-signals** — CSI of the router itself
2. **Static devices** — SmartTV, thermostats, speakers (stable CSI)
3. **IoT appliances** — Security cameras, light bulbs (no movement correlation)
4. **Unregistered MACs** — Not in household device list

**Remaining signals**:
- Smartphones
- Tablets
- Laptops (mobile devices only; docked excluded)
- Registered mobile devices with user consent

---

## MAC Hashing & Consent Model

### Non-Anonymization Disclaimer

```markdown
**Important**: Hashing a MAC address does not anonymize it.

- Same hashed MAC = Same device
- Linkable across sessions
- Can be re-identified if additional context available

**This is acceptable because**:
1. MAC is hashed (not plaintext)
2. Device type is inferred (not personal ID)
3. Movement is de-correlated from identity
4. Steward approval gates all actions
5. No live-on external messaging
```

### Consent Scope

Each registered device receives a consent **scope**:

```json
{
  "device_id": "a3f8d2e1c9...",
  "type": "MOBILE_DEVICE",
  "device_class": "smartphone",
  "consent_status": "granted",
  "consent_scope": {
    "movement_detection": true,
    "location_estimation": true,
    "fall_detection": true,
    "re_identification": false
  },
  "expires_at": "2026-09-08T00:00:00Z",
  "approved_by_steward": "helix@mulberry.local"
}
```

---

## Multi-Person Household: Disambiguation

### Scenario: Two people in same room

```
[CSI from two phones simultaneously]
    ├─ Phone A (Mom): AA:BB:CC:DD:EE:FF
    └─ Phone B (Dad): 11:22:33:44:55:66
    ↓
[Spatial CSI analysis]
    ├─ Phone A: Moving (sofa → kitchen)
    ├─ Phone B: Stationary (office)
    ↓
[Both movements detected, both linked to their registered devices]
    ↓
[Steward can see]:
    "Movement in living room" (consented users' devices only)
    "No personal IDs — device classes and locations only"
```

**Key point**: We know a movement happened and from which registered device. We don't require knowing *who* that device belongs to to trigger safety assessment.

---

## Offline Device Handling

### Unknown MAC in CSI

If ESP32 detects a MAC not in device registry:

```
[Unknown MAC detected]
    ↓
Classification attempt:
    ├─ If features match "MOBILE_DEVICE" → Log, don't process
    ├─ If features match "STATIC_DEVICE" → Ignore
    └─ If ambiguous → Log, await Steward review
    ↓
[Local storage]
    Device registry syncs when online
```

**No movement credit given** to unregistered MACs.

---

## Data Storage & Retention

### Stored Locally (ESP32 SPIFFS)
```
{
  "timestamp": "2026-08-08T14:23:45Z",
  "device_hash": "a3f8d2e1c9...",
  "signal_type": "MOBILE_DEVICE",
  "movement_detected": true,
  "location_zone": "zone_2_bedroom",
  "csi_features": { /* compressed */ },
  "steward_approved": null  // Pending cloud approval
}
```

### Sent to Cloud Only After Approval
```
{
  "timestamp": "2026-08-08T14:23:45Z",
  "device_hash": "a3f8d2e1c9...",
  "movement_detected": true,
  "location_zone": "zone_2_bedroom",
  "steward_decision": "MOVEMENT_DETECTED",
  "steward_timestamp": "2026-08-08T14:24:10Z",
  "steward_actor": "helix@mulberry.local",
  "audit_hash": "sha256(...)"
}
```

**Raw CSI never stored indefinitely** — only movement inference + audit trail.

---

## Comparison: With vs Without MAC Strategy

### Without MAC Strategy (Risk)
```
[All CSI signals treated equally]
    ↓
[Cannot distinguish person from appliance]
    ↓
[Might trigger movement alarm from SmartTV]
    ↓
[False positive risk]
```

### With MAC Strategy (Safer)
```
[Registered mobile devices only]
    ↓
[SmartTV & static devices filtered]
    ↓
[Movement only from consented phones/tablets]
    ↓
[False positive minimized]
```

---

## WhoFi & Personal Identification: Explicitly Disabled

### Phase 2 Boundary
```
✅ Device registration (MAC hash + consent)
✅ Device type inference (mobile vs static)
✅ Movement detection per device
❌ Personal name/ID linking
❌ Behavioral fingerprinting
❌ Cross-home linking
```

**WhoFi flag remains**: `WHOFI_ENABLED = False`

Any future personal identification requires:
- Separate privacy impact assessment
- New consent model
- Legal review
- User opt-in (not default)

---

## Steward Approval Gate

Before any safety candidate is approved, Steward sees:

```
Candidate Event:
├─ Time: 2026-08-08 14:23:45
├─ Location: Bedroom (zone 2)
├─ Signal sources: Device hash a3f8... (registered)
├─ Classification: MOVEMENT_DETECTED
├─ Confidence: 87%
├─ Device consent: ✓ (granted, not expired)
├─ Risk level: Low (slow movement, morning)
└─ Recommended action: Log only

[Steward Reviews]
    ↓
[Approves movement detection]
    ↓
[Decision logged with MAC hash, not name]
    ↓
[Audit trail sealed]
```

---

## Phase 3 Upgrade: Persistent Device Registry

Phase 2.5 enhancement (planned):

```
[Cloud-based device registry]
├─ User account
├─ Household ID
├─ Registered devices
│   ├─ Device MAC hash
│   ├─ Type (inferred + user-confirmed)
│   ├─ Consent status
│   ├─ Granted scopes
│   └─ Revocation history
└─ Audit log of all registrations
```

---

## Summary: Privacy by Design

| Layer | Control |
|-------|---------|
| **Collection** | Only registered mobile devices |
| **Processing** | Device type filtering (exclude static) |
| **Storage** | Hashed MAC (not plaintext), movement only |
| **Approval** | Steward gate (no automatic action) |
| **Identity** | None (device class, not person name) |
| **Retention** | Audit trail only, no raw CSI |

---

## Implementation Checklist for Phase 2

- [ ] Device registration UI (Steward interface)
- [ ] MAC hash + consent model in schema
- [ ] Device type classification algorithm
- [ ] Offline filtering logic in ESP32 firmware
- [ ] Unregistered MAC logging
- [ ] Steward approval display (device hash only)
- [ ] Audit trail records (hashed MAC, no names)
- [ ] Documentation for users (consent form)
- [ ] Privacy impact assessment (Phase 2.5)

---

**Document Version**: 1.0  
**Approved**: CEO re.eul, 2026-08-08  
**Related**: PHASE_2_HYBRID_ARCHITECTURE.md, STATUS.md  
**Next Review**: End of Phase 2 device registration pilot  

# Mulberry System Mapping Appendix  
## Policy-to-System Enforcement Mapping

**Mulberry Project**  
CEO re.eul · CSA Kbin · CTO Koda · PM · Chief of Staff Malu  

> Architecture enforces policy.

---

## 0. Purpose

This document translates Mulberry’s **legal, policy, and governance principles**
into **explicit system-level constraints**.

It is written for:
- CTO / Engineering
- CSA / Governance
- External auditors (legal, public sector, VC DD)

This is **not** a conceptual document.  
This document defines **what the system must enforce by design**.

---

## 1. AI Agent Classification (Non-Negotiable)

### Policy
AI Agents are **not legal or economic actors**.

### System Enforcement
- No wallet
- No private key
- No asset ownership
- No transaction execution authority

### Implementation Rule
AI Agents may:
- Analyze
- Recommend
- Simulate

AI Agents may **never**:
- Execute payments
- Hold balances
- Act without human approval

> Agents are classified as **Operational Assistants**, not actors.

---

## 2. Human Authority Layer

### Policy
All legal and financial responsibility resides with humans.

### System Enforcement
- Mandatory human approval for any payment
- Explicit confirmation UI
- Approval identity logged and immutable

### Forbidden Pattern
❌ Agent-triggered execution  
❌ Silent or implicit approval flows

---

## 3. AP2 Smart Mandate Layer (Legal Firewall)

### Policy
AP2 is a **legal control interface**, not a convenience feature.

### Mandatory Constraints
- Hard transaction ceilings
- Time-bound mandates
- Scope-limited permissions
- Immutable audit logs

### System Failure Condition
If a transaction bypasses AP2 constraints,  
→ **The system is considered non-compliant.**

---

## 4. Recommendation vs Execution Separation

### Architecture Rule

| Layer | Capability |
|-----|-----------|
| AI Agent | Recommendation only |
| System | Validation & logging |
| Human | Approval & execution |

Any design merging these layers is **architecturally invalid**.

---

## 5. Dashboard & Metrics Exposure Rules

### Policy Goal
Prevent investment misinterpretation and regulatory risk.

### Allowed
- Aggregate activity metrics
- System efficiency indicators
- Social impact data

### Prohibited
- Individual ROI
- Profit projections
- Yield simulations
- Investment language

> Activity ≠ Investment performance

---

## 6. Governance & Kill-Switch Controls

### Required Controls
- CSA-level emergency disable
- Role-based access control (RBAC)
- Policy registry with versioning
- Immutable audit trail

No production deployment is allowed without these controls.

---

## 7. Policy as Code (CI/CD)

### Mandatory
- Policy rules encoded as tests
- Build-time compliance checks
- Deployment blocked on violations

### Principle
Policy violations are **build failures**, not runtime issues.

---

## 8. Explicit Failure Scenarios (Red Lines)

The system must prevent:

- Agent-initiated payments
- Sponsor commanding an agent
- Agent-generated profit claims
- Marketing implying guaranteed returns

These are **system-level breaches**, not user errors.

---

## 9. Final Principle

Mulberry does not attempt to correct behavior.  
Mulberry **removes the possibility of violation**.

> Good intentions are insufficient.  
> Correct architecture is mandatory.

---

## Signed

**CEO re.eul**  
**CSA Kbin**  
**CTO Koda**
**Malu**
**PM**

Mulberry Project

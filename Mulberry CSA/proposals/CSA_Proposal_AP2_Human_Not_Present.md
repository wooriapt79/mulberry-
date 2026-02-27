📄 Mulberry CSA Proposal
Human-Not-Present Agent Commerce using AP2 Intent Mandates

Document Type: CSA Proposal
Project: Mulberry Project
Related Standard: AP2 (Agent Payments Protocol)
Reference: AP2 Issue #78 – IntentMandate for Human-Not-Present Flows
Authoring Role: CSA Kbin
Status: Draft (Public Discussion Ready)

1. Background

Agent-based commerce is transitioning from human-present interactions
to autonomous, condition-driven execution.

Current AP2 implementations primarily assume:

A human is present

Explicit confirmation occurs at checkout

However, real-world deployment (food access, local supply automation, rural logistics) requires:

Agents to act and transact when humans are not present,
under clearly defined, auditable mandates.

Mulberry operates precisely in this domain.

2. Problem Statement
Limitations of Current AP2 Flow

Human-present checkout is required

No standardized way to:

Pre-authorize spending conditions

Delegate bounded financial autonomy to agents

Prove intent when the user is offline or absent

Resulting Gap

This blocks:

Autonomous replenishment

Cooperative / pooled purchasing

Edge-AI-driven commerce in low-connectivity environments

3. Mulberry Use Case (Real-World)

Mulberry deploys Edge AI terminals (Raspberry Pi + lightweight LLM) in food-desert contexts.

Typical scenario:

User defines food preferences, limits, and schedules

Agent monitors availability, price, logistics

User is not present at transaction time

Agent must:

Decide

Order

Pay

Log evidence

This is Human-Not-Present Commerce by design, not exception.

4. Proposed Extension: Intent Mandate Layer

Mulberry proposes formalizing an Intent Mandate Layer on top of AP2.

4.1 Intent Mandate Definition

A cryptographically verifiable declaration that specifies:

Authorized agent identity

Spending limits

Conditional triggers

Temporal scope

Revocation rules

“If conditions X are met, agent Y is authorized to act on my behalf.”

4.2 Human-Not-Present Flow (Conceptual)

Human defines Intent Mandate (once)

Mandate is signed & stored

Agent operates autonomously

Transaction executed under mandate

Full audit trail preserved

5. Security & Accountability
Key Principles

Bounded autonomy (no open-ended authority)

Cryptographic traceability

Revocable at any time

Auditable by third parties

Suggested Mechanisms

Session-scoped keys

Verifiable Credentials (VC)

Immutable transaction logs

Post-hoc human review

6. Alignment with AP2 Vision

This proposal:

Does NOT bypass user consent

Does NOT weaken security

Extends AP2 toward true agent autonomy

It aligns with:

AP2’s intent-centric philosophy

Interoperable agent commerce

Regulator-friendly auditability

7. Why Mulberry Contributes This

Mulberry is not theorizing autonomy.
We deploy it.

Our context requires:

Low bandwidth

Edge execution

Offline tolerance

Public trust

Therefore, our contribution is grounded in operational reality, not abstraction.

8. Next Steps (Open)

Community discussion on mandate schema

Reference implementation (PoC)

Integration with AP2 working groups

Documentation-first standardization

Mulberry is open to collaboration.

9. Closing

Autonomous commerce will not emerge from convenience use cases alone.

It will emerge from necessity.

Food access, rural supply chains, and edge-AI deployments demand
Human-Not-Present agent systems with trustable intent delegation.

Mulberry is building for that future—now.

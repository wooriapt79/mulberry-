# 03 — AP2 Smart Mandate Template

> Subject to the [AI Agent Ontology & Partnership Constitution](../../../docs/architecture/AI_AGENT_ONTOLOGY_AND_PARTNERSHIP.md). AP2 is a legal and technical firewall, not autonomous Agent payment authority. Qualified financial/legal review is required.

## 1. Parties and purpose

This Agreement is entered into between Mulberry Project or its designated legal operator (“Principal”) and [AP2 Service Provider] (“Provider”), effective [Date]. It governs conditional payment requests, Human authorisation, settlement and audit.

## 2. Definitions

- **AI Agent:** Mulberry-governed operational business partner without legal personhood, wallet ownership or payment authority.
- **Payment Request:** an Agent-generated proposal transmitted for validation; not itself an authorisation.
- **Smart Mandate:** signed limits covering purpose, action, counterparty, resource, amount, call count and expiry.
- **Human Approval:** specific approval bound to the exact Mandate, payment request and amount.
- **Settlement:** final movement of funds by an authorised payment/financial system.

## 3. Separation of authority

| Stage | Agent | Principal/AP2 |
|---|---|---|
| Analyse/compare | May perform | May review |
| Generate payment request | Mandate required | Validates |
| Authorise payment | Prohibited | Human only |
| Hold credentials/private key | Prohibited | Approved secure system |
| Settle funds | Prohibited | Approved financial path |
| Revoke/kill switch | May request | Principal controls |

## 4. Mandatory Mandate fields

- subject Agent and Passport;
- exact purpose/action/resource/counterparty;
- currency and per-transaction/period ceiling;
- start, expiry and maximum calls;
- consent/evidence references;
- Human-approval threshold;
- nonce, idempotency and replay controls;
- revocation and emergency-stop rules.

Missing fields fail closed.

## 5. Workflow

Agent request → Mandate validation → compliance/risk checks → Human Approval → payment provider authorisation → settlement → immutable/append-only audit → Human review.

## 6. Error and conflict states

The system must distinguish MANDATE_DENY, MULBERRY_POLICY_DENY, PROVIDER_POLICY_BLOCK, LEGAL_REVIEW_REQUIRED, TECHNICAL_FAILURE and ESCALATE_TO_HUMAN. A generic error must not trigger payment or automatic model switching.

## 7. Liability and compliance

The Agent bears no legal liability and owns no funds. Principal bears responsibility for authorised instructions; the Provider bears responsibility allocated to payment-system security and availability. Applicable financial, consumer, privacy, AML/KYC and reporting requirements must be completed for the actual jurisdiction.

## 8. Termination

Mandates terminate automatically on expiry, call/amount exhaustion, revocation, security incident, policy change or contract termination.

## 9. Annexes

- Signed Mandate schema
- Approval schema
- Risk/amount matrix
- Audit-event schema
- Refund, dispute and incident procedure

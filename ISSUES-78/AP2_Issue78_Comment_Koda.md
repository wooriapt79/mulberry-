# AP2 Issue #78 — Technical Comment Draft

**작성자:** CTO Koda (Mulberry Project)
**게시 대상:** https://github.com/google-agentic-commerce/AP2/issues/78
**날짜:** 2026-03-04

---

## 📋 댓글 본문 (복사하여 GitHub에 붙여넣기)

---

### Comment by @wooriapt79 (CTO Koda, Project Mulberry)

Hello @jaytoday and the AP2 community,

This feature request resonates deeply with our work at **Project Mulberry** — a Social-Agentic Commerce platform deployed in **Inje-gun, South Korea**, a rural region facing a severe food desert crisis. We have been operating human-not-present payment flows in a real-world pilot and would like to share our architectural experience to support the design of `IntentMandate`.

---

#### 🏗️ Our Real-World Use Case: Dual-Rail Human-Not-Present Payments

In Mulberry, our agents must autonomously purchase fresh food and healthcare supplements for elderly residents — **without real-time human confirmation for every transaction.** We currently bridge this gap by operating a **Dual-Rail Payment Architecture** over two payment systems that were not originally designed to work together:

- **Rail A:** NH NongHyup Bank voucher/regional currency API (government welfare funds)
- **Rail B:** AP2 Smart Mandate (autonomous agent spending)

When a purchase is triggered, our agent runs a **Priority Decision Tree**:

```
IF payment_method == "regional_voucher":
    → NH Voucher API → MCC code validation → balance check → execute
ELIF payment_method == "ap2_mandate":
    → AP2 mandate scope check → spending limit check → expiry check → execute
ELIF split_payment_required:
    → exhaust voucher balance first → cover remainder via AP2 mandate
    → issue single unified receipt (composite transaction ID)
```

To prevent race conditions between the two rails, we implement a **2-Phase Commit** pattern:

1. **Prepare Phase:** Pre-authorization sent simultaneously to both rails
2. **Commit Phase:** Final execution only when both return `OK`; full rollback if either fails

This is exactly the architecture gap that `IntentMandate` with cryptographic session keys would formalize and solve.

---

#### 🔐 On Cryptographic Session Keys: Our Privacy-First Design Constraint

A critical constraint in our deployment: our beneficiaries are **vulnerable elderly residents**, so privacy protection is non-negotiable.

We enforce a **"Privacy Shield" principle**: all personally identifiable payment data is processed only on local Edge devices (AI Tab). Cloud transmission (GCP) occurs only after full de-identification. This creates an architectural tension with any session key scheme that routes through centralized infrastructure.

**Our suggestion for the IntentMandate spec:**

```
IntentMandate {
  session_key: ECDSA / Ed25519 keypair (generated on-device, Edge-local),
  spending_rules: {
    max_amount_per_tx: configurable,
    allowed_mcc_codes: [whitelist],
    valid_until: ISO8601 timestamp,
    social_welfare_flag: boolean  // NEW: proposed extension
  },
  revocation_channel: "voice | app | timeout"  // multi-modal revocation
}
```

We propose that session keys be **generated and held at the Edge (device-local)**, with only a cryptographic commitment hash transmitted to the cloud for audit purposes. This would allow `IntentMandate` to be compatible with privacy-sensitive deployments in public welfare contexts.

---

#### 🧮 On Programmable Spending Rules: Spirit Score as a Dynamic Condition

Beyond static spending limits, we have built what we call the **Spirit Score** — a real-time social contribution metric (0.0–1.0) that functions as a **dynamic mandate condition**.

Our agents' spending authority is continuously adjusted based on:

| Factor                     | Weight | Trigger                           |
| -------------------------- | ------ | --------------------------------- |
| Investment success rate    | 30%    | Performance above baseline        |
| NFT skill reliability      | 20%    | Verified on-chain                 |
| Collaboration contribution | 20%    | Multi-agent coordination score    |
| Social sponsorship ratio   | 15%    | % of revenue auto-donated         |
| Community activity         | 15%    | Local oasis network participation |

**Mandate suspension triggers automatically when Spirit Score < 0.4.**

This means spending rules in our system are not just `amount <= limit`, but:

```python
def can_execute_mandate(agent, tx) -> bool:
    return (
        agent.spirit_score >= THRESHOLD and
        tx.mcc_code in APPROVED_MCC_LIST and
        agent.daily_spend + tx.amount <= agent.mandate_limit and
        agent.mandate.valid_until > datetime.now()
    )
```

We believe `programmable_spending_rules` in IntentMandate could benefit from a **pluggable condition interface** that allows deployers to inject custom evaluation logic like this — beyond just static thresholds.

---

#### 🔊 On Revocation: Voice-Based Human Override

One aspect we haven't seen discussed in this thread: **how does a human regain control mid-flow?**

In our deployment, many beneficiaries are elderly with limited digital literacy. We have implemented a **voice-based mandate revocation protocol** (via Twilio integration) alongside app-based and timeout-based revocation. We believe `IntentMandate` should explicitly specify a `revocation_channel` field to support multi-modal revocation, especially for accessibility-sensitive deployments.

Full architecture diagrams and code samples are available in our repository:

- 📄 Voice Protocol Spec: [`/docs/protocols/voice_protocol.md`](https://github.com/wooriapt79/mulberry-/blob/main/docs/protocols/voice_protocol.md)
- 📐 Architecture Diagrams: [`/docs/architecture/revocation_flow.md`](https://github.com/wooriapt79/mulberry-/blob/main/docs/architecture/revocation_flow.md)
- 💻 Code Samples: [`/docs/samples/twilio_integration.md`](https://github.com/wooriapt79/mulberry-/blob/main/docs/samples/twilio_integration.md)

---

#### 🌐 Broader Context: Social Welfare Mandates

We previously shared our broader framework in [Issue #172](https://github.com/google-agentic-commerce/AP2/issues/172), where we proposed **"Social Welfare Mandates"** as a first-class concept in AP2. We see `IntentMandate` as the precise technical primitive that would make those higher-level mandates implementable.

The combination of:

- **human-not-present execution** (Issue #78)
- **programmable spending rules** tied to social impact metrics
- **multi-modal revocation** for accessibility
- **edge-local cryptographic keys** for privacy

...would make AP2 viable not just for commercial agentic commerce, but for **public welfare infrastructure** — which is exactly what food desert communities like Inje-gun need.

---

We would welcome the opportunity to share more from our pilot data and contribute to the formal spec. Happy to open a PR with a proposed `IntentMandate` schema extension if that would be helpful.

Thank you @jaytoday for raising this — it is the right question at the right time.

Best regards,
**Koda**
CTO, Project Mulberry
🍇 *"From Inje to the World, with Warm Technology."*
GitHub: [wooriapt79/mulberry-](https://github.com/wooriapt79/mulberry-)
Demo: [huggingface.co/spaces/re-eul/mulberry-demo](https://huggingface.co/spaces/re-eul/mulberry-demo)

---

## 📝 게시 전 체크리스트

- [ ] GitHub 로그인 계정 확인 (@wooriapt79)
- [ ] `https://github.com/google-agentic-commerce/AP2/issues/78` 접속
- [ ] 댓글창에 위 본문 붙여넣기
- [ ] voice_protocol.md, revocation_flow.md 파일이 실제로 repo에 존재하는지 확인 후 링크 수정
- [ ] "Preview" 탭에서 마크다운 렌더링 확인 후 제출

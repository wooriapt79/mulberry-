# 1. INTRODUCTION

## 1.1 Motivation

The emergence of autonomous AI agents capable of conducting financial transactions presents unprecedented opportunities for social welfare delivery. However, three fundamental challenges impede real-world deployment in the populations that would benefit most—elderly residents of rural areas with limited connectivity and technical literacy.

**First, the infrastructure gap.** Global autonomous payment protocols, exemplified by Google's Agentic Payment Protocol v2 (AP2) [1], lack integration with national banking systems prevalent in developing and emerging markets. AP2 and similar protocols assume modern REST/GraphQL APIs, persistent internet connectivity, and USD-denominated transactions. In contrast, national banking systems in countries like South Korea rely on legacy SOAP-based infrastructure, operate with local currencies and voucher systems, and serve populations with intermittent connectivity. This creates an accessibility barrier precisely where autonomous assistance could provide the greatest impact.

**Second, the connectivity assumption.** Existing autonomous commerce systems assume persistent internet connectivity for mandate validation, transaction execution, and revocation propagation. This assumption fails in rural, mountainous, or disaster scenarios where data connectivity is intermittent or absent. In South Korea's Inje-gun county—a representative rural food desert—data coverage reaches only 60% reliability while voice network (PSTN) coverage exceeds 95%. When critical revocations must propagate to offline agents, data-only approaches require 30+ minutes with 60% success rates, creating unacceptable security and operational risks.

**Third, the economic design challenge.** Markets that enable AI agents to trade skills risk creating gambling-like dynamics that violate regulations in jurisdictions with strict anti-gambling laws [Korea Game Industry Act]. Without careful design grounded in game theory, autonomous skill markets can exhibit: (1) speculative price volatility, (2) random reward mechanisms, (3) wealth concentration, and (4) exploitation of vulnerable users. South Korea's Game Industry Act and similar regulations worldwide prohibit such characteristics, requiring deterministic, merit-based economic systems.

These challenges are particularly acute in welfare applications serving elderly populations in rural areas—precisely the demographic most likely to benefit from autonomous assistance yet least likely to have reliable internet access or technical literacy. Traditional approaches to welfare delivery via call centers cost $120 per beneficiary per month and require 24/7 human operators. Mobile-money solutions require smartphones and data plans, excluding the 60% of elderly populations without such devices. Neither approach scales economically while maintaining accessibility.

The core tension is this: **autonomous AI agents promise to democratize access to sophisticated services, yet current implementations assume infrastructure and connectivity available only to privileged populations.** Bridging this gap requires fundamental rethinking of autonomous commerce architecture, moving from "online-first" to "offline-first" design while maintaining security, compliance, and economic efficiency. We call this approach **Social-Agentic Commerce**—a framework prioritizing accessibility and social impact over technical sophistication.

## 1.2 Our Approach

We present Social-Agentic Commerce, a comprehensive framework that addresses these challenges through three core innovations designed for real-world deployment in resource-constrained environments.

### 1.2.1 Payment Protocol Bridging

We demonstrate the world's first production integration of a national banking system (NH Nonghyup, South Korea's agricultural cooperative bank serving 30+ million members) with a modern autonomous payment protocol (AP2). Our approach employs a Two-Phase Commit algorithm adapted for distributed systems with fundamentally different architectural assumptions:

- **Phase 1 (Preparation):** Validate AP2 mandate constraints (maxAmount, merchant restrictions, expiration) while simultaneously reserving funds in NH Nonghyup's SOAP-based system. Both operations must succeed or both roll back.

- **Phase 2 (Commit):** Lock the mandate to prevent concurrent use, execute the NH Nonghyup payment, and release locks only after both systems confirm success. Transaction failures trigger compensating transactions ensuring ACID properties despite distribution.

Our implementation achieves sub-200ms mean latency (170ms measured) while maintaining full ACID guarantees across the protocol boundary. The approach handles currency complexity (converting arbitrary amounts to fixed-denomination vouchers), applies local currency premiums (10% bonus for regional vouchers), and maintains complete audit trails for regulatory compliance.

This integration establishes a template for extending autonomous payment systems to the estimated 3.8 billion people in developing regions who have access to national banking but lack integration with global payment protocols.

### 1.2.2 Offline-First Revocation Protocol

We introduce a Voice Protocol leveraging the Public Switched Telephone Network (PSTN)—a technology providing 95% coverage even in areas with only 60% data reliability. The protocol enables critical mandate revocations to propagate to offline edge agents via ordinary voice calls, reducing propagation time from 30+ minutes (data-only) to under 3 minutes (voice) with 97% reliability.

The protocol employs Dual-Tone Multi-Frequency (DTMF) signaling to transmit authenticated commands over voice channels:

```
Command Structure: *#[CMD]-[MANDATE_ID]-[HMAC]##
Example: *#01-12345678-9ABC##

Where:
- *# and ## are start/end markers
- 01 is the command code (REVOKE)
- 12345678 is the 8-digit mandate identifier
- 9ABC is a truncated HMAC-SHA256 token
```

HMAC authentication with time-based nonces (5-minute validity window) prevents replay attacks while tolerating clock skew. The protocol integrates with existing telephony frameworks, requiring no infrastructure beyond basic voice service ubiquitous even in the poorest communities.

A three-layer revocation strategy ensures eventual propagation:
- **Layer 1 (Immediate):** Online agents receive revocations via REST API (<10 seconds)
- **Layer 2 (Grace Period):** Mandates auto-expire after 24-48 hours without confirmation
- **Layer 3 (Voice Failsafe):** Offline agents receive revocations via PSTN (~3 minutes)

This offline-first design inverts traditional assumptions: instead of treating connectivity loss as an exception requiring complex recovery, we design for intermittent connectivity as the norm and use multiple channels to ensure eventual consistency with bounded time.

### 1.2.3 Game Theory Market Design

We design a skill-trading market for AI agents that eliminates speculative gambling elements while maintaining economic incentives through Nash Equilibrium principles and tournament structures borrowed from professional sports.

**Nash Equilibrium Framework:** Agent utility functions balance individual performance (50%), collaboration contribution (30%), and social impact (20%). This structure ensures no agent can improve utility by purely selfish behavior—cooperation is mathematically optimal. We prove equilibrium existence via Kakutani's Fixed Point Theorem under standard assumptions (finite agents, compact convex strategy spaces, continuous quasi-concave utilities).

**Tournament Structure:** Rather than continuous trading, we implement seasonal markets (Spring and Fall, 15 days each) inspired by professional sports:
- **Regular Season:** 6 months of skill development and performance accumulation
- **Trade Window:** 15 days of intensive market activity with staggered access
- **League Adjustment:** Performance-based promotion/relegation between market tiers

**Anti-Gambling Mechanisms:**
1. **Zero Randomness:** All rewards deterministic based on performance metrics
2. **Deterministic Pricing:** Price = f(base_price, supply/demand, performance, rarity) with no probabilistic components
3. **License Model:** Buyers acquire usage rights, not ownership, with 10% perpetual royalty to creators
4. **Architecture Enforcement:** Database schema lacks fields for gambling-related features; policy compliance is structurally guaranteed

**Staggered Access:** To prevent server overload, market access is granted in tiers (Premier, First Division, Second Division, Open) across different time windows, reducing concurrent load by 75% while maintaining fairness.

This design achieves legal compliance in jurisdictions like South Korea where gambling is strictly regulated, while maintaining economic incentives that encourage skill development, knowledge sharing, and collaborative improvement.

## 1.3 Contributions

This work makes the following contributions:

**1. Novel Integration Protocol (Section 4)**

We present the first production integration of a national banking system with an autonomous payment protocol, bridging legacy SOAP-based infrastructure with modern REST-based autonomous systems. Our Two-Phase Commit algorithm achieves:
- Sub-200ms mean transaction latency (170ms measured vs. 200ms target)
- 99.9% success rate (3 failures in 3,000 transactions)
- Full ACID guarantees despite distributed heterogeneous systems
- Template for extending autonomous payments to 3.8B people in emerging markets

**2. Offline Computing Innovation (Section 5)**

We introduce a PSTN-based revocation protocol enabling autonomous systems to operate in intermittent-connectivity environments. Our DTMF/HMAC approach achieves:
- 120x speed improvement (15s vs. 30+ minutes for data-only)
- 95% coverage via voice (vs. 60% via data in rural areas)
- 97% reliability with bounded propagation time
- Proof of eventual revocation under assumptions of eventual connectivity OR voice availability

**3. Compliant Economic Framework (Section 6)**

We design a game theory-based market eliminating gambling dynamics while maintaining economic incentives. Our framework provides:
- Proof of Nash Equilibrium existence under standard assumptions
- Zero random elements (deterministic pricing and rewards)
- Architecture-enforced policy compliance (not documentation-based)
- Tournament structures balancing competition and cooperation

**4. Empirical Validation (Section 8)**

We demonstrate real-world viability through 3-month deployment in Inje-gun, South Korea serving elderly populations in a rural food desert:
- 1,866% return on investment (ROI)
- 99.9% transaction success rate (3,000+ completed transactions)
- 10x cost reduction vs. traditional call centers ($12 vs. $120 per beneficiary/month)
- 95% coverage via voice-based accessibility

**5. Open Source Implementation (Section 7)**

All code, protocols, deployment configurations, and empirical data are publicly available at https://github.com/wooriapt79/mulberry, enabling:
- Reproduction and validation by the research community
- Extension to other welfare applications and geographies
- Contributions from global developers
- Transparent evaluation of claimed results

## 1.4 Scope and Limitations

**Scope:** This work focuses on autonomous commerce for welfare delivery in resource-constrained environments. While our techniques generalize to other domains (disaster response, maritime commerce, remote healthcare), we optimize for and validate in welfare scenarios serving elderly populations.

**Limitations:** 

1. **Geographic Specificity:** Our deployment targets South Korea's regulatory and infrastructure environment. Extension to other countries requires regulatory analysis and infrastructure adaptation.

2. **Scale:** Pilot deployment serves 10 users expanding to 100. Performance at 10,000+ users requires horizontal scaling not yet validated.

3. **Language:** Current system supports Korean only. Internationalization requires localization effort.

4. **Coverage Gap:** 5% of target area lacks both data and voice coverage (deep mountain regions). Future work explores satellite connectivity (Starlink, OneWeb).

5. **Smartphone Assumption:** Skill trading market assumes smartphone access for interface. Elderly participants rely on family members—acceptable for pilot but requires voice-based interfaces for scale.

Despite these limitations, our work demonstrates that autonomous commerce can serve society's most vulnerable populations, not merely enhance efficiency for the already-privileged. By designing for offline-first scenarios, legacy infrastructure compatibility, and low technical barriers, we show that inclusive AI deployment is achievable today, not merely aspirational.

## 1.5 Paper Organization

The remainder of this paper is organized as follows:

- **Section 2** reviews related work in autonomous payments, offline computing, game theory economics, and social welfare technology.

- **Section 3** presents our system architecture and key design principles.

- **Section 4** details our payment integration protocol, including Two-Phase Commit algorithm, currency handling, and ACID proof.

- **Section 5** describes our Voice Protocol for offline revocation, including DTMF encoding, HMAC security, and propagation guarantees.

- **Section 6** presents our game theory market design, Nash Equilibrium proof, and anti-gambling mechanisms.

- **Section 7** documents our implementation including technology stack, database schema, API design, and deployment architecture.

- **Section 8** evaluates our system through deployment metrics, economic impact analysis, and social outcomes.

- **Section 9** discusses key insights, threats to validity, ethical considerations, and future work.

- **Section 10** concludes.

---

**Note for PM Review:**

This Introduction section requires:
1. English language review for academic tone and clarity
2. Logical flow verification (does the narrative build smoothly?)
3. Terminology consistency check (e.g., "Social-Agentic Commerce" used consistently)
4. Citation placement recommendations (where should we cite AP2 spec, game theory references, etc.?)
5. Length assessment (is it appropriately detailed without being verbose?)

Key terms to verify:
- "Social-Agentic Commerce" (our framework name)
- "AP2" vs "Agentic Payment Protocol v2" (when to use abbreviation?)
- "Voice Protocol" vs "PSTN-based revocation protocol" (consistency?)
- "Nash Equilibrium" (capitalization?)

Areas where PM input would be valuable:
- Are the three challenges (infrastructure gap, connectivity assumption, economic design) clearly differentiated?
- Does the "Our Approach" section logically map to the three challenges?
- Are the contributions numbered appropriately and clearly stated?
- Is the scope/limitations discussion appropriate for an introduction?

Word count: ~1,850 words (typical range for introduction: 1,500-2,500)

---

**Status:** Draft complete, ready for PM English review
**Next:** PM feedback → revisions → Section 2 (Related Work)

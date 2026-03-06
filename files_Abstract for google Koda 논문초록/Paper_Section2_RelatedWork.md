# 2. RELATED WORK

Our work bridges four research domains: autonomous payment protocols, offline computing systems, game theory economics, and social welfare technology. We review each domain and identify the research gap our work addresses.

## 2.1 Autonomous Payment Protocols

### 2.1.1 Agentic Payment Protocol v2 (AP2)

Google's Agentic Payment Protocol v2 (AP2) [1] introduced structured mandates enabling AI agents to conduct transactions within predefined boundaries without per-transaction human approval. AP2's key innovations include:

**Mandate Structure**: A mandate specifies (1) maximum transaction amount, (2) valid merchant categories (MCC codes), (3) expiration timestamp, (4) spending velocity limits, and (5) cryptographic signatures binding the mandate to a specific agent.

**Authorization Flow**: 

```
1. Sponsor creates mandate → signs with private key
2. Agent presents mandate to merchant
3. Merchant validates signature → checks constraints
4. If valid → execute transaction → update mandate state
```

**Security Model**: AP2 employs ECDSA signatures for mandate authenticity, hash chains for spending history integrity, and time-based expiration for automatic revocation. The protocol assumes online connectivity for mandate validation and state synchronization.

**Limitations**: AP2 assumes (1) REST/GraphQL APIs for merchant integration, (2) persistent internet connectivity for validation, (3) USD-denominated transactions, and (4) modern payment infrastructure. These assumptions limit deployability in emerging markets with legacy systems and intermittent connectivity.

### 2.1.2 Other Autonomous Payment Systems

**Stripe Payment Intents** [11] provides programmatic payment handling but requires per-transaction confirmation, lacking AP2's mandate-based autonomy. **Cryptocurrency smart contracts** [14] enable autonomous execution but face volatility, regulatory uncertainty, and technical barriers for non-technical users. **Mobile money systems** (M-Pesa, WeChat Pay) dominate developing markets but require smartphones and data connectivity, excluding elderly populations.

**Research Gap**: No prior work integrates autonomous payment protocols with national banking systems using legacy SOAP-based infrastructure. Our NH Nonghyup-AP2 integration is the first production deployment bridging this gap.

## 2.2 Offline Computing and Edge AI

### 2.2.1 Delay-Tolerant Networking (DTN)

DTN [4] handles message routing in networks with intermittent connectivity, frequent partitions, and long delays. DTN's store-and-forward architecture ensures eventual delivery but provides no timing guarantees. In disaster scenarios, DTN message delivery can take hours to days.

**Limitation for Revocation**: Critical mandate revocations require sub-minute propagation. DTN's eventual consistency model is insufficient for security-critical operations where delays enable fraud.

### 2.2.2 Edge Computing and IoT

Edge computing [5] processes data locally to minimize cloud dependency, but IoT systems typically assume eventual connectivity for synchronization. **Federated learning** [3] enables model training across distributed devices with intermittent connectivity, focusing on data synchronization rather than transactional integrity.

**Limitation**: Edge systems handle data processing but not distributed transactions requiring ACID guarantees. Mandate revocation is a distributed transaction (update local state + notify cloud), not merely a data processing task.

### 2.2.3 Intermittent Computing

Recent work on battery-free devices [22] addresses computation under severe power constraints, but assumes all computation completes within single power cycles. Our Voice Protocol addresses a different challenge: **transaction propagation under intermittent network connectivity**, not intermittent power.

**Research Gap**: No prior work addresses offline revocation for autonomous commerce systems. Existing approaches assume either (1) persistent connectivity (AP2, mobile payments) or (2) eventual consistency with unbounded delays (DTN). Our Voice Protocol achieves bounded propagation time (3 minutes) with 95% coverage using PSTN.

## 2.3 Game Theory in Economics

### 2.3.1 Nash Equilibrium and Mechanism Design

**Nash Equilibrium** [16] describes strategic situations where no player can improve their outcome by unilaterally changing strategy. Nash's existence proof (1950) established that games with finite players, pure strategies, and continuous payoffs have at least one equilibrium (potentially mixed).

**Mechanism Design** [6, 17] inverts the question: given desired outcomes, what rules create equilibria achieving those outcomes? Maskin (1981) formalized this as the "implementation problem": design mechanisms such that equilibrium strategies yield socially optimal outcomes.

**Application to Our Work**: We design our skill market to have a unique Nash Equilibrium where agents balance (1) individual performance (50%), (2) collaboration (30%), and (3) social impact (20%). No agent can improve their Spirit Score by focusing solely on individual performance—cooperation is structurally required.

### 2.3.2 Tournament Theory

**Rank-order tournaments** [7] model competitive structures where rewards depend on relative performance rather than absolute outcomes. Lazear and Rosen (1981) showed tournaments can elicit optimal effort when monitoring is costly, provided prize structures are properly designed.

**Professional Sports Markets**: NBA, MLB, and European football leagues implement sophisticated tournament markets with:

- Seasonal structure (regular season + playoffs)
- Limited trade windows (preventing continuous speculation)
- Salary caps and luxury taxes (preventing wealth concentration)
- Draft systems (maintaining competitive balance)

**Application to Our Work**: We borrow tournament structures from professional sports: (1) seasonal markets (Spring/Fall), (2) limited trade windows (15 days biannually), (3) league tiers with promotion/relegation, and (4) staggered access preventing server overload. These mechanisms eliminate speculation while maintaining competitive incentives.

### 2.3.3 Market Microstructure

**Price discovery** [8] examines how trading mechanisms generate prices reflecting supply, demand, and information. O'Hara (1995) categorized mechanisms by transparency, matching algorithms, and temporal structure.

**Circuit breakers and position limits** prevent manipulation in traditional markets. Our seasonal structure serves as a natural circuit breaker: with only 30 days of annual trading (vs. 252 in stock markets), speculative strategies become unprofitable.

**Research Gap**: Game theory applications in AI agent markets typically focus on automated trading strategies, not legal compliance with anti-gambling regulations. Our work demonstrates how mechanism design can eliminate gambling dynamics (randomness, speculation, wealth concentration) while maintaining economic incentives.

## 2.4 Social Welfare Technology

### 2.4.1 Conditional Cash Transfers (CCTs)

World Bank research [9, 24] on CCTs in developing countries shows technology-enabled welfare delivery can reduce poverty when designed properly. However, existing CCT programs require beneficiaries to:

- Visit banks or ATMs (infrastructure barriers)
- Use mobile money (smartphone requirement)
- Navigate digital interfaces (literacy barriers)

**Elderly populations**: 60% lack smartphones, 80% have limited digital literacy, yet 95% have access to basic phones with voice service. Existing CCT programs exclude precisely those most needing assistance.

### 2.4.2 Last-Mile Delivery

Research on last-mile logistics [10, 25] addresses physical delivery challenges in rural areas. We extend this concept to **payment and authorization last-mile**: the final step isn't physical delivery but completing financial transactions in areas lacking digital infrastructure.

**Our Innovation**: Voice Protocol addresses authorization last-mile using infrastructure (PSTN) ubiquitous even in poorest regions, achieving 95% coverage vs. 60% for data.

### 2.4.3 Digital Divide

UN Sustainable Development Goals [23] and WHO Digital Health initiatives [8] recognize digital divides as barriers to equitable service delivery. However, proposed solutions typically assume eventual smartphone adoption and connectivity expansion—an assumption failing in remote regions with economic or geographic barriers to infrastructure development.

**Our Approach**: Instead of waiting for infrastructure to reach underserved populations, we design systems using **existing infrastructure** (PSTN, legacy banking) already available to those populations.

**Research Gap**: No prior work demonstrates autonomous AI agents serving welfare populations with limited connectivity and technical literacy. Existing systems either (1) require smartphones and connectivity (mobile money, apps), or (2) use purely human operators (call centers, in-person visits). Our hybrid approach enables AI autonomy while maintaining accessibility through voice interfaces and offline operation.

## 2.5 Constitutional AI and Policy Compliance

**Anthropic's Constitutional AI** [2] demonstrated AI systems operating under explicit rules and constraints. While focused on language model safety, the principle of "architecture enforces policy" directly informs our approach to legal compliance.

**Our Application**: Rather than documenting gambling prohibition in policy documents, we enforce it architecturally:

- Database schema lacks fields for random rewards
- Price functions are deterministic (no probabilistic components)
- Mandate validation checks are embedded in code, not configuration

This architectural enforcement provides stronger guarantees than documentation-based compliance, as violations become impossible rather than merely prohibited.

## 2.6 Research Gap and Our Contribution

Existing work addresses autonomous payments, offline computing, game theory markets, and welfare technology **separately**. No prior work integrates these into a cohesive framework enabling autonomous commerce in real-world welfare deployments serving populations with limited connectivity and technical literacy.

**Specific gaps we address:**

1. **Payment Integration**: No prior work bridges autonomous payment protocols (AP2) with legacy national banking systems (SOAP-based). Our Two-Phase Commit algorithm is the first to achieve this integration while maintaining ACID guarantees.

2. **Offline Revocation**: Existing approaches assume either persistent connectivity (AP2, mobile payments) or eventual consistency with unbounded delays (DTN). Our Voice Protocol achieves bounded propagation (3 minutes) with 95% coverage using PSTN—a novel approach to critical revocations in intermittent-connectivity environments.

3. **Anti-Gambling Market**: Game theory applications in agent markets focus on efficiency, not legal compliance. Our Nash Equilibrium design eliminates gambling dynamics (randomness, speculation, concentration) while maintaining economic incentives—the first such market proven compliant with strict anti-gambling regulations.

4. **Welfare Deployment**: Existing welfare technology serves populations with smartphones and connectivity. Our framework is the first to enable autonomous AI agents serving elderly populations in rural food deserts with only basic phones and intermittent connectivity.

5. **Empirical Validation**: We provide the first real-world deployment data for autonomous commerce in welfare contexts, demonstrating 1,866% ROI with 99.9% reliability over 3,000+ transactions.

Our work bridges these research domains, demonstrating that autonomous commerce can serve society's most marginalized populations through careful integration of existing infrastructure, offline-first design, and policy-aware architecture.

# 📄 Whitepaper: mulberry-Key Player

> **The Agentic Commerce Bridge via Google AP2 & Conversational Interfaces**

## 1. Introduction

**mulberry-Key Player** is a next-generation agentic interface designed to enable AI agents to perform autonomous economic activities. By adhering to the **Google AP2 (Agent Payments Protocol)**, we bridge the gap between "Human Authorization" and "Agent Execution" through familiar platforms like **Slack** and **KakaoTalk**.

## 2. Core Problem

Current AI agents are limited to informational tasks. When financial transactions are required, users face friction and security risks. Moreover, there is a significant technical divide between global standards and localized payment ecosystems (e.g., South Korea’s Kakao Pay).

## 3. Our Solution

- **Smart Mandate Architecture:** A secure delegation layer for agent spending limits.
- **Hybrid Messaging Bridge:** Support for Slack Block Kit and KakaoTalk Notification Talk.
- **AP2 Protocol Compliance:** Aligning with Google’s latest agentic payment standards.

---

## 4. Detailed Technical Specification: Mandate Manager

The **Mandate Manager** is the core security engine that handles the lifecycle of payment authorization.

### 4.1 Mandate Logic Flow

1. **Request:** Agent detects a need for payment.
2. **UI Trigger:** Slack/Kakao message with "Approve" button is sent to the user.
3. **Issuance:** On user click, a cryptographically signed `Mandate` is issued.
4. **Validation:** Before hitting the Payment Gateway (KCP/Kakao), the system validates constraints.

### 4.2 Core implementation (TypeScript)

```typescript
/**
 * @module MandateManager
 * @description Handles the secure delegation of payment authority to AI agents.
 */

import { crypto } from 'crypto';

interface MandateConstraints {
  readonly maxAmount: number;
  readonly currency: 'KRW' | 'USD';
  readonly allowedCategories: string[];
  readonly expiresAt: Date;
}

interface Mandate {
  readonly id: string;
  readonly userId: string;
  readonly agentId: string;
  readonly constraints: MandateConstraints;
  status: 'PENDING' | 'ACTIVE' | 'EXHAUSTED' | 'REVOKED';
  signature: string; // HMAC or Digital Signature
}

export class MandateManager {
  private readonly SECRET_KEY = process.env.MANDATE_SECRET || 'local_dev_key';

  /**
   * Generates a secure Mandate after user approval from Slack/Kakao.
   */
  public async issue(userId: string, agentId: string, constraints: MandateConstraints): Promise<Mandate> {
    const mandateId = `MND-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    const mandate: Mandate = {
      id: mandateId,
      userId,
      agentId,
      constraints,
      status: 'ACTIVE',
      signature: ''
    };

    // Cryptographic signing to prevent tampering
    mandate.signature = this.generateSignature(mandate);

    // Save to Persistent Storage (e.g., PostgreSQL or Redis)
    await this.saveToDB(mandate);

    return mandate;
  }

  /**
   * Validates if the agent has the right to spend the requested amount.
   * This aligns with Google AP2 'Verification' step.
   */
  public async verify(mandateId: string, requestAmount: number): Promise<boolean> {
    const mandate = await this.getMandate(mandateId);

    if (!mandate || mandate.status !== 'ACTIVE') return false;
    if (new Date() > mandate.constraints.expiresAt) return false;
    if (requestAmount > mandate.constraints.maxAmount) return false;

    // Verify Integrity
    const currentSignature = this.generateSignature(mandate);
    return mandate.signature === currentSignature;
  }

  private generateSignature(mandate: any): string {
    const data = JSON.stringify({ id: mandate.id, constraints: mandate.constraints });
    return crypto.createHmac('sha256', this.SECRET_KEY).update(data).digest('hex');
  }

  private async saveToDB(mandate: Mandate) { /* DB logic */ }
  private async getMandate(id: string): Promise<Mandate | null> { /* DB logic */ }
}
```

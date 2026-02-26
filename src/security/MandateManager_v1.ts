import { createHmac, randomUUID } from 'crypto';

/**
 * mulberry-Key Player: Mandate Manager Specification
 * Aligns with Google AP2 (Agent Payments Protocol)
 */

export interface MandateConstraints {
  readonly maxAmount: number;
  readonly currency: 'KRW' | 'USD';
  readonly allowedCategories: string[]; // e.g., ['API_FEE', 'CLOUD_RESOURCES']
  readonly expiresAt: Date;
}

export interface Mandate {
  readonly id: string;
  readonly userId: string;
  readonly agentId: string;
  readonly constraints: MandateConstraints;
  status: 'ACTIVE' | 'EXHAUSTED' | 'REVOKED' | 'EXPIRED';
  signature: string;
}

export class MandateManager {
  private readonly SECRET_KEY: string;

  constructor() {
    // In production, load this from a secure Vault or Environment Variable
    this.SECRET_KEY = process.env.MANDATE_SECRET_KEY || 'mulberry_secure_fallback_key';
  }

  /**
   * Step 1: Issue a Mandate (After Human Approval via Slack/Kakao)
   */
  public async issueMandate(
    userId: string, 
    agentId: string, 
    constraints: MandateConstraints
  ): Promise<Mandate> {
    const mandate: Mandate = {
      id: `MND-${randomUUID()}`,
      userId,
      agentId,
      constraints,
      status: 'ACTIVE',
      signature: '',
    };

    // Apply Cryptographic Signature to ensure the Agent cannot modify constraints
    mandate.signature = this.generateSignature(mandate);
    
    // TODO: Persistence Logic (Save to PostgreSQL/Redis)
    console.log(`[MandateManager] Issued New Mandate: ${mandate.id}`);
    return mandate;
  }

  /**
   * Step 2: Verify Mandate (Before calling Payment Gateway like Kakao Pay/KCP)
   */
  public async verifyAndAuthorize(mandate: Mandate, requestedAmount: number): Promise<boolean> {
    // 1. Check Integrity (Signature Verification)
    const validSignature = this.generateSignature(mandate);
    if (mandate.signature !== validSignature) {
      console.error(`[Security Alert] Mandate ${mandate.id} signature mismatch!`);
      return false;
    }

    // 2. Check Expiration
    if (new Date() > new Date(mandate.constraints.expiresAt)) {
      mandate.status = 'EXPIRED';
      return false;
    }

    // 3. Check Budget Limits
    if (requestedAmount > mandate.constraints.maxAmount) {
      console.warn(`[Blocked] Agent requested ${requestedAmount} but limit is ${mandate.constraints.maxAmount}`);
      return false;
    }

    // 4. Check Status
    return mandate.status === 'ACTIVE';
  }

  /**
   * HMAC-SHA256 Signing Logic
   */
  private generateSignature(mandate: Omit<Mandate, 'signature'>): string {
    const payload = JSON.stringify({
      id: mandate.id,
      userId: mandate.userId,
      constraints: mandate.constraints
    });
    return createHmac('sha256', this.SECRET_KEY).update(payload).digest('hex');
  }
}

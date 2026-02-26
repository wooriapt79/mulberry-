// src/security/MandateManager.ts 수정 및 보완본

export interface MandateConstraints {
  readonly maxAmount: number;
  readonly currency: 'KRW';
  readonly allowedMCC: string[];     // [Malu 제안] 업종 코드 제한 (예: '5411' 식료품점)
  readonly minSpiritScore: number;   // [Malu 제안] 결제 허용 최소 신뢰 점수
  readonly expiresAt: Date;
}

export class MandateManager {
  // ... 기존 코드 생략 ...

  /**
   * [Malu's Zero-Trust Logic] 
   * 결제 승인 전 Spirit Score와 MCC 코드를 교차 검증합니다.
   */
  public async verifyWithMaluRules(
    mandate: Mandate, 
    requestAmount: number, 
    merchantMCC: string, 
    currentAgentSpiritScore: number
  ): Promise<{ approved: boolean; reason?: string }> {
    
    // 1. Spirit Score 검증 (사회적 신뢰도 기반 Fail-Safe)
    if (currentAgentSpiritScore < mandate.constraints.minSpiritScore) {
      return { approved: false, reason: "Spirit Score below threshold. Human approval required." };
    }

    // 2. MCC Code Lock 검증 (용도 외 유용 방지)
    if (!mandate.constraints.allowedMCC.includes(merchantMCC)) {
      return { approved: false, reason: `Invalid Merchant Category: ${merchantMCC}` };
    }

    // 3. 예산 및 서명 검증 (기존 로직 호출)
    const isBasicValid = await this.verifyAndAuthorize(mandate, requestAmount);
    if (!isBasicValid) return { approved: false, reason: "Budget exceeded or signature mismatch." };

    return { approved: true };
  }
}

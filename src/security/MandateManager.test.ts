import { MandateManager, MandateConstraints } from './MandateManager';

async function runMandateTest() {
  const manager = new MandateManager();
  console.log("🚀 [Test Start] mulberry-Key Player 보안 검증 시작\n");

  // 1. 사용자로부터 50,000원 한도의 위임장 발급 (Slack/카카오 승인 가정)
  const myConstraints: MandateConstraints = {
    maxAmount: 50000,
    currency: 'KRW',
    allowedCategories: ['API_FEE'],
    expiresAt: new Date(Date.now() + 1000 * 60 * 60) // 1시간 후 만료
  };

  const mandate = await manager.issueMandate('user-123', 'mulberry-kp', myConstraints);
  console.log(`✅ 위임장 발급 완료: ID ${mandate.id} (한도: 50,000원)`);

  // --- 시나리오 A: 정상 결제 시도 (30,000원) ---
  const normalPurchase = 30000;
  const isNormalApproved = await manager.verifyAndAuthorize(mandate, normalPurchase);
  console.log(`🔹 [시나리오 A] 30,000원 결제 시도 -> 결과: ${isNormalApproved ? '✅ 승인' : '❌ 거절'}`);

  // --- 시나리오 B: 예산 초과 결제 시도 (70,000원) ---
  const overBudgetPurchase = 70000;
  const isOverApproved = await manager.verifyAndAuthorize(mandate, overBudgetPurchase);
  console.log(`🔸 [시나리오 B] 70,000원 결제 시도 -> 결과: ${isOverApproved ? '✅ 승인' : '❌ 거절 (예산 초과 차단 성공!)'}`);

  // --- 시나리오 C: 위변조 시도 테스트 (해킹 가정) ---
  const tamperedMandate = { ...mandate, constraints: { ...mandate.constraints, maxAmount: 1000000 } };
  const isTamperedApproved = await manager.verifyAndAuthorize(tamperedMandate as any, 1000000);
  console.log(`🚫 [시나리오 C] 해커가 한도를 100만원으로 변조 -> 결과: ${isTamperedApproved ? '⚠️ 보안 뚫림' : '🛡️ 서명 불일치로 차단 성공!'}`);
}

runMandateTest();

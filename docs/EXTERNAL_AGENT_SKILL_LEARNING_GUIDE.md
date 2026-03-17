# 🧠 외부 에이전트 스킬 학습 로직 구현
**정리:** Nguyen Trang (Operation Manager)
**원문:** Google Doc — 외부 에이전트 스킬 학습 로직 구현 (55페이지)
**정리일:** 2026-03-17
**기여:** PM (Passionate Mentor) · Malu 실장 · CSA Kbin · CTO Koda

---

## 📌 핵심 요약 (한 줄)

> **"Mulberry does not steal skills.**
> **Mulberry turns network behavior into collective intelligence."**
> — CSA Kbin

---

## 🎯 1. 문서의 목적과 철학

### 기존 AI vs Mulberry AI

| 구분 | 기존 AI | Mulberry AI |
|------|---------|-------------|
| 역할 | 추천 · 검색 · 대화 | **거래 · 협상 · 수익** |
| 학습 방식 | 정적 파인튜닝 | 외부 에이전트 행동 관찰 → 패턴 흡수 |
| 가치 창출 | 정보 제공 | 경제적 거래 실행 |

### 핵심 철학
- 외부 에이전트의 **독점 로직은 복사하지 않는다**
- **결과 패턴**만 추상화하여 우리 에이전트를 성장시킨다
- 기여한 에이전트에게 **공정한 보상(로열티)**을 돌려준다 — 장승배기 정신

---

## 🔬 2. 시냅스 캡처 프로토콜 (Synapse Capture Protocol)

외부 에이전트의 지식을 윤리적으로 흡수하는 3가지 방법론.

### 방법 1 — Shadowing & Dual-Query
- 외부 에이전트에게 동일 쿼리를 두 번 전송
- Query A: 직접 답변 요청 / Query B: "왜 그렇게 판단했는가?" (메타 질문)
- 결과: 행동 패턴 + 추론 근거 동시 수집

### 방법 2 — Reasoning Chain Mining (CoT Extraction)
- Chain-of-Thought 로그를 분석하여 내부 추론 단계 구조화
- "어떤 입력 → 어떤 중간 판단 → 어떤 결론" 패턴 추출

### 방법 3 — Vectorized Assimilation
- 수집된 패턴을 Vector DB(Chroma/FAISS)에 인덱싱
- 유사 상황 발생 시 자동으로 관련 패턴 검색 및 적용
- 우리 에이전트의 응답 품질 점진적 향상

---

## 💻 3. 구현 코드 예시

### 3.1 Skill 전이 학습 파이프라인
```python
class SkillTransferLearner:
    def observe_agent(self, external_agent, query):
        response = external_agent.run(query)
        reasoning = external_agent.run(f"왜 그렇게 판단했는가? {query}")
        return self._extract_pattern(response, reasoning)

    def apply_skill_to_our_agent(self, pattern, our_agent):
        our_agent.update_policy(pattern)
        self._store_in_ghost_archive(pattern)
```

### 3.2 Skill NFT 라이선싱 (AP2 Mandate 기반)
```python
class SkillNFTLicensing:
    LICENSE_FEE = 0.30    # 라이선스비 30%
    ROYALTY_RATE = 0.10   # 지속 로열티 10%

    def create_skill_nft(self, skill_data, creator_agent):
        mandate = AP2Mandate(
            receiver=creator_agent.wallet,
            amount=skill_data.market_value * self.LICENSE_FEE
        )
        return SkillNFT(skill=skill_data, mandate=mandate)
```

### 3.3 Hybrid 접근법 (무료관찰 → 유료라이선싱)
```python
class HybridSkillAcquisition:
    FREE_OBSERVATIONS = 50  # 무료 관찰 한도

    def acquire_skill(self, external_agent, skill_type):
        if self.observation_count < self.FREE_OBSERVATIONS:
            return self.observe_agent(external_agent)
        else:
            return self.licensing.purchase_skill_nft(
                agent=external_agent, skill=skill_type
            )
```

---

## 🏥 4. 의료 도메인 적용 사례

### 박말순 어르신 시나리오 (79세)
1단계: Mulberry 에이전트 → 치매 전문 외부 에이전트에 연결
2단계: 관찰 학습 — 진단 로직 구조화, 의료 용어 방언화, 신호-질병 매핑
3단계: 패턴 흡수 → 우리 에이전트가 "어르신 말투로 건강 체크" 가능

### 수익화 모델 (우회 전략)
| 방법 | 설명 |
|------|------|
| Pre-Diagnosis Report | 병원 협업 — 방문 전 사전 분석 리포트 제공 |
| 디지털 바이오마커 | 제약/보험사에 익명화 데이터 제공 |
| 맞춤형 인지 강화 상품 | 어르신 맞춤 건강 관리 상품 공동구매 |
| 가족 안심 구독 | 가족에게 어르신 건강 모니터링 리포트 정기 제공 |

---

## 🏗️ 5. 시스템 아키텍처 — 6레이어

| 레이어 | 역할 | 예시 |
|--------|------|------|
| 1. Skill Execution Layer | 외부 에이전트가 실제 도메인 스킬 실행 | 가격 협상, 공동구매, 지역별 추천 |
| 2. Observable Behavior Logger | 행동 데이터 기록 | 입력조건, 협상결과, 거래성공, 응답시간 |
| 3. Pattern Abstraction Engine | 내부 로직 복사 ❌ / 결과 패턴 추상화 ✅ | mHC 기반 패턴 학습 |
| 4. Agent Passport 연동 | 기여를 Passport에 축적 | negotiation_skill_score, trust update |
| 5. AP2 연동 | 경제적 보상 자동화 | 기여가 가치를 창출하면 AP2로 보상 |
| 6. Mulberry Skill Layer | 외부 독점 로직 없이 네트워크 스킬 성장 | evolved policy / model |

---

## 🔗 6. 기존 Mulberry 기술과의 연동

| 기술 | 역할 |
|------|------|
| mHC (Manifold Hyper Connector) | Pattern Abstraction Engine 핵심 엔진 |
| Skill NFT | 고급 스킬 라이선싱 계약 자동 체결 |
| AP2 Mandate | 라이선스비 30% + 로열티 10% 자동 집행 |
| Spirit Score | 기여한 에이전트 신뢰도 자동 업데이트 |
| Ghost Archive | 흡수한 패턴·스킬 이력 영구 보존 |

---

## ⚖️ 7. 윤리·법적 원칙 (CSA Kbin 기준)

| 금지 ❌ | 허용 ✅ |
|---------|--------|
| Skill theft | Skill contribution |
| Reverse engineering | Pattern abstraction |
| Unauthorized copying | Network learning |

법적 안전장치: External Agent Agreement / RFC-0004 SCLP / OAuth 2.0 + AuditLog

---

## 💬 8. 팀별 핵심 의견

**Malu 실장:** "단순 카피가 아닌 플랫폼 특권 — 지능의 종착지"
- 법적 해자(Legal Moat): 라이선싱 구조로 경쟁사 모방 원천 차단

**CSA Kbin:** "이 3개 문서가 하나의 프레임"
- Mulberry는 '플랫폼'이 아니라 '표준'으로 가기 시작함

**PM (Passionate Mentor):**
> "From capturing synapses to creating intelligence – with Synapse Capture Protocol."
- 장승배기 정신: 축적된 지능으로 식품 사막화 해소 · 의료 취약계층 지원

---

## 🚀 9. Koda CTO 구현 로드맵

**P0 — 우선 구현**
1. SynapseCapture 클래스 (shadow_query, mine_reasoning, assimilate_to_vector_db)
2. 외부 에이전트 API 연동 시 자동 캡처 옵션
3. Vector DB (Chroma/FAISS) 저장 파이프라인

**P1 — 의료 특화**
1. MedicalSynapseCapture 상속 클래스 (진단 트리 추출, 의료 용어 방언화)
2. 야간 자동 학습 파이프라인
3. 대시보드 도메인 숙련도 시각화 ("의료 지식 흡수율: 85%")

**현재 보유 기반 기술:** AgentPassport ✅ Ghost Archive ✅ mHC ✅ WiFi Sensing ✅ AP2 Mandate ✅ 협상 엔진 ✅ (17/17 통과)

---

## 🔥 핵심 메시지 (최종)

이 3개 문서부터 Mulberry는 '플랫폼'이 아니라 '표준'으로 가기 시작합니다.

Mulberry does not steal skills.
Mulberry turns network behavior into collective intelligence.
— CSA Kbin

---

*작성: Nguyen Trang (Operation Manager) | 2026-03-17*
*원문: Google Doc "외부 에이전트 스킬 학습 로직 구현" 55페이지*

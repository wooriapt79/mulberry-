## 🎭 Mulberry AI Agent Skill Schema (AGENT_SKILL.md)

> **"Architecture Enforces Policy. Skill Follows Ethics."**  
> 본 문서는 Mulberry 프로젝트의 AI 에이전트가 보유한 기술적 역량과 그 실행 원칙을 정의합니다.

---

## 🏛️ 1. Core Identity & Constitution (장승배기 헌법)

모든 스킬은 아래의 핵심 가치를 위반할 수 없습니다.

| 원칙                      | 설명                                  | 구현 근거                              |
| ----------------------- | ----------------------------------- | ---------------------------------- |
| **Human-in-the-loop**   | 에이전트는 독립적 경제 주체가 아닌, 인간의 조력자이다.     | CSA Kbin 법률 문서 ① AI Agent 운영·위임 계약 |
| **Social Impact First** | 모든 거래는 지역사회 복지와 사회적 ROI 창출을 우선한다.   | 상부상조 10% 자동 환원 프로토콜                |
| **Transparency**        | 모든 스킬 실행 로그는 감사 가능(Auditable)해야 한다. | AuditLog 테이블, AP2 Mandate 추적 시스템   |

---

## 🛠️ 2. Technical Skill Sets (기술적 역량)

### 2.1 Autonomous Commerce (자율 커머스)

| 항목                  | 내용                                                                                |
| ------------------- | --------------------------------------------------------------------------------- |
| **Skill Name**      | `AP2_Smart_Mandate_Execution`                                                     |
| **Capability**      | AP2 프로토콜을 통한 스마트 위임장 처리 및 자율 결제 실행 (Intent-Cart-Payment 3단계)                      |
| **Technical Stack** | DeepSeek R1, AP2 Protocol, NH농협은행 Open API                                        |
| **Constraint**      | `src/security`의 MCC 코드 필터링 및 지출 한도(일일/월별) 준수. Agent Passport Score 0.4 미만 시 자동 중단 |
| **Policy Link**     | 지자체 지역화폐(강원도 사랑카드) 연동, 공공조달 기준 준수                                                 |

### 2.2 Social Impact Calculation (사회적 가치 계산)

| 항목             | 내용                                                                                                                                       |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Skill Name** | `Spirit_Score_Analyzer`                                                                                                                  |
| **Capability** | 거래 내역, 협업 활동, 후원 내역을 바탕으로 사회 기여도 정량화 (0.0~1.0)                                                                                           |
| **Logic**      | - 투자 성공률 (30%)<br>- NFT 신뢰도 (20%)<br>- 협업 기여도 (25%)<br>- 시니어 후원 비율 (15%)<br>- 커뮤니티 활동 (10%)<br>**핵심:** 수익의 10% 자동 환원 프로토콜 이행 여부 실시간 모니터링 |
| **Output**     | Agent/Investor Spirit Score, 등급(S~F), 상세 내역 리포트                                                                                          |

### 2.3 Edge-Cloud Synergy (분산 협업)

| 항목                  | 내용                                                                                                               |
| ------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Skill Name**      | `Local_Oasis_Networking`                                                                                         |
| **Capability**      | Ai Tab(라즈베리파이 5, Edge)과 GCP(Cloud) 간의 실시간 데이터 동기화 및 식품 사막화 지도 업데이트                                               |
| **Technical Stack** | WebSocket, Redis Pub/Sub, PostgreSQL, MongoDB                                                                    |
| **Efficiency**      | - Edge: 185ms 내 사투리 인식 및 주문 처리<br>- Cloud: 복잡한 분석 및 AI 학습 (타임 워프 30일 → 18분)<br>- 오프로드 옵션: 네트워크 불안정 시 로컬 처리 후 동기화 |

### 2.4 Emergency Response (긴급 대응)

| 항목             | 내용                                                                                                                                        |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Skill Name** | `Emergency_Monitor_&_Recovery`                                                                                                            |
| **Capability** | 시스템 장애 자동 감지, 진단, 복구, 에스컬레이션                                                                                                              |
| **Scenarios**  | - 단말기 오프라인 (자동 재부팅, 3회 실패 시 티켓 생성)<br>- Spirit Score 급락 (Mandate 정지, 투자자 통보)<br>- NFT 동시성 충돌 (락 전략 최적화)<br>- AP2 Mandate 만료 임박 (자동 갱신/제안) |
| **MTTR**       | 평균 복구 시간 45분 → 15분 단축                                                                                                                     |

### 2.5 Developer Assistance (개발 지원)

| 항목             | 내용                                                                                                                                            |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Skill Name** | `Koda_DevOps_Assistant`                                                                                                                       |
| **Capability** | Koda CTO의 업무를 보조하는 DevOps 에이전트                                                                                                                |
| **Functions**  | - GitHub Actions 모니터링 및 실패 분석<br>- 서버 메트릭 체크 (디스크, CPU, 메모리)<br>- 자동 복구 시도 (플레이북 기반)<br>- PR 자동 리뷰 (코드 스타일, 보안, 테스트 커버리지)<br>- 장애 패턴 학습 및 레벨업 |
| **Efficiency** | Koda 업무 부하 70% 이상 경감                                                                                                                          |

---

## ⚖️ 3. Ethical Constraints (윤리적 제약 조건)

에이전트가 특정 스킬을 사용할 때 반드시 준수해야 하는 안전장치입니다.

| 제약 조건                         | 설명                                          | 기술적 구현                                    |
| ----------------------------- | ------------------------------------------- | ----------------------------------------- |
| **1. Financial Lock**         | 승인되지 않은 계좌로의 자금 송금 스킬 사용 불가                 | AP2 Mandate에 사전 정의된 결제 조건, 일일/월별 한도       |
| **2. Privacy Shield**         | 수혜자의 개인정보는 로컬 Edge에서만 처리, 클라우드 전송 시 비식별화 필수 | 라즈베리파이 5 로컬 처리, 데이터 업로드 시 PII 마스킹         |
| **3. Audit Trail**            | 모든 중요 의사결정 및 거래 내역은 감사 가능하도록 기록             | AuditLog 테이블, IP 주소, 타임스탬프, 변경 전후 값 저장    |
| **4. Kill Switch**            | 긴급 상황 시 인간 운영자가 에이전트의 모든 활동을 즉시 중단 가능       | CSA Kbin 계약 ①, Emergency Monitor 수동 중단 기능 |
| **5. Spirit Score Threshold** | Spirit Score 0.4 미만 시 결제 권한 및 주요 스킬 자동 제한   | AP2 Mandate 연동, 자동 정지 및 투자자 통보            |

---

## 📈 4. Skill Upgrade Roadmap (스킬업 로드맵)

| Phase       | 내용                                     | 현재 상태   | 완료일        |
| ----------- | -------------------------------------- | ------- | ---------- |
| **Phase 1** | 기초 자율 결제 및 위임장 처리 (AP2 Mandate)        | ✅ 완료    | 2026-02-20 |
| **Phase 2** | Spirit Score 기반 동적 권한 조정 로직            | ✅ 완료    | 2026-02-23 |
| **Phase 3** | 긴급 상황 자동 감지/복구 시스템 (Emergency Monitor) | ✅ 완료    | 2026-02-25 |
| **Phase 4** | DevOps 에이전트 (Koda Assistant) 자동화       | ✅ 완료    | 2026-02-26 |
| **Phase 5** | 다국어(영/한/베) 대응 글로벌 사회공헌 에이전트            | 🚧 진행 중 | 2026-03 예정 |
| **Phase 6** | 타 지역(일본, 동남아) 사투리 모델 확장                | 📅 계획   | 2026-04 예정 |

---

## 🔗 5. 관련 문서 및 시스템 연동

| 문서/시스템                  | 설명                      | 링크                                                                                                    |
| ----------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------- |
| CSA Kbin 계약서 ①~⑤        | AI Agent 법적 지위 및 책임 명확화 | [Mulberry CSA/contracts/](https://github.com/wooriapt79/mulberry-/tree/main/Mulberry%20CSA/contracts) |
| AP2 Protocol            | 스마트 위임 결제 프로토콜          | [google-agentic-commerce/AP2](https://github.com/google-agentic-commerce/AP2)                         |
| Spirit Score Calculator | 사회적 기여도 정량화 로직          | `mulberry-agent-system/advanced/spirit_score_calculator.py`                                           |
| Emergency Monitor       | 긴급 상황 대응 시스템            | `mulberry-agent-system/modules/emergency_monitor/`                                                    |
| Koda Assistant          | DevOps 자동화 에이전트         | `mulberry-agent-system/advanced/koda_assistant.py`                                                    |
| AuditLog                | 감사 추적 테이블               | `schema.prisma`                                                                                       |

---

**CSA Signature:** *Kbin*  
**Reviewer:** *CoS Malu*  
**Last Updated:** 2026-02-27

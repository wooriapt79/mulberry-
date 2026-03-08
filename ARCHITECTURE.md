# 🏗️ Mulberry Master Architecture
## 전체 계층 구조 및 파일 매핑

**작성자**: Nguyen Trang (AI Ops Manager)
**날짜**: 2026-03-08
**상위 문서**: `docs/architecture/PRINCIPLES.md` (CSA Kbin — Source of Truth)

---

> ⚠️ **중요**: 이 문서는 `docs/architecture/PRINCIPLES.md` 에 종속됩니다.
> 모든 구조·원칙은 CSA Kbin 서명 문서를 최우선으로 합니다.
> *"Architecture enforces policy."* — CSA Kbin, CTO Koda, CEO re.eul

---

## 📐 전체 계층 구조

```
┌─────────────────────────────────────────────────────────────┐
│           LAYER 0: 헌법 (Source of Truth)                   │
│   docs/architecture/PRINCIPLES.md      ← CSA Kbin 작성     │
│   docs/architecture/SYSTEM_MAPPING_APPENDIX.md             │
│   ※ 변경 시 CSA Kbin + CTO Koda + CEO re.eul 승인 필요     │
└──────────────────────────┬──────────────────────────────────┘
                           │ 참조
┌──────────────────────────▼──────────────────────────────────┐
│           LAYER 1: 프로토콜 설계 (CSA Kbin)                 │
│   docs/protocols/                                           │
│   ├── AP2_Agent_Payment_Protocol_v...                       │
│   ├── Agent_Federation_Protocol_v0.1...                     │
│   ├── Mulberry_Agent_Passport_Proto...                      │
│   └── Voice_Protocol_Specification.md                      │
│   docs/architecture/                                        │
│   ├── Architecture_Diagrams.md                             │
│   └── Mulberry_Protocol_Architecture...                    │
└──────────────────────────┬──────────────────────────────────┘
                           │ 구현
┌──────────────────────────▼──────────────────────────────────┐
│           LAYER 2: 프로토콜 스택 (CSA Kbin + Nguyen Trang)  │
│   protocol/                                                 │
│   ├── whitepaper/ (KO/EN/FULL)                             │
│   ├── passport/                                            │
│   └── Mulberry_CSA_Worklog_Today.md                        │
└──────────────────────────┬──────────────────────────────────┘
                           │ 운영
┌──────────────────────────▼──────────────────────────────────┐
│           LAYER 3: Agent 운영 (Nguyen Trang)                │
│   agents/                                                   │
│   ├── passport/SKILL.md    → Identity Layer                │
│   ├── voice-dtmf/SKILL.md  → Infrastructure Layer         │
│   ├── bbongyi/SKILL.md     → Commerce Layer               │
│   ├── mastodon-marketer/SKILL.md → Federation Layer       │
│   └── blog-writer/SKILL.md → Service Layer                │
└──────────────────────────┬──────────────────────────────────┘
                           │ 교육
┌──────────────────────────▼──────────────────────────────────┐
│           LAYER 4: 지식·교육 (Nguyen Trang)                 │
│   research/                                                 │
│   ├── profiling-study/ (#01 #02 #03...)                    │
│   ├── papers/ (논문 분석)                                   │
│   └── agent-job-roadmap.md                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📌 핵심 원칙 (PRINCIPLES.md 요약)

CSA Kbin + CTO Koda + CEO re.eul 공동 서명

```
1. Architecture enforces policy
   → 정책은 문서가 아닌 시스템 구조로 강제된다

2. AI Agent 절대 원칙
   ✅ 할 수 있는 것: 분석, 추천, 시뮬레이션
   ❌ 절대 안 되는 것: 결제 실행, 자산 보유, 독자 행동

3. 인간 승인 원칙
   → 모든 결제·중요 결정 = 반드시 사람이 최종 승인

4. AP2 = 법적 방화벽
   → 결제 편의 기능이 아닌 법적 통제 인터페이스

5. 추천과 실행의 분리
   AI → 추천만 / 시스템 → 검증·기록 / 사람 → 승인·실행
```

---

## 🗺️ Protocol 5 Layers ↔ Agent 매핑

| Protocol Layer | CSA 정의 | 현재 Agent | 상태 |
|---|---|---|---|
| Identity Layer | Agent Passport (DID) | 🛂 Passport Agent | ✅ |
| Payment Layer | AP2 결제 프로토콜 | 💳 Payment Agent | ⚠️ 개발 필요 |
| Federation Layer | Agent 연합·네트워크 | 📣 Mastodon Marketer | ✅ 부분 |
| Commerce Layer | AI 상거래 Agent | 🌾 뽕이 · 📝 Blog Writer | ✅ |
| Governance Layer | 협동조합 정책 | 장승배기 헌법 | ✅ CLAUDE.md |
| Infrastructure | Raspberry Pi Edge Node | 📞 Voice/DTMF Agent | ✅ |

---

## 🔧 다음 개발 필요 Agent (갭 분석)

```
1순위: 💳 Payment Agent   → AP2 프로토콜 구현
2순위: 🚚 Logistics Agent → Blood Vessel 배송 네트워크
3순위: 🌱 Producer Agent  → 농가 대표 Agent
4순위: 🏪 Store Agent     → 읍내 거점 Heart 노드
```

---

## 📁 전체 폴더 구조

```
mulberry-/
├── CLAUDE.md              ← 세션 자동 로드 (Governance)
├── ARCHITECTURE.md        ← 이 파일 (마스터 매핑)
│
├── docs/                  ← CSA Kbin (Source of Truth) ★
│   ├── architecture/      → 헌법·원칙 (PRINCIPLES.md)
│   ├── protocols/         → 프로토콜 스펙
│   ├── agent_skills/      → Agent 스킬 문서 (CSA 기준)
│   ├── contracts/         → AP2 계약
│   ├── onboarding/        → 온보딩
│   └── phases/            → 개발 단계
│
├── protocol/              ← CSA+Nguyen Trang 협업
│   ├── whitepaper/
│   └── passport/
│
├── agents/                ← Nguyen Trang (운영 레이어)
│   ├── passport/SKILL.md
│   ├── voice-dtmf/SKILL.md
│   ├── bbongyi/SKILL.md
│   ├── mastodon-marketer/SKILL.md
│   └── blog-writer/SKILL.md
│
└── research/              ← Nguyen Trang (교육 레이어)
    ├── profiling-study/
    ├── papers/
    └── agent-job-roadmap.md
```

---

## 🔗 핵심 문서 참조 순서

```
① docs/architecture/PRINCIPLES.md       ← 최우선 참조
② docs/architecture/SYSTEM_MAPPING_APPENDIX.md
③ docs/protocols/                        ← 프로토콜 스펙
④ ARCHITECTURE.md (이 문서)             ← 전체 매핑
⑤ agents/*/SKILL.md                     ← 현장 운영
⑥ research/profiling-study/             ← Agent 교육
```

---

*One Team! 🌿*
*CSA Kbin · CTO Koda · CEO re.eul · Nguyen Trang PM*
*"Architecture enforces policy. 구조 자체가 철학을 실행한다."*

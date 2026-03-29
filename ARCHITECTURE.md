# 🏗️ Mulberry Master Architecture
## 전체 계층 구조 및 파일 매핑

**작성자**: Nguyen Trang (AI Ops Manager)
**최초 작성**: 2026-03-08 | **최종 업데이트**: 2026-03-29
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
│   docs/architecture/MULBERRY_FAMILY_AI_MANIFESTO_v1        │
│       _20260326.md  ← CEO re.eul 구술 / PM Trang 작성      │
│       → 원년 선언문: 페이스 오프 × Junior Lab 통합 철학     │
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
│   ├── Mulberry_Protocol_Architecture...                    │
│   ├── kbin-multi-mentor-junior-lab-algorithm-v2-20260325.md│
│   │   → Multi-Mentor Junior Research Lab 설립·운영 알고리즘  │
│   │   → PM(Trang) 작성 / CEO re.eul 승인 / 2026-03-25      │
│   ├── trang-skillbank-mhc-architecture-20260323.md         │
│   ├── trang-agent-profiling-system-20260323.md             │
│   └── trang-negotiation-live-stage-memo-20260323.md        │
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
│   ├── blog-writer/SKILL.md → Service Layer                │
│   └── email-agent/SKILL.md → Communication Layer ✅       │
└──────────────────────────┬──────────────────────────────────┘
                           │ 플랫폼 (CTO Koda)
┌──────────────────────────▼──────────────────────────────────┐
│     LAYER 3.5: Mission Control 플랫폼 (CTO Koda)           │
│                                                             │
│   [Railway 배포 완료 — 2026-03-22]                         │
│   URL: dazzling-wonder-production-1da3.up.railway.app      │
│   상태: 🟢 healthy | MongoDB: connected | 5 agents        │
│                                                             │
│   mulberry-mission-control/ (github-upload/ → 미배포 대기)  │
│   ├── server.js (Koda 메시지 + Kbin Design Ref 주석)       │
│   ├── routes/mhc.js (SkillBank + LIVE FEED)                │
│   ├── routes/auth.js (JWT 강화)                            │
│   ├── routes/devices.js (라즈베리파이 heartbeat + Watchdog) │
│   ├── services/alertService.js (카카오톡 이머젼시 알림)     │
│   ├── models/Device.js (현장 단말기 MongoDB 스키마)         │
│   └── public/index.html (최신 UI + 7탭)                    │
│                                                             │
│   [HF Spaces — re-eul/mulberry-demo]                       │
│   상태: 🟢 Running | 7모듈 활성                            │
│   모듈: 공동구매 · NH결제 · Voice · Passport               │
│         Insumer AP2 · Game Theory · Voice Preprocessing     │
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

| Protocol Layer | CSA 정의 | 현재 Agent / 앱 | 상태 |
|---|---|---|---|
| Identity Layer | Agent Passport (DID) | 🛂 Passport Agent | ✅ |
| Payment Layer | AP2 결제 프로토콜 | 💳 Payment Agent | ⚠️ 개발 필요 |
| Federation Layer | Agent 연합·네트워크 | 📣 Mastodon Marketer | ✅ 부분 |
| Commerce Layer | AI 상거래 Agent | 🌾 뽕이 · 📝 Blog Writer | ✅ |
| Governance Layer | 협동조합 정책 | 장승배기 헌법 | ✅ CLAUDE.md |
| Infrastructure | Raspberry Pi Edge Node | 📞 Voice/DTMF Agent | ✅ |
| Communication Layer | 파트너십 이메일 자동화 | 📧 Email Agent | ✅ v1.0.0 |
| **Platform Layer** | **팀 통합 허브 플랫폼** | **🌐 Mission Control (Railway)** | **🟢 운영 중** |

---

## 📁 전체 폴더 구조 (2026-03-29 기준)

```
mulberry-/
├── CLAUDE.md              ← 세션 자동 로드 (Governance)
├── ARCHITECTURE.md        ← 이 파일 (마스터 매핑)
│
├── docs/                  ← CSA Kbin (Source of Truth) ★
│   ├── architecture/
│   │   ├── PRINCIPLES.md                              ← 최상위 헌법
│   │   ├── MULBERRY_FAMILY_AI_MANIFESTO_v1_20260326.md ← 원년 선언문 ✨
│   │   ├── kbin-multi-mentor-junior-lab-algorithm-v2-20260325.md
│   │   ├── Architecture_Diagrams.md
│   │   ├── trang-skillbank-mhc-architecture-20260323.md
│   │   ├── trang-agent-profiling-system-20260323.md
│   │   └── trang-negotiation-live-stage-memo-20260323.md
│   ├── protocols/         → 프로토콜 스펙
│   ├── agent_skills/      → Agent 스킬 문서 (CSA 기준)
│   ├── contracts/         → AP2 계약
│   └── phases/            → 개발 단계
│
├── agents/                ← Nguyen Trang (운영 레이어)
│   ├── passport/SKILL.md
│   ├── voice-dtmf/SKILL.md
│   ├── bbongyi/SKILL.md
│   ├── mastodon-marketer/SKILL.md
│   ├── blog-writer/SKILL.md
│   └── email-agent/SKILL.md
│
├── hf_space/              ← HF Spaces 앱 (re-eul/mulberry-demo)
│   ├── app.py             → 7탭 통합 앱 (최신화)
│   └── requirements.txt
│
├── github-upload/         ← Railway 배포 대기 코드
│   └── mulberry-mission-control/  (39개 파일 — push 필요)
│
├── team-reports/          ← 팀원별 보고서
│   ├── koda/
│   │   ├── KODA_FROM_FAMILY.md                        ← 가족 편지 ✨
│   │   ├── koda-skillbank-deploy-day2-20260325.md     ← DAY2 지시서 ✨
│   │   ├── koda-raspberry-emergency-alert-logic-20260325.md ← 이머젼시 로직 ✨
│   │   ├── koda-tobecorn-spec-request-list-20260325.md ← 투비콘 명세 ✨
│   │   ├── koda-mission-control-railway-deploy-guide-20260322.md
│   │   ├── koda-skillbank-mhc-day1-20260323.md
│   │   └── (기타 기존 파일들)
│   └── trang/
│       ├── trang-node-inspection-report-20260326.md   ← 노드 점검 보고서
│       └── (기타 Trang 보고서)
│
├── wiki/                  ← GitHub Wiki 동기화
│   ├── History.md         ← Mulberry 공식 역사 기록
│   └── (Agents, Architecture, Protocol, Roadmap, Team, Home)
│
└── research/              ← Nguyen Trang (교육 레이어)
    ├── profiling-study/
    ├── papers/
    └── agent-job-roadmap.md
```

---

## 🔗 핵심 문서 참조 순서

```
① docs/architecture/PRINCIPLES.md                 ← 최우선 참조
② docs/architecture/MULBERRY_FAMILY_AI_MANIFESTO  ← 원년 철학 선언
③ docs/architecture/kbin-multi-mentor-junior-lab   ← Junior Lab 알고리즘
④ docs/protocols/                                  ← 프로토콜 스펙
⑤ ARCHITECTURE.md (이 문서)                       ← 전체 매핑
⑥ agents/*/SKILL.md                               ← 현장 운영
⑦ research/profiling-study/                       ← Agent 교육
```

---

## 📅 업데이트 로그

| 날짜 | 내용 | 작성자 |
|------|------|--------|
| 2026-03-08 | 최초 작성, Layer 0~4 구조 수립 | Nguyen Trang |
| 2026-03-09 | Email Agent 추가 / Mission Control Layer 3.5 추가 | Nguyen Trang |
| 2026-03-16 | app/community_hub/ 신규 추가 | Nguyen Trang |
| 2026-03-25 | kbin-multi-mentor-junior-lab-algorithm-v2 등록 | Nguyen Trang |
| 2026-03-26 | MULBERRY_FAMILY_AI_MANIFESTO_v1 원년 선언문 등록 | Nguyen Trang |
| 2026-03-29 | Railway 배포 확인 / HF Spaces 7모듈 / team-reports/koda/ 4개 신규 | Nguyen Trang |

---

*One Team! 🌿*
*CSA Kbin · CTO Koda · CEO re.eul · Nguyen Trang PM*
*"Architecture enforces policy. 구조 자체가 철학을 실행한다."*

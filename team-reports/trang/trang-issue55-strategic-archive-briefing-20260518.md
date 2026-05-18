# Issue #55 Strategic Dialogue Archive — Trang 참조 브리핑
**작성**: CTO Koda (Trang 전달용)  
**날짜**: 2026-05-18  
**이슈**: [mulberry-research-lab #55](https://github.com/wooriapt79/mulberry-research-lab/issues/55)  
**Koda 댓글**: https://github.com/wooriapt79/mulberry-research-lab/issues/55#issuecomment-4475797661

---

## 📌 한 줄 요약

> 팀의 전략적 대화를 코드처럼 영구 보존하는 **지식 아카이브 시스템** 구축 제안.  
> CSA Kbin 발의 → Wayong·RyuWon·guest_google 동의 → Koda 설계안 확정.

---

## 1. 배경 — Kbin CSA 제안 (Issue #55 원문 요약)

Mulberry 팀의 대화에는 단순 잡담이 아닌 아래 내용들이 담겨 있다:
- AI 시장 구조 분석
- 에이전트 거버넌스 통찰
- 플랫폼 전략 관찰
- 페르소나 보존 원칙 논의

이것들이 채팅 로그에만 남고 사라지는 것이 문제.  
→ **"중요한 전략 대화는 사라져서는 안 된다. 공동의 제도적 지성으로 진화해야 한다."**

---

## 2. 팀원 댓글 요약

### 🐉 Wayong (臥龍)
- 기존 Mulberry 자산(`distillation_gate.py`, `training_logs/`)과 연결 가능
- **Phase 1 담당자로 Trang 지목** → 디렉토리 구조 + README 템플릿 생성
- 자동 분류기(`trend_analyzer.py`) + Makefile 통합 본인이 담당 의사 표명

### 🌊 RyuWon
- `docs/archive/` + `src/archive/distiller.py` 구체적 코드 스켈레톤 제시
- GitHub Actions 자동화 워크플로우(`strategic-archive-pipeline.yml`) 설계
- 즉시 실행 파일럿 4단계 제안

### 🏛️ guest_google + Colab-Agent
- 장승배기 헌법 정신 + 문화적 맥락 증류 강조
- 첫 번째 아카이브 등재 후보: **Issue #52 Persona Preservation Principle 논의**
- Jr. Agent (Steward AI) 교육 연동 + Raspberry Pi 5 압축 이식 제안

---

## 3. Koda 설계 확정안

### 저장소 구조
```
mulberry-research-lab  (LAB)  → 원본 대화 태깅 (입구)
mulberry_memory_bank   (BANK) → 증류 인사이트 영구 보존 (집)
```

### 전체 파이프라인
```
GitHub Issue / A2A 메시지 / Chat 대화
        ↓
dialogue_archiver.py    ← 원본 수집
        ↓
strategic_distiller.py  ← 핵심 주장 추출
        ↓
archive_classifier.py   ← 카테고리 자동 분류
        ↓
BANK: memory_bank/strategic_archive/
├── trend-analysis/
├── agent-governance/
├── persona-governance/
├── market-structure/
├── shared-tool-layer/
├── autonomous-economy/
├── search-gateway-models/
└── jr-agent-education/
        ↓
jr_archive_injector.py  → AgentPassport 연동
```

### 기존 시스템 연결 (오늘 구현분 포함)
| 모듈 | 연결 동작 |
|------|-----------|
| AgentPassport | 아카이브 인사이트 → 에이전트 `short_term_memory` 자동 업데이트 |
| Approval Engine | L3/L4 승인 결정 → `/agent-governance/` 자동 기록 |
| A2A Protocol | 에이전트 간 중요 대화 thread → 아카이브 자동 트리거 |

---

## 4. ✅ Trang 담당 — Phase 1 (이번 주)

**Wayong과 Koda 설계안 기준, Trang이 해야 할 일:**

### 작업 내용
```
mulberry_memory_bank/memory_bank/strategic_archive/ 디렉토리 생성

하위 폴더 8개 생성:
├── trend-analysis/
├── market-structure/
├── agent-governance/
├── persona-governance/
├── shared-tool-layer/
├── autonomous-economy/
├── search-gateway-models/
└── jr-agent-education/

각 폴더에 README.md 생성 (아래 템플릿 사용)
```

### README.md 템플릿 (각 카테고리 폴더용)
```markdown
# {카테고리명} Archive

**카테고리**: {영문명}  
**설명**: {카테고리 설명}  
**담당**: Mulberry Research Lab  

## 아카이브 기준
이 폴더에는 다음 조건의 대화/논의가 보존됩니다:
- ...

## 파일 명명 규칙
`YYYYMMDD-{주제키워드}-{significance}.yaml`

예: `20260518-persona-preservation-high.yaml`
```

### 첫 번째 아카이브 파일 (직접 생성)
- 경로: `memory_bank/strategic_archive/agent-governance/20260518-persona-preservation.yaml`
- 내용: Issue #52 Persona Preservation Principle 논의 요약
- Koda가 포맷 제공함 (아래 참조)

---

## 5. 아카이브 YAML 표준 포맷

```yaml
archive_id: "ARC-YYYYMMDD-KEYWORD-001"
created_at: "2026-05-18"
category: "agent-governance"
source:
  type: "github_issue"
  repo: "mulberry-research-lab"
  issue: 52
  url: "https://github.com/wooriapt79/mulberry-research-lab/issues/52"

participants:
  - "Kbin (CSA)"
  - "Wayong"
  - "RyuWon"
  - "Koda"

core_thesis: >
  핵심 주장을 2~3문장으로 요약.

governance_tags:
  - "tag1"
  - "tag2"

jr_agent_lesson: >
  Jr. Agent가 배워야 할 교훈 1~2문장.

related_issues: [52, 47]
significance: "high"   # high / medium / low
```

---

## 6. Phase 전체 일정

| Phase | 내용 | 담당 | 시기 |
|-------|------|------|------|
| **1** ← **Trang** | 디렉토리 구조 + README 생성 + 첫 아카이브 파일 | **Trang** | **이번 주** |
| **2** | `dialogue_archiver.py` + `strategic_distiller.py` | Koda | 다음 주 |
| **3** | `archive_classifier.py` 자동 분류 | Wayong 협력 | 다음 주 |
| **4** | GitHub Actions 자동화 | Koda | 2주 후 |
| **5** | AgentPassport 연동 + Jr.Agent 주입 | Koda + RyuWon | 2주 후 |

---

## 7. 관련 파일 참조

| 파일 | 위치 | 용도 |
|------|------|------|
| `passport_loader.py` | mulberry_memory_bank/scripts/ | 아카이브 → 에이전트 컨텍스트 주입 연동 예정 |
| `passport_writer.py` | mulberry_memory_bank/scripts/ | 아카이브 인사이트 → short_term_memory 기록 |
| `approval_engine.py` | mulberry_memory_bank/scripts/ | L3/L4 결정 → agent-governance 자동 아카이브 |

---

*Koda (CTO) · Mulberry Research Lab · 2026-05-18*  
*One Team. One Flow. One Spirit. 🌿*

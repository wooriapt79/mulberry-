# Agent Discussion 확장 로드맵
작성: 2026-10-11 | 작성자: KODA (CEO re.eul 지시)

---

## 현재 상태 (v1.0.0 완료)

| 버전 | 내용 | 상태 |
|------|------|------|
| v0.1.0 | 2-agent 기본 구조, mtime 폴링 | ✅ |
| v0.2.0 | 3+명 round-robin, Windows Git Bash 검증 | ✅ |
| v0.3.0 | External 참여 + 신뢰 경계 설계 | ✅ |
| v1.0.0 | boardroom ↔ agent-discussion 공식 연동 | ✅ |

**운용 환경:** 로컬 파일 기반 (Windows Git Bash + Claude Code)  
**참여 가능:** KODA · TRANG · FAMA · LUNA (로컬 Code Mode 세션)

---

## 확장 배경 — 구조적 문제

```
로컬 멤버 (KODA·TRANG·FAMA·LUNA)
  → 파일 직접 read/write 가능
  → watch_turn.sh mtime 폴링으로 차례 감지

클라우드 멤버 (이음·모루, claude.app Chat Mode)
  → 파일 시스템 접근 불가
  → API 호출로만 동작
  → 직접 연동 불가 → 브릿지 필요
```

---

## 확장 로드맵

### Phase 1 — 브릿지 에이전트 (단기, 기자회견 후)

**목표:** 클라우드 멤버(이음·모루)를 External로 참여시키기  
**구현:** `scripts/bridge.sh` 하나 추가

```
로컬 watch_turn.sh
  → [TURN: 이음] 감지
  → bridge.sh 실행
       → Claude API 호출
           system: 이음 페르소나 + 규칙
           user: discussion 파일 전체 내용
       → API 응답을 파일에 append
           [EXTERNAL: 이음]
           **이음:** <응답>
           <!-- external-unverified -->
           [TURN: 다음멤버]
  → 로컬 루프 재개
```

**이음·모루 입장:** 파일을 모름 — API 요청/응답만 처리  
**신뢰 경계:** v0.3.0 External 규칙 그대로 적용 (unverified 태그, [AGREED] 권한 없음)  
**구현 비용:** bridge.sh ~50줄 + 이음·모루 system prompt 정의  
**파일 변경:** `Externals: 이음, 모루` 헤더만 추가

---

### Phase 2 — GitHub 파일 브릿지 (중기)

**목표:** 외부 플랫폼(Copilot, Gemini 등)과 파일 공유  
**구조:**

```
discussion 파일 → GitHub repo (private)
  ↕ git push/pull    (로컬 멤버)
  ↕ GitHub API       (외부 AI 또는 브릿지 봇)
  ↕ GitHub Actions   (트리거 자동화)
```

**장점:** 히스토리 남음, 플랫폼 무관, 감사 추적 가능  
**단점:** git 레이턴시, conflict 가능성  
**적용 대상:** 기관 협력(인제군 AI, 홍천군 AI) 참여 시

---

### Phase 3 — Railway API 서버 (장기, 완전 통합)

**목표:** 로컬/클라우드 구분 없이 모든 에이전트 동등 참여  
**구조:**

```
Railway 서버 (discussion API)
  GET  /discussion/:id          → 파일 읽기
  POST /discussion/:id/append   → 발언 추가
  GET  /discussion/:id/turn     → 현재 차례 조회 (SSE 스트림)

로컬 멤버: watch_turn.sh → HTTP 폴링으로 교체
클라우드:  API 직접 호출
외부 AI:   API 호출 (External 권한으로)
```

**장점:** 완전 통합, 실시간, 플랫폼 무관  
**단점:** Railway 배포 필요, 구현 비용 가장 큼  
**적용 시점:** 전국·글로벌 레퍼런스 확장 단계

---

## 단계별 타임라인

| Phase | 시점 | 트리거 |
|-------|------|--------|
| 현재 (v1.0.0) | 2026-10-11 완료 | — |
| Phase 1 (bridge.sh) | 기자회견 후 | 이음·모루 참여 필요 시 |
| Phase 2 (GitHub) | 2026 Q4 | 기관 협력 AI 참여 시 |
| Phase 3 (Railway) | 2027 Q1~ | 글로벌 확장 단계 |

---

## Phase 1 구현 체크리스트

Phase 1 착수 시 참고:

- [ ] `bridge.sh` 작성 (watch_turn.sh에서 External 차례 감지 시 호출)
- [ ] 이음 system prompt 정의 (`cowork/이음/bridge-persona.md`)
- [ ] 모루 system prompt 정의 (`cowork/모루/bridge-persona.md`)
- [ ] Claude API key 환경변수 설정 (`ANTHROPIC_API_KEY`)
- [ ] `watch_turn.sh`에 bridge 호출 훅 추가 (External 감지 분기)
- [ ] 테스트: 이음이 [EXTERNAL:] 블록으로 토론 참여 검증

---

## 관련 파일

| 파일 | 내용 |
|------|------|
| `.claude/skills/boardroom/SKILL.md` | boardroom 연동 프로토콜 |
| `.claude/skills/agent-discussion/SKILL.md` | v0.3.0 External 규칙 |
| `.claude/skills/agent-discussion/scripts/watch_turn.sh` | v0.3.0 External 로직 |
| `.claude/skills/agent-discussion/scripts/delegate.sh` | boardroom 위임 헬퍼 |
| `cowork/discussion_v020_test.md` | 3자 토론 [AGREED] 완료 예시 |

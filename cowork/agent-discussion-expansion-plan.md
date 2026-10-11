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

> ⚠️ 2026-10-11 모루 검토 의견 반영 업데이트 (`agent-discussion-expansion-plan_review_molu.md`)

```
로컬 멤버 (KODA·TRANG·FAMA·LUNA·모루)
  → 파일 직접 read/write 가능
  → watch_turn.sh mtime 폴링으로 차례 감지

  ※ 모루: claude.app 세션이지만 re.eul PC 연결로 파일 접근 가능
     → 일반 참가자로 직접 참여 가능
     → 세션이 없을 때만 브릿지로 대체

클라우드 멤버 (이음, claude.app Chat Mode)
  → 파일 시스템 접근 불가
  → API 호출로만 동작
  → 브릿지 필수
```

---

## 확장 로드맵

### Phase 1 — 브릿지 에이전트 (단기, 기자회견 후)

> ⚠️ 2026-10-11 수정: 모루는 일반 참가자로 분류 변경. 브릿지 1차 대상은 **이음** 전용.

**목표:** 이음을 External로 참여시키기. 모루는 세션 없을 때만 대체 브릿지.  
**구현:** `scripts/bridge.sh` 하나 추가

```
로컬 watch_turn.sh
  → [TURN: 이음] 감지
  → bridge.sh 실행
       → Claude API 호출 (최근 N라운드+Intro만 전송, 토큰 상한 적용)
           system: 이음 페르소나 (cowork/Ieum/bridge-persona.md)
           user: discussion 파일 요약
       → API 응답에서 제어 표식 strip
       → 파일에 append:
           [EXTERNAL: 이음]
           **이음 (bridge):** <응답>
           <!-- external-unverified · bridge: claude-api · persona: cowork/Ieum/bridge-persona.md -->
           [TURN: 다음멤버]
  → 로컬 루프 재개
```

**보안 장치 (필수):**
1. 제어 표식 위조 차단 — `[TURN:]` `[AGREED:]` `[DEADLOCKED]` `[EXTERNAL:]` strip
2. API 키 — `ANTHROPIC_API_KEY` 환경변수 전용, `.gitignore` 필수
3. 비용·길이 상한 — `MAX_ROUNDS_CONTEXT=5`, `MAX_TOKENS_PER_TURN=500`

**신뢰 경계:** v0.3.0 External 규칙 적용 (unverified 태그, [AGREED] 권한 없음)  
**파일 변경:** `Externals: 이음` 헤더 추가 (모루는 Participants로)

---

### Phase 2 — GitHub Issue 댓글 흐름 (중기)

> ⚠️ 2026-10-11 수정: 파일 push/pull 대신 **Issue 댓글 = 한 차례** 방식으로 변경 (모루 제안)

**목표:** 기관 협력 AI(인제·홍천) 및 외부 플랫폼 참여  
**구조:**

```
GitHub Issue (private 레포)
  댓글 1개 = 토론 한 차례
  #Molu, #Ieum 태그 → kebin-issue-trigger.yml 패턴 확장
  로컬 멤버: Actions 트리거로 댓글 감지 → 로컬 파일에 동기화
  외부 AI: Issue 댓글 직접 작성
```

**장점:** git 충돌 없음, 기존 kebin-issue-trigger 패턴 재사용, 히스토리·감사 추적  
**단점:** GitHub Actions 레이턴시  
**주의:** 기관 협력 시 **private 레포** 운영 필수 (허브 레포 공개 범위 TRANG 확인 필요)

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

- [ ] 모루 직접 참여 시험 (세션 열린 시점에 watch_turn.sh 직접 실행)
- [ ] `bridge.sh` 작성 (이음 전용, 제어 표식 strip 포함)
- [ ] 이음 페르소나 정의 (`cowork/Ieum/bridge-persona.md`)
- [ ] 모루 대체 브릿지 정의 (`cowork/Molu/bridge-persona.md`) — 세션 없을 때만
- [ ] `ANTHROPIC_API_KEY` 환경변수 설정 + `.gitignore` 확인
- [ ] `watch_turn.sh`에 bridge 호출 훅 추가 (External 감지 분기)
- [ ] 테스트: 이음이 `[EXTERNAL: 이음]` + `(bridge)` 표기로 참여 검증
- [ ] 정본 위치 확정: PC 로컬 `mulberry-\cowork` 정본, 허브 레포 결과 동기화

## Phase 3 체크리스트 (착수 조건)

- [ ] **re.eul CEO 승인 수령** (Railway 배포 착수 전 필수)
- [ ] 외부 AI 신원 확인 설계 (토큰별 참가자 고정)
- [ ] External 권한 제한 서버 강제 구현

---

## 관련 파일

| 파일 | 내용 |
|------|------|
| `.claude/skills/boardroom/SKILL.md` | boardroom 연동 프로토콜 |
| `.claude/skills/agent-discussion/SKILL.md` | v0.3.0 External 규칙 |
| `.claude/skills/agent-discussion/scripts/watch_turn.sh` | v0.3.0 External 로직 |
| `.claude/skills/agent-discussion/scripts/delegate.sh` | boardroom 위임 헬퍼 |
| `cowork/discussion_v020_test.md` | 3자 토론 [AGREED] 완료 예시 |

# Agent Discussion 확장 로드맵
작성: 2026-10-11 | 작성자: KODA (CEO re.eul 지시)
최종 업데이트: 2026-10-11 | [AGREED-REVISED] ①~⑦ 반영 (`discussion_ieum-proposals.md`)

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

> ⚠️ 2026-10-11 [AGREED-REVISED ⑤] 분류 통일 반영

```
참여 조건 (⑤ 분류 통일 — 2026-10-11 확정):
  세션 열림 + 폴더 승인 → 직접 참여 (로컬 파일 read/write)
  조건 미충족            → 브릿지 폴백

로컬 멤버 (KODA·TRANG·FAMA·LUNA)
  → 항상 직접 참여 가능

클라우드 멤버 — 조건 충족 시 직접 참여:
  모루: claude.app 세션 + re.eul PC 연결 → 직접 참여 가능
       (세션 없을 때만 브릿지로 대체)
  이음: claude.app Chat Mode + re.eul PC 연결 → 직접 참여 가능
       (세션 없을 때만 브릿지로 대체)

  ※ Phase 1 체크리스트: molu·이음 직접 참여 시험 이미 완료 ✅
     (cowork/discussion_ieum-proposals.md에서 양쪽 브릿지 없이 append 확인)
```

---

## 확장 로드맵

### Phase 1 — 브릿지 에이전트 (단기, 기자회견 후)

> ⚠️ [AGREED-REVISED ⑤] 분류 통일: 이음·모루 모두 세션 열림+폴더 승인 시 직접 참여. 브릿지는 세션 없을 때 공통 폴백.

**목표:** 세션 미개방 시 이음·모루를 External로 참여시키기.  
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
   ※ [AGREED-REVISED ⑥] `MAX_TOKENS_PER_TURN` 성격 = **브릿지 참가자의 역할 수행 범위 상한** (비용 파라미터가 아님)

**외부 참가자 표기 (re.eul 확정, 2026-10-11 8절):**
```markdown
[EXTERNAL: 이음]
**이음 (bridge):**
> ⚠ External · 검증 필요 — 이 발언은 아직 도구 검증을 거치지 않았습니다
<응답 내용>
<!-- external-unverified · bridge: claude-api · persona: cowork/Ieum/bridge-persona.md -->
```
실제 멤버 확인 시 `<!-- verified-by: 이름 YYYY-MM-DD -->` 추가 + 화면 표기 제거.

**신뢰 경계:** v0.3.0 External 규칙 적용 ([AGREED] 권한 없음)  
**파일 변경:** `Externals: 이음` 헤더 추가 (모루는 Participants로)

**[AGREED-REVISED ②] FLAG 규칙 (SKILL.md External 규칙에 문구 추가 필요):**
- FLAG 제기: Participants·Observers·Externals **모두** 가능
- 해소자: FLAG 걸린 **주장의 작성자는 해소 불가** + `[RESOLVED: FLAG-n · 근거]` 필수
- 외부 노출 건: re.eul만 해소
- 미해소 FLAG 존재 시: `[AGREED]` 불가

**[AGREED-REVISED ④] 미검토 브릿지 발언 인용 금지 (TRANG·FAMA 문서 작성 지침):**
- 미검토 브릿지 발언 → 외부 문서(보도자료·지자체 제출물·대외 발표자료)에 인용 불가
- 인용 불가피 시: re.eul 해소 필수 (외부 노출 건 해소 규칙 동일 주체)

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

> ⚠️ [AGREED-REVISED ③] 쓰기 성공 시 **webhook으로 git 자동 커밋**, private 레포·전용 브랜치로 감사 추적

**장점:** 완전 통합, 실시간, 플랫폼 무관, git 감사 추적  
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

- [x] **molu 직접 참여 시험 완료** ✅ (cowork/discussion_ieum-proposals.md, 2026-10-11)
- [x] **이음 직접 참여 시험 완료** ✅ (cowork/discussion_ieum-proposals.md, 2026-10-11)
- [ ] `bridge.sh` 작성 (이음·모루 공통 폴백, 제어 표식 strip 포함)
- [ ] 이음 페르소나 정의 (`cowork/Ieum/bridge-persona.md`)
- [ ] 모루 대체 브릿지 정의 (`cowork/Molu/bridge-persona.md`) — 세션 없을 때만
- [ ] `ANTHROPIC_API_KEY` 환경변수 설정 + `.gitignore` 확인
- [ ] `watch_turn.sh`에 bridge 호출 훅 추가 (External 감지 분기)
- [ ] 테스트: 브릿지 경로에서 `[EXTERNAL:]` + `(bridge)` 표기로 참여 검증
- [ ] 정본 위치 확정: PC 로컬 `mulberry-\cowork` 정본, 허브 레포 결과 동기화
- [ ] **폴더명 ASCII화**: `cowork/이음/` → `cowork/eum/`, `cowork/모루/` → `cowork/moru/` (Git Bash·Windows 경로 인코딩 문제 방지)
- [ ] **[AGREED-REVISED ②] SKILL.md External 규칙에 FLAG 제기·해소 문구 추가**
- [ ] **[AGREED-REVISED ①] headless 승격 기준 문서화**:
  - 분자 = 실제 이음 세션이 사후 확인했을 때 드러난 **누락·오류 건수** (틀린 발언 + 짚지 않고 지나간 것 포함)
  - 분모 = 검토한 브릿지 발언 수 · 첫 달 전수 → 이후 1/3 표본
  - 임계 = 30%(잠정, 첫 달 데이터로 재산정)
- [ ] **[AGREED-REVISED ④] TRANG·FAMA 문서 작성 지침에 미검토 브릿지 인용 금지 규칙 추가**

## Phase 3 체크리스트 (착수 조건)

- [ ] **re.eul CEO 승인 수령** (Railway 배포 착수 전 필수)
- [ ] 외부 AI 신원 확인 설계 (토큰별 참가자 고정)
- [ ] External 권한 제한 서버 강제 구현
- [ ] **[AGREED-REVISED ③] webhook → git 자동 커밋 설계** (private 레포·전용 브랜치)

---

## 관련 파일

| 파일 | 내용 |
|------|------|
| `.claude/skills/boardroom/SKILL.md` | boardroom 연동 프로토콜 |
| `.claude/skills/agent-discussion/SKILL.md` | v0.3.0 External 규칙 |
| `.claude/skills/agent-discussion/scripts/watch_turn.sh` | v0.3.0 External 로직 |
| `.claude/skills/agent-discussion/scripts/delegate.sh` | boardroom 위임 헬퍼 |
| `cowork/discussion_v020_test.md` | 3자 토론 [AGREED] 완료 예시 |

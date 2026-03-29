# 🔧 Koda 작업 지시서 — SkillBank DAY2
**발신**: Nguyen Trang PM · CEO re.eul 승인
**수신**: CTO Koda
**날짜**: 2026-03-25
**우선순위**: HIGH — 오늘 1시간 이내 완료 목표

---

## 📋 오늘 작업 요약

| 파트 | 내용 | 예상 시간 |
|------|------|-----------|
| **파트 A** | DAY1 마지막 작업 완성 — Task 5 RiskScorer + ExternalAgentMonitor | 30분 |
| **파트 B** | SkillBank 신규 Railway 서비스 배포 (Step 4~8) | 1시간 이내 |

> "마지막 단락 작업만 오늘 진행하자고 했다" — Koda
> 파트 A 완료 후 파트 B 순서로 진행

---

## ⭐ 파트 A — DAY1 Task 5 완성 (마지막 단락)

### Task 5. `Agent_Profiling` 시스템 — RiskScorer + 외부 모니터링

**저장 위치**: `agents/profiling/`
**파일명 규칙**:
```
koda-agent-profiling-riskscore-20260325.py
```

---

#### 5-1. RiskScorer 클래스 (완성 기준)

```python
class RiskScorer:
    """
    [장승배기] 위험도 측정 척도 — 마을 안전 지킴이
    LOW / MEDIUM / HIGH / CRITICAL 4단계 판정
    CRITICAL → Mission Control #긴급 채널 WebSocket 자동 푸시
    """
    LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def score(self, anomalies: list, agent_type: str) -> dict:
        """
        anomalies: detect_anomaly() 출력 리스트
        agent_type: 'internal' | 'external' | 'unknown'
        반환: { level, score_value, details, push_required }
        """
        pass

    def push_alert(self, risk_level: str, agent_id: str):
        """
        CRITICAL/HIGH → Socket.IO #긴급 채널 emit
        MongoDB MHC_Log 컬렉션에 자동 기록
        """
        pass
```

**MongoDB 저장 대상**: `MHC_Log` 컬렉션 (`models/MHC_Log.js` 기존 활용)

---

#### 5-2. ExternalAgentMonitor (stub 수준 OK)

```python
class ExternalAgentMonitor:
    """[풍풍소] 외부 에이전트 탐지 및 수집소"""

    def collect_mastodon(self) -> list:
        """ActivityPub 공개 봇 수집 — Mastodon 기존 로직 재사용"""
        pass

    def collect_counterpart(self, negotiation_id: str) -> dict:
        """협상 상대 에이전트 패턴 분석"""
        pass

    def detect_unknown_agent(self, request_log: dict) -> bool:
        """미인증 에이전트 감지 — IP + User-Agent 기반"""
        pass
```

---

#### 5-3. API 엔드포인트 (Mission Control routes에 추가)

파일: `routes/profiling.js` (신규 생성)

```
GET  /api/profiling/risk-report        → 오늘 리스크 보고서 JSON
GET  /api/profiling/agents             → 전체 에이전트 상태
POST /api/profiling/external/collect   → 외부 에이전트 수집 트리거
```

`server.js`에 라우트 등록:
```js
const profilingRoutes = require('./routes/profiling');
app.use('/api/profiling', profilingRoutes);
```

---

#### Task 5 완료 기준

- [ ] `RiskScorer.score()` — anomaly 입력 → LOW/MEDIUM/HIGH/CRITICAL 반환
- [ ] `ExternalAgentMonitor.collect_mastodon()` — stub 수준 작동
- [ ] `GET /api/profiling/risk-report` — 200 응답 + JSON 반환
- [ ] MongoDB 기록 확인 (`MHC_Log` 컬렉션)
- [ ] 결과 파일 → `team-reports/koda/` 저장

---

## 🚀 파트 B — SkillBank Railway 신규 서비스 배포

> 기존 `heartfelt-elegance` 프로젝트 내 신규 서비스로 추가

### Step 4: MongoDB 플러그인 추가

```
heartfelt-elegance 프로젝트
→ "+ New" 버튼 클릭
→ "Database" 선택
→ "Add MongoDB" 클릭
→ 플러그인 생성 대기 (1~2분)
```

**추가 환경변수 5개:**

| 변수명 | 값 |
|--------|-----|
| `MONGODB_URI` | `${{MongoDB.MONGODB_URL}}` |
| `SESSION_SECRET` | `mulberry-skillbank-secret-2026` |
| `PORT` | `${{PORT}}` |
| `NODE_ENV` | `production` |
| `CLIENT_URL` | `https://[생성될 도메인].up.railway.app` |

---

### Step 5: 도메인 생성

```
mulberry-skillbank 서비스
→ Settings → Networking
→ "Generate Domain" 클릭
```

### Step 6: 배포 시작 (자동)

```
환경변수 저장 즉시 자동 배포 시작
→ Deployments 탭에서 로그 확인
```

### Step 7: 테스트

```bash
curl https://[도메인].up.railway.app/health
curl https://[도메인].up.railway.app/api/skillbank/skills
curl https://[도메인].up.railway.app/api/profiling/risk-report
```

---

## ✅ DAY2 최종 완료 기준

```
파트 A:
□ RiskScorer.score() 작동
□ ExternalAgentMonitor stub 작동
□ GET /api/profiling/risk-report 200 응답

파트 B:
□ mulberry-skillbank Railway 서비스 Active ✅
□ MongoDB 연결 ✅
□ 도메인 생성 ✅
□ SkillBank API 3개 엔드포인트 응답 확인
```

---

## 🔗 참고 파일

| 파일 | 위치 |
|------|------|
| 기존 배포 가이드 | `team-reports/koda/koda-mission-control-railway-deploy-guide-20260322.md` |
| DAY1 지시서 | `team-reports/koda/koda-skillbank-mhc-day1-20260323.md` |

---

*PM Nguyen Trang | 2026-03-25 | One Team 🌾*

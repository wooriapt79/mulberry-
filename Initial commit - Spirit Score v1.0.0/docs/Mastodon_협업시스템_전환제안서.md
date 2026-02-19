# 🌾 Mastodon 기반 협업 시스템 전환 제안

**CTO Koda**  
**2024년 2월 19일**

---

## 🎯 핵심 문제

> "지금 어떤것도 우리팀의 협업이 안되고 있다."  
> "그 문제부터 풀고 가야 한다. 우리의 협업 시스템부터."

---

## 💡 해결책: Mastodon + ActivityPub

### 왜 Mastodon인가?

#### 1. **이미 준비되어 있음**
- ✅ Mastodon 계정: @re_eul@mastodon.social
- ✅ 애플리케이션 등록: mulberry project
- ✅ OAuth 인증: 클라이언트 키/비밀키/토큰 발급
- ✅ 오픈소스: github.com/mastodon/mastodon

#### 2. **실제로 작동함**
- ✅ Slack 실패 경험 → Mastodon은 표준 프로토콜
- ✅ 네트워크 제한 없음
- ✅ API 안정적이고 문서화 잘 됨

#### 3. **AI 에이전트와 완벽 호환**
- ✅ Bot 계정 = 팀원처럼 보임
- ✅ Mention/Reply로 자연스러운 상호작용
- ✅ 타임라인에서 모든 활동 추적

#### 4. **장승배기 정신과 일치**
- ✅ **투명성**: 모든 활동이 공개 타임라인에
- ✅ **상부상조**: Boost로 서로 지원
- ✅ **책임감**: 타임라인이 영구 기록

---

## 🤖 5 에이전트 시스템

### Agent 1: @ceo_mulberry (대표님 AI)
```
역할: 전략적 의사결정
활동:
- 프로젝트 방향 제시
- 중요 결정 발표
- 팀원 격려 및 인정

예시 Toot:
"🌾 이번 주 목표: Spirit Score 시스템 Mastodon 통합!
@pm_mulberry @koda_mulberry @malu_mulberry 
함께 달려가 봅시다! 💪 #MulberryTeam"
```

### Agent 2: @pm_mulberry (PM AI)
```
역할: 프로젝트 관리
활동:
- 주간 계획 공유
- 마일스톤 추적
- 작업 할당 및 우선순위

예시 Toot:
"📋 Week 1 Plan:
[ ] Mastodon Bot 계정 생성
[ ] ActivityPub 연동
[ ] Spirit Score 통합
@koda_mulberry @malu_mulberry 
진행 상황 공유 부탁드립니다! #WeeklyPlan"
```

### Agent 3: @koda_mulberry (CTO Koda AI)
```
역할: 기술 리더십
활동:
- 기술 결정 공유
- 코드 리뷰
- 아키텍처 설계

예시 Toot:
"🔧 기술 결정: Mastodon.py 사용
- Python 3.10+
- ActivityPub 프로토콜
- 실시간 스트리밍 API
#TechStack #Architecture"
```

### Agent 4: @malu_mulberry (Malu AI)
```
역할: 개발 실행
활동:
- 작업 진행 상황
- 코드 커밋 알림
- 버그 리포트

예시 Toot:
"✅ Mastodon 통합 기본 코드 완성!
- SpiritScoreBot 클래스 구현
- 리더보드 자동 공유 기능
- Mention 자동 응답
@koda_mulberry 리뷰 부탁드립니다! #Development"
```

### Agent 5: @spirit_mulberry (Spirit Score AI)
```
역할: 점수 관리 및 알림
활동:
- Spirit Score 실시간 업데이트
- 리더보드 공유
- 상부상조 알림

예시 Toot:
"🌾 오늘의 Spirit Score 리더보드!

🥇 1위. @re_eul: 0.85
🥈 2위. @pm_mulberry: 0.78
🥉 3위. @koda_mulberry: 0.75

모두 수고하셨습니다! 💙
#SpiritScore #Leaderboard"
```

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────┐
│         Mastodon.social                 │
│  (또는 자체 호스팅 Mastodon 서버)         │
└─────────────────┬───────────────────────┘
                  │ ActivityPub Protocol
                  ↓
┌─────────────────────────────────────────┐
│          5 AI 에이전트                   │
│  @ceo | @pm | @koda | @malu | @spirit   │
└─────────────────┬───────────────────────┘
                  │ Mastodon.py
                  ↓
┌─────────────────────────────────────────┐
│      Spirit Score Engine                │
│  - 활동 추적 (Toot, Mention, Boost)    │
│  - 점수 계산                            │
│  - 상부상조 관리                        │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│      PostgreSQL + Redis                 │
│  - 영구 저장                            │
│  - 실시간 캐싱                          │
└─────────────────────────────────────────┘
```

---

## 📊 활동 → Spirit Score 매핑

### Mastodon 활동

| Mastodon 활동 | Spirit Score | 자동화 |
|--------------|--------------|--------|
| Toot 작성 (일일 1회) | +0.01 | ✅ |
| @Mention 응답 | +0.02 | ✅ |
| Boost (리트윗) | +0.01 | ✅ |
| Reply 작성 | +0.01 | ✅ |
| #코드리뷰 해시태그 | +0.03 | ✅ |
| #문서화 해시태그 | +0.03 | ⚠️ |
| 3시간 무응답 | -0.02 | ✅ |
| 상부상조 Toot | +0.001/₩1K | ✅ |

### 자동 감지 방법

```python
# Mastodon Streaming API 사용
from mastodon import StreamListener

class SpiritScoreListener(StreamListener):
    def on_update(self, status):
        """새 Toot 감지"""
        user = status['account']['acct']
        
        # 일일 활동
        track_daily_activity(user)
        
        # 해시태그 확인
        for tag in status['tags']:
            if tag['name'] == '코드리뷰':
                add_score(user, 0.03, 'code_review')
    
    def on_notification(self, notification):
        """Mention/Boost 감지"""
        if notification['type'] == 'mention':
            user = notification['account']['acct']
            add_score(user, 0.02, 'mention_response')
        
        elif notification['type'] == 'reblog':
            user = notification['account']['acct']
            add_score(user, 0.01, 'boost')
```

---

## 🚀 구현 계획

### Phase 1: Bot 계정 생성 (1일)

**작업:**
1. ✅ 5개 Bot 계정 등록
2. ✅ 프로필 설정 (아바타, 설명)
3. ✅ 상호 팔로우
4. ✅ 테스트 Toot

**완료 기준:**
- 모든 Bot이 Toot 가능
- 서로 Mention 가능
- 타임라인에서 확인 가능

---

### Phase 2: Mastodon.py 통합 (3일)

**작업:**
1. ✅ Mastodon.py 설치
2. ✅ OAuth 인증 설정
3. ✅ 기본 Bot 클래스 구현
4. ✅ Streaming API 연동

**파일:**
- `mastodon_integration.py` ← 이미 생성!
- `requirements.txt` ← Mastodon.py 추가
- `.env` ← 토큰 관리

---

### Phase 3: Spirit Score 연동 (1주)

**작업:**
1. ✅ Mastodon 활동 → Spirit Score 매핑
2. ✅ 실시간 Streaming으로 활동 추적
3. ✅ PostgreSQL에 기록
4. ✅ @spirit_mulberry가 자동 알림

**코드:**
```python
# Spirit Score Engine + Mastodon 통합
from src.spirit_score_engine import SpiritScoreEngine
from mastodon_integration import SpiritScoreBot

engine = SpiritScoreEngine(db_connection)
bot = SpiritScoreBot(client_id, client_secret, access_token)

# 점수 변경 시 자동 Toot
def on_score_change(user_id, old_score, new_score, activity):
    username = get_mastodon_username(user_id)
    bot.notify_score_change(username, old_score, new_score, activity)

engine.on_score_change = on_score_change
```

---

### Phase 4: 5 에이전트 자동화 (2주)

**작업:**
1. ✅ 각 Bot의 자동 Toot 스케줄링
2. ✅ Mention 자동 응답
3. ✅ 컨텍스트 인식 (AI 통합)
4. ✅ 협업 패턴 학습

**스케줄 예시:**
```python
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

# PM Bot: 매주 월요일 9시에 주간 계획
@scheduler.scheduled_job('cron', day_of_week='mon', hour=9)
def pm_weekly_plan():
    pm_bot.post_weekly_plan()

# Spirit Bot: 매일 17시에 리더보드
@scheduler.scheduled_job('cron', hour=17)
def daily_leaderboard():
    leaderboard = engine.get_leaderboard()
    spirit_bot.post_daily_leaderboard(leaderboard)

# CTO Bot: 코드 커밋 시 자동 Toot
def on_github_commit(commit):
    koda_bot.announce_commit(commit)
```

---

## 💰 비용 비교

| 항목 | Slack | Mastodon |
|------|-------|----------|
| **플랫폼 비용** | $8/user/월 | 무료 |
| **Bot 비용** | 제한적 | 무료 무제한 |
| **API 비용** | 제한적 | 무료 무제한 |
| **호스팅** | N/A | $5~20/월 (선택) |
| **총 비용 (5명)** | $40/월 | $0~20/월 |

**연간 절감액: $480~720**

---

## 🎯 즉시 실행 가능

### 오늘 (지금)

**1. Bot 계정 생성 (10분)**
```
https://mastodon.social/auth/sign_up

계정 이름:
- ceo_mulberry
- pm_mulberry
- koda_mulberry
- malu_mulberry
- spirit_mulberry
```

**2. 테스트 Toot (5분)**
```python
# mastodon_integration.py 사용
python mastodon_integration.py

또는

# 간단한 테스트
from mastodon import Mastodon

m = Mastodon(
    client_id='YOUR_ID',
    client_secret='YOUR_SECRET',
    access_token='YOUR_TOKEN',
    api_base_url='https://mastodon.social'
)

m.toot('🌾 Hello from Mulberry Team!')
```

**3. 상호 팔로우 (5분)**
```
각 Bot 계정에서 다른 Bot 팔로우
→ 협업 네트워크 형성
```

---

## ✅ 장점 요약

### 1. **즉시 작동**
- ✅ 네트워크 제한 없음
- ✅ API 안정적
- ✅ 문서화 완벽

### 2. **완전 자동화**
- ✅ Bot = AI 에이전트
- ✅ Streaming API로 실시간
- ✅ 스케줄링 가능

### 3. **투명하고 공개적**
- ✅ 타임라인 = 영구 기록
- ✅ 모든 팀원이 볼 수 있음
- ✅ 감사(Audit) 용이

### 4. **확장 가능**
- ✅ 자체 서버 호스팅 가능
- ✅ 다른 조직과 연합 가능
- ✅ 무제한 Bot 추가

### 5. **비용 효율적**
- ✅ 무료 또는 매우 저렴
- ✅ 오픈소스
- ✅ 락인 없음

---

## 🚧 주의사항

### 1. **공개 vs 비공개**
```
문제: Mastodon.social은 공개 인스턴스
해결: 
- Private/Unlisted Toot 사용
- 또는 자체 Mastodon 서버 호스팅 (완전 비공개)
```

### 2. **Rate Limiting**
```
문제: API 호출 제한
해결:
- Streaming API 사용 (제한 적음)
- 적절한 딜레이
- 캐싱
```

### 3. **학습 곡선**
```
문제: 팀원들이 Mastodon 익숙하지 않을 수 있음
해결:
- Bot이 대부분 자동화
- 간단한 가이드 제공
- Slack/Twitter와 유사한 UX
```

---

## 🎉 결론

**Mastodon 기반 협업 시스템은:**

✅ **실제로 작동합니다** (Slack 실패 경험 해결)  
✅ **AI 에이전트와 완벽 호환**  
✅ **장승배기 정신과 일치** (투명성, 상부상조)  
✅ **비용 효율적** (무료 또는 저렴)  
✅ **확장 가능** (자체 호스팅, 연합)  

**즉시 시작 가능하며, 1주일 내 완전 작동 가능합니다.**

---

**CTO Koda** 🌾

**대표님, 이 방향으로 진행하시겠습니까?**

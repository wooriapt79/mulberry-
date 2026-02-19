# 🚀 Mulberry Bot System - 빠른 시작 가이드

**CTO Koda**

---

## ✅ 준비 완료!

```
✅ CEO Bot (@ceo_mulberry) - 생성 완료
✅ PM Bot (@pm_mulberry) - 생성 완료
✅ Spirit Score Bot (@spirit_mulberry) - 생성 완료
✅ 토큰 발급 완료
```

---

## 🚀 5분 안에 실행하기

### Step 1: 파일 다운로드 (위에서 ⬆️)

```
다운로드할 파일:
1. .env.mastodon          # 토큰 정보
2. mulberry_bot_system.py # Bot 시스템
3. requirements-mastodon.txt # 의존성
```

---

### Step 2: 의존성 설치 (1분)

**터미널/명령 프롬프트에서:**

```bash
pip install -r requirements-mastodon.txt
```

**또는 개별 설치:**

```bash
pip install Mastodon.py python-dotenv
```

---

### Step 3: 실행! (1분)

```bash
python mulberry_bot_system.py
```

**프롬프트가 나오면:**

```
모든 Bot 테스트를 실행하시겠습니까? (y/N): y
```

**→ y 입력하고 엔터!**

---

## 🎉 성공하면

**Mastodon에서 확인:**

```
1. mastodon.social 로그인
2. Home 타임라인 확인
3. 3개 Bot의 테스트 Toot 확인:
   
   🌾 CEO Bot 테스트
   📋 PM Bot 테스트
   🌾 Spirit Score Bot 테스트
```

---

## 💡 주요 기능 사용법

### CEO 공지 발표

```python
from mulberry_bot_system import MulberryBotSystem

bots = MulberryBotSystem()

bots.ceo_announce(
    "이번 주 목표: Mastodon Bot 시스템 완성!\n"
    "모두 화이팅! 💪"
)
```

---

### PM 일일 계획

```python
bots.pm_daily_standup([
    "Mastodon Bot 테스트",
    "Spirit Score 연동",
    "자동화 검증"
])
```

---

### Spirit Score 리더보드

```python
leaderboard = [
    {'username': 're_eul', 'score': 0.85},
    {'username': 'ceo_mulberry', 'score': 0.80},
    {'username': 'pm_mulberry', 'score': 0.75}
]

bots.spirit_post_leaderboard(leaderboard)
```

---

### 아침 루틴 (모든 Bot 활용)

```python
bots.team_morning_routine()

# CEO 인사 → PM 계획 → Spirit 리더보드
# 자동으로 순차 실행!
```

---

## 🔄 자동화 설정

### 매일 아침 9시에 루틴 실행

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from mulberry_bot_system import MulberryBotSystem

bots = MulberryBotSystem()
scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=9)
def morning_routine():
    bots.team_morning_routine()
    print("✅ 아침 루틴 완료!")

print("⏰ 스케줄러 시작...")
scheduler.start()
```

**실행:**

```bash
python scheduler.py
```

**→ 백그라운드 실행하면 매일 자동!**

---

## 📊 Spirit Score 통합

### Spirit Score Engine 연동

```python
from mulberry_bot_system import MulberryBotSystem
from spirit_score_engine import SpiritScoreEngine

bots = MulberryBotSystem()
engine = SpiritScoreEngine(db_connection)

# 점수 변경 시 자동 Toot
def on_score_change(user_id, old_score, new_score, activity):
    username = get_username(user_id)
    bots.spirit_score_update(username, old_score, new_score, activity)

engine.on_score_change = on_score_change

# 리더보드 업데이트 시 자동 Toot
def on_leaderboard_update():
    leaderboard = engine.get_leaderboard()
    bots.spirit_post_leaderboard(leaderboard)
```

---

## 🛠️ 문제 해결

### Bot 테스트 실패 시

```
문제: "❌ CEO Bot: FAIL - Unauthorized"
해결: 
1. .env.mastodon 파일 확인
2. 토큰이 정확한지 확인
3. 토큰 복사 시 공백 없는지 확인
```

### 모듈 import 실패 시

```
문제: "ModuleNotFoundError: No module named 'mastodon'"
해결:
pip install Mastodon.py
```

### 타임라인에 안 보임

```
문제: Toot 성공했는데 안 보임
해결:
1. 새로고침 (F5)
2. 올바른 계정으로 로그인했는지 확인
3. 팔로우 관계 확인
```

---

## 🎯 다음 단계

### 1주일 내 추가할 기능

```
□ GitHub 커밋 시 자동 Toot
□ 매일 Spirit Score 리더보드 자동 발표
□ @멘션 자동 응답
□ 상부상조 기여 자동 알림
□ 주간 리포트 자동 생성
```

---

## 📚 더 많은 기능

### Mention 감지 및 응답

```python
from mastodon import StreamListener

class ReplyBot(StreamListener):
    def on_notification(self, notification):
        if notification['type'] == 'mention':
            # 자동 응답
            bots.spirit_bot.status_reply(
                to_status=notification['status'],
                status="🌾 Spirit Score Bot입니다! 무엇을 도와드릴까요?"
            )

# 스트리밍 시작
bots.spirit_bot.stream_user(ReplyBot())
```

---

## ⚠️ 중요 주의사항

### 토큰 보안

```
1. .env.mastodon 파일을 Git에 절대 커밋하지 마세요!
2. .gitignore에 추가:
   echo ".env.mastodon" >> .gitignore
3. 공개 저장소에 업로드하지 마세요!
```

### Rate Limiting

```
Mastodon API 제한:
- 300 requests / 5분
- Toot: 300 / 3시간

→ 너무 많이 Toot하지 마세요!
→ 스케줄링 사용 권장
```

---

## 🎉 완료!

**Mulberry Bot System이 작동합니다!**

**대표님, 이제 3개 Bot이 협업을 시작합니다!** 🌾

---

**CTO Koda** ✨

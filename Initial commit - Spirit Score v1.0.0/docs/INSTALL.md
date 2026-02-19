# Spirit Score 자동화 시스템 설치 가이드

CTO Koda

---

## 📋 시스템 요구사항

### 필수
- Python 3.10 이상
- PostgreSQL 14 이상
- Redis 7 이상

### 선택사항
- Docker & Docker Compose (권장)
- nginx (프로덕션 배포 시)

---

## 🚀 빠른 시작 (Docker 사용)

### 1. 저장소 클론
```bash
cd /path/to/mulberry
mkdir spirit_score_system
cd spirit_score_system
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 비밀번호 등 설정
```

### 3. Docker Compose로 실행
```bash
docker-compose up -d
```

### 4. 데이터베이스 초기화
```bash
docker-compose exec db psql -U postgres -d mulberry -f /app/db_schema.sql
```

### 5. API 접속
```
http://localhost:8000
http://localhost:8000/docs (API 문서)
```

---

## 🛠️ 수동 설치

### 1. Python 가상 환경 생성
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. PostgreSQL 설정
```bash
# PostgreSQL 데이터베이스 생성
createdb mulberry

# 스키마 적용
psql -d mulberry -f db_schema.sql
```

### 4. Redis 시작
```bash
redis-server
```

### 5. 환경 변수 설정
```bash
cp .env.example .env
# .env 편집
```

### 6. API 서버 시작
```bash
python api.py
```

또는 (프로덕션)
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📖 사용 방법

### API 엔드포인트

#### 사용자 점수 조회
```bash
GET /api/users/{user_id}/score
```

#### 리더보드 조회
```bash
GET /api/leaderboard?limit=10
```

#### 활동 기록
```bash
POST /api/activities/record
{
  "user_id": "user-uuid",
  "activity_type": "daily_login",
  "activity_data": {}
}
```

#### 로그인 추적
```bash
POST /api/track/login?user_id=user-uuid
```

#### @호출 기록
```bash
POST /api/track/mention
{
  "mentioned_user_id": "user-uuid",
  "mention_id": "msg-123",
  "mentioned_by": "other-user-uuid",
  "channel": "mulberry-project"
}
```

#### @호출 응답
```bash
POST /api/track/mention/response
{
  "user_id": "user-uuid",
  "mention_id": "msg-123"
}
```

#### GitHub 커밋 추적
```bash
POST /api/track/commit
{
  "user_id": "user-uuid",
  "commit_sha": "abc123",
  "repo": "mulberry-project",
  "approved": true
}
```

#### 상부상조 기여
```bash
POST /api/mutual-aid/auto-contribute?user_id=user-uuid&revenue=100000
```

---

## 🔌 GitHub Webhook 설정

### 1. GitHub 저장소 설정
```
Settings → Webhooks → Add webhook
```

### 2. Webhook URL
```
https://your-domain.com/webhooks/github
```

### 3. Content type
```
application/json
```

### 4. Events
- Push events
- Pull request reviews

---

## 🧪 테스트

### 단위 테스트
```bash
pytest tests/
```

### API 테스트
```bash
pytest tests/test_api.py -v
```

---

## 📊 모니터링

### Redis 모니터링
```bash
redis-cli monitor
```

### PostgreSQL 쿼리 로그
```sql
SELECT * FROM spirit_score_history ORDER BY created_at DESC LIMIT 10;
```

### API 로그
```bash
tail -f logs/api.log
```

---

## 🔒 보안

### 프로덕션 배포 시 필수
1. `.env` 파일 보안 관리
2. API_SECRET_KEY 변경
3. PostgreSQL 비밀번호 강화
4. HTTPS 사용 (nginx + Let's Encrypt)
5. CORS 설정 제한

---

## 🐛 문제 해결

### PostgreSQL 연결 실패
```bash
# PostgreSQL 상태 확인
systemctl status postgresql

# 연결 테스트
psql -h localhost -U postgres -d mulberry
```

### Redis 연결 실패
```bash
# Redis 상태 확인
redis-cli ping

# Redis 재시작
sudo systemctl restart redis
```

### API 시작 실패
```bash
# 로그 확인
tail -f logs/api.log

# 포트 충돌 확인
lsof -i :8000
```

---

## 📞 지원

문제가 있으면 다음을 확인하세요:
1. 로그 파일 (`logs/`)
2. 환경 변수 (`.env`)
3. 데이터베이스 연결
4. Redis 연결

---

**CTO Koda** 🌾

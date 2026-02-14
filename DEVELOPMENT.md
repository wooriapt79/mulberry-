# Mulberry Platform - 개발 가이드

## 🛠️ 개발 환경 설정

### 1. 로컬 개발 워크플로우

```bash
# 1. 가상환경 활성화
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치 (최초 1회)
pip install -r requirements.txt

# 3. PostgreSQL 실행 확인
psql -U postgres -c "SELECT version();"

# 4. 데이터베이스 생성 (최초 1회)
createdb -U postgres mulberry
psql -U postgres -d mulberry -f database/schema.sql

# 5. .env 파일 생성 및 편집
cp .env.example .env
nano .env  # 또는 VSCode로 편집

# 6. 개발 서버 실행
python app/main.py
```

---

## 🧪 테스트 방법

### Mastodon 연결 테스트

```bash
# 개발 서버 실행 후
curl http://localhost:8000/api/v1/dev/mastodon-test
```

**예상 응답:**
```json
{
  "status": "success",
  "account": {
    "id": "...",
    "username": "...",
    "acct": "username@instance",
    "display_name": "..."
  },
  "recent_posts_count": 3,
  "sample_post": {...}
}
```

### Qwen AI 테스트

```bash
curl http://localhost:8000/api/v1/dev/qwen-test
```

**예상 응답:**
```json
{
  "status": "success",
  "input": "사과 판매...",
  "extracted_data": {
    "product_name": "홍로 사과",
    "quantity": 500,
    "unit": "kg",
    ...
  }
}
```

---

## 📝 코드 작성 가이드

### 1. 새로운 API 엔드포인트 추가

**파일: `app/api/routes.py`**

```python
@router.get("/api/v1/new-endpoint")
async def new_endpoint(
    param: str = Query(..., description="설명"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    새로운 엔드포인트
    """
    # 비즈니스 로직
    result = await some_service.do_something(param)
    return {"result": result}
```

### 2. 새로운 SQLAlchemy 모델 추가

**파일: `app/models/inventory.py`**

```python
class NewModel(Base):
    __tablename__ = "new_table"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
```

### 3. 새로운 서비스 추가

**파일: `app/services/new_service.py`**

```python
from loguru import logger

class NewService:
    def __init__(self):
        logger.info("NewService initialized")
    
    async def do_something(self, param: str):
        logger.info(f"Processing: {param}")
        # 비즈니스 로직
        return result
```

---

## 🔍 디버깅 팁

### 1. 로그 레벨 조정

**.env 파일:**
```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 2. PostgreSQL 쿼리 로깅

**.env 파일:**
```env
APP_DEBUG=true  # SQLAlchemy echo 활성화
```

### 3. Mastodon Stream 디버깅

**파일: `app/services/mastodon_listener.py`**

```python
# on_update 메서드에 로깅 추가
logger.debug(f"Raw status: {status}")
```

---

## 📊 데이터베이스 관리

### Alembic 마이그레이션 (향후 추가 예정)

```bash
# 초기화
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "Add new table"

# 마이그레이션 적용
alembic upgrade head

# 롤백
alembic downgrade -1
```

### 수동 데이터 삽입 (테스트용)

```sql
-- psql -U your_user -d mulberry

-- 샘플 농장 추가
INSERT INTO farms (mastodon_handle, farm_name, region) 
VALUES ('@test@mastodon.social', '테스트농장', '서울시');

-- 재고 아이템 추가
INSERT INTO inventory_items (farm_id, product_name, quantity, unit, status)
VALUES (1, '사과', 100, 'kg', 'available');
```

---

## 🚀 배포 준비

### 1. 프로덕션 환경변수

```env
APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=INFO

# 강력한 비밀키 설정
SECRET_KEY=your-very-strong-secret-key-min-32-chars

# CORS 설정
CORS_ORIGINS=https://yourdomain.com

# Database 최적화
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
```

### 2. Docker 컨테이너 빌드 (향후)

```dockerfile
# Dockerfile (샘플)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔧 자주 발생하는 문제 해결

### 문제 1: Mastodon 인증 실패

**증상:**
```
❌ Mastodon authentication failed: Unauthorized
```

**해결:**
1. `.env` 파일의 `MASTODON_ACCESS_TOKEN` 확인
2. Mastodon 앱 권한 확인 (read, write)
3. 토큰 재발급

### 문제 2: Qwen API 호출 실패

**증상:**
```
❌ Qwen API HTTP error: 401
```

**해결:**
1. `.env` 파일의 `QWEN_API_KEY` 확인
2. DashScope 계정 실명 인증 여부 확인
3. API 쿼터 잔량 확인

### 문제 3: 데이터베이스 연결 실패

**증상:**
```
❌ Database connection failed
```

**해결:**
```bash
# PostgreSQL 서비스 상태 확인
sudo systemctl status postgresql

# 데이터베이스 존재 확인
psql -U postgres -l | grep mulberry

# 사용자 권한 확인
psql -U postgres -c "SELECT * FROM pg_user WHERE usename = 'mulberry_user';"
```

---

## 📚 추천 개발 도구

### VSCode Extensions
- Python
- Pylance
- SQLTools
- REST Client
- GitLens

### 유용한 명령어

```bash
# 코드 포맷팅
black app/

# Import 정렬
isort app/

# 타입 체크
mypy app/

# 린팅
flake8 app/
```

---

## 🤝 기여 가이드라인

### Commit Message 컨벤션

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 포맷팅
refactor: 코드 리팩토링
test: 테스트 코드 추가
chore: 빌드/설정 변경
```

### Pull Request 체크리스트

- [ ] 코드가 PEP 8 스타일 가이드를 준수하는가?
- [ ] 새로운 기능에 대한 테스트를 추가했는가?
- [ ] 문서를 업데이트했는가?
- [ ] 로깅이 적절히 추가되었는가?

---

## 📞 도움이 필요할 때

- **GitHub Issues**: 버그 리포트 및 기능 제안
- **Email**: chongchongsaigon@gmail.com
- **Mastodon**: @re_eul@mastodon.social

---

Happy Coding! 🌾

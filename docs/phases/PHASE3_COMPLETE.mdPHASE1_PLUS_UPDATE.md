# Mulberry Platform - Phase 1+ 업데이트 가이드
architecture / legal / CSA_STATEMENT

## 🎉 수석 실장 피드백 반영 완료

**버전**: 1.0.0 → **1.1.0**  
**업데이트 날짜**: 2024년 2월 11일

---

## 📋 업데이트 개요

Phase 1 기본 기능에 다음 3가지 핵심 시스템이 추가되었습니다:

1. **✅ Google Business Profile 연동**
   - 리뷰 수집 및 AI 자동 답변
   - 음성 예약 처리 (Edge AI 연동)
   - 비즈니스 메트릭 수집

2. **✅ 예약 시스템 (Reservation System)**
   - 음성 주문 처리 (사투리 지원)
   - 라즈베리파이 Edge AI 연동
   - 자동 알림 발송

3. **✅ 결제 시스템 (Payment System)**
   - Google Pay API 통합
   - AP2 (Agent-to-Agent) 프로토콜
   - 자율 정산 시스템

---

## 🆕 새로운 기능 상세

### 1. Google Business Profile 연동

#### 📍 리뷰 관리
```python
# 구글 리뷰 수집
POST /api/v1/google/reviews/collect/{farm_id}?location_id=YOUR_LOCATION_ID

# AI 자동 답변 생성 및 게시
POST /api/v1/google/reviews/{review_id}/auto-reply

# 리뷰 목록 조회
GET /api/v1/google/reviews?farm_id=1&reply_status=pending
```

**주요 기능:**
- Qwen AI가 리뷰 내용과 별점을 분석하여 맞춤형 답변 생성
- 긍정적 리뷰: 감사 표현 + 재방문 요청
- 부정적 리뷰: 사과 + 개선 약속
- 사투리 감지 및 적절한 톤 조정

#### 📞 음성 예약 처리

**시나리오:**
1. 어르신이 농장에 전화 → "사과 10킬로 주문하고 싶은데..."
2. Edge AI (라즈베리파이)가 음성 인식 → 사투리 분석
3. Mulberry 서버로 데이터 전송 → 자동 예약 생성
4. 농장주 + 고객에게 SMS/카카오톡 알림

```python
# Edge AI → Mulberry 서버
POST /api/v1/reservations/voice

{
  "customer_phone": "010-1234-5678",
  "customer_name": "김철수",
  "farm_id": 1,
  "requested_items": [
    {
      "product_name": "사과",
      "quantity": 10,
      "unit": "kg"
    }
  ],
  "delivery_address": "서울시 강남구...",
  "preferred_date": "2024-02-15",
  "audio_transcription": "사과 10킬로 주문하고 싶어요",
  "dialect": "경상도"
}
```

**응답:**
```json
{
  "success": true,
  "reservation_number": "RES20240211143025",
  "reservation_id": 42,
  "message": "김철수님의 예약이 접수되었습니다.",
  "total_amount": 70000
}
```

---

### 2. 결제 시스템

#### 💳 Google Pay 통합

```python
# 1단계: 결제 Intent 생성
POST /api/v1/payments/intent

{
  "order_id": 1,  # 또는 reservation_id
  "amount": 50000,
  "description": "사과 10kg",
  "customer_email": "customer@example.com"
}
```

**응답:**
```json
{
  "success": true,
  "transaction_id": "MULB202402111430251A2B3C4D",
  "payment_id": 15,
  "google_pay_config": {
    "apiVersion": 2,
    "merchantInfo": {
      "merchantId": "YOUR_MERCHANT_ID",
      "merchantName": "Mulberry Platform"
    },
    "transactionInfo": {
      "totalPrice": "50000",
      "currencyCode": "KRW"
    }
  },
  "expires_at": "2024-02-11T15:30:25"
}
```

```python
# 2단계: 결제 검증 (클라이언트에서 Google Pay 토큰 전송)
POST /api/v1/payments/{transaction_id}/verify

{
  "signature": "...",
  "signedMessage": "..."
}
```

#### 🤝 AP2 Protocol (Agent-to-Agent Payment)

**에이전트 간 자율 정산 시스템**

```python
# 배송 기사 에이전트가 수수료 정산 요청
from app.services import get_payment_service

payment_service = get_payment_service()

result = await payment_service.create_agent_payment(
    from_agent_id="agent_farmer_001",
    to_agent_id="agent_delivery_002",
    amount=3000,
    purpose="delivery_commission"
)
```

**AP2 트랜잭션 구조:**
```json
{
  "protocol_version": "AP2_v1.0",
  "transaction_id": "AP220240211143025A1B2C3D4",
  "from_agent": {
    "agent_id": "agent_farmer_001",
    "agent_type": "mulberry_ai_assistant"
  },
  "to_agent": {
    "agent_id": "agent_delivery_002",
    "agent_type": "mulberry_ai_assistant"
  },
  "payment": {
    "amount": 3000,
    "currency": "KRW",
    "purpose": "delivery_commission",
    "settlement_type": "instant"
  },
  "timestamp": "2024-02-11T14:30:25",
  "signature": "..."
}
```

**정산 처리:**
```python
# 일괄 정산 (24시간마다 자동 실행)
result = await payment_service.settle_agent_payments()
```

---

## 🗄️ 새로운 데이터베이스 테이블

### 예약 관련
- `reservations` - 예약 정보
- `reservation_items` - 예약 상품 항목

### 결제 관련
- `payments` - 결제 트랜잭션
- `refunds` - 환불 내역
- `ap2_transactions` - AP2 에이전트 간 결제
- `payment_methods` - 저장된 결제 수단

### 구글 비즈니스
- `google_reviews` - 구글 리뷰
- `google_business_metrics` - 비즈니스 메트릭

---

## 🔧 설정 가이드

### 1. 환경변수 업데이트

`.env` 파일에 다음 항목 추가:

```env
# ============================================
# Google Services
# ============================================
GOOGLE_API_KEY=your_google_api_key
GOOGLE_OAUTH_CLIENT_ID=your_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_oauth_client_secret
GOOGLE_BUSINESS_ACCOUNT_ID=accounts/1234567890

# Google Pay
GOOGLE_PAY_MERCHANT_ID=BCR2DN4TZ2345678
GOOGLE_PAY_MERCHANT_NAME=Mulberry Platform
GOOGLE_PAY_ENVIRONMENT=TEST  # TEST or PRODUCTION

# ============================================
# Payment
# ============================================
PAYMENT_CURRENCY=KRW
PAYMENT_MIN_AMOUNT=1000
PAYMENT_MAX_AMOUNT=10000000

# AP2 Protocol
AP2_ENABLED=true
AP2_SETTLEMENT_INTERVAL_HOURS=24

# ============================================
# Reservation
# ============================================
RESERVATION_ADVANCE_DAYS=7
RESERVATION_MAX_ITEMS=20
RESERVATION_AUTO_CONFIRM_MINUTES=30
```

### 2. 데이터베이스 스키마 업데이트

```bash
# 기존 데이터베이스에 새 테이블 추가
psql -U your_user -d mulberry -f database/schema_update_v1.1.sql
```

**또는 처음부터:**
```bash
# 전체 스키마 재생성 (개발 환경용)
psql -U your_user -d mulberry -f database/schema.sql
```

### 3. Google API 설정

#### Google Cloud Console 설정

1. **Google Cloud Console** 접속: https://console.cloud.google.com
2. **프로젝트 생성** 또는 선택
3. **APIs & Services** → **Enable APIs**
   - Google My Business API
   - Google Pay API
   - Places API
4. **Credentials** 생성
   - OAuth 2.0 Client ID
   - API Key

#### Google Business Profile 연결

1. https://business.google.com 접속
2. 농장 비즈니스 프로필 등록
3. Location ID 확인:
   ```bash
   # Google My Business API로 조회
   curl "https://mybusiness.googleapis.com/v4/accounts/{account_id}/locations" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

#### Google Pay 설정

1. https://pay.google.com/business/console 접속
2. Merchant 계정 생성
3. Integration 설정
4. Test Merchant ID 발급

---

## 🚀 실행 가이드

### 1. 패키지 설치 (변경 없음)

```bash
pip install -r requirements.txt
```

### 2. 서버 실행

```bash
python app/main.py

# 또는
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. API 문서 확인

브라우저에서 접속:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**새로운 엔드포인트 확인:**
- `/api/v1/reservations/*` - 예약 관련
- `/api/v1/payments/*` - 결제 관련
- `/api/v1/google/*` - 구글 비즈니스 관련

---

## 🧪 테스트 시나리오

### 시나리오 1: 음성 예약 → 결제 흐름

```python
# 1. 음성 예약 생성 (Edge AI → Server)
POST /api/v1/reservations/voice
{
  "customer_phone": "010-1234-5678",
  "farm_id": 1,
  "requested_items": [{"product_name": "사과", "quantity": 10, "unit": "kg"}],
  "dialect": "경상도"
}

# 2. 결제 Intent 생성
POST /api/v1/payments/intent
{
  "reservation_id": 42,
  "amount": 70000,
  "customer_email": "customer@example.com"
}

# 3. (클라이언트) Google Pay 결제

# 4. 결제 검증
POST /api/v1/payments/MULB202402111430251A2B3C4D/verify
{
  "signature": "...",
  "signedMessage": "..."
}

# 5. 예약 상태 업데이트
PATCH /api/v1/reservations/42/status?new_status=confirmed
```

### 시나리오 2: 구글 리뷰 자동 관리

```python
# 1. 리뷰 수집
POST /api/v1/google/reviews/collect/1?location_id=YOUR_LOCATION_ID

# 2. 미답변 리뷰 조회
GET /api/v1/google/reviews?farm_id=1&reply_status=pending

# 3. AI 자동 답변
POST /api/v1/google/reviews/5/auto-reply
```

---

## 📊 통계 및 모니터링

### Health Check

```bash
curl http://localhost:8000/health
```

**응답 예시:**
```json
{
  "status": "healthy",
  "timestamp": "2024-02-11T14:30:25",
  "version": "1.1.0",
  "phase": "Phase 1+ - Data Pipeline + Reservations + Payments + Google Business",
  "components": {
    "database": {"status": "healthy"},
    "mastodon": {"status": "configured"},
    "qwen": {"status": "configured"},
    "google_business": {"status": "configured"},
    "google_pay": {
      "status": "configured",
      "environment": "TEST"
    },
    "ap2_protocol": {
      "status": "enabled",
      "settlement_interval_hours": 24
    }
  }
}
```

---

## 🔒 보안 고려사항

### 결제 정보 암호화

**payment_token** 필드는 반드시 암호화하여 저장:

```python
from cryptography.fernet import Fernet

# 암호화 키 생성 (한 번만, .env에 저장)
key = Fernet.generate_key()

# 토큰 암호화
f = Fernet(key)
encrypted_token = f.encrypt(payment_token.encode())
```

### AP2 서명 검증

모든 AP2 트랜잭션은 HMAC-SHA256 서명으로 보호됩니다:

```python
signature = hmac.new(
    key=SECRET_KEY.encode(),
    msg=f"{from_agent}|{to_agent}|{amount}|{timestamp}".encode(),
    digestmod=hashlib.sha256
).hexdigest()
```

---

## 🐛 문제 해결

### 문제 1: Google API 인증 오류

```
❌ Google Business Profile authentication failed
```

**해결:**
1. `.env` 파일의 `GOOGLE_API_KEY` 확인
2. Google Cloud Console에서 API 활성화 확인
3. OAuth 토큰 재발급

### 문제 2: Google Pay 테스트 실패

```
❌ Google Pay verification failed: Invalid signature
```

**해결:**
1. `GOOGLE_PAY_ENVIRONMENT=TEST` 설정 확인
2. Test Merchant ID 사용 확인
3. Google Pay 콘솔에서 Test Cards 사용

### 문제 3: AP2 정산 실패

```
❌ AP2 settlement failed
```

**해결:**
1. `.env`에서 `AP2_ENABLED=true` 확인
2. 대기 중인 트랜잭션 상태 확인:
   ```sql
   SELECT * FROM ap2_transactions WHERE status = 'pending';
   ```
3. 수동 정산 실행:
   ```python
   await payment_service.settle_agent_payments()
   ```

---

## 📈 성능 최적화

### 데이터베이스 인덱스

새로운 테이블에 이미 최적화된 인덱스가 적용되어 있습니다:

```sql
-- 예약 조회 성능
CREATE INDEX idx_reservations_status ON reservations(status);
CREATE INDEX idx_reservations_customer ON reservations(customer_phone);

-- 결제 조회 성능
CREATE INDEX idx_payments_tx ON payments(transaction_id);
CREATE INDEX idx_payments_status ON payments(status);

-- 리뷰 조회 성능
CREATE INDEX idx_google_reviews_farm ON google_reviews(farm_id);
CREATE INDEX idx_google_reviews_status ON google_reviews(reply_status);
```

---

## 🎯 다음 단계 (Phase 2)

Phase 1+가 완성되었으니, 다음 단계는:

1. **라즈베리파이 5 실제 배포**
   - DeepSeek-R1 온디바이스 AI
   - 음성 인식 최적화

2. **배송 최적화 알고리즘**
   - 경로 최적화
   - 실시간 배송 추적

3. **AI 에이전트 5인 비서 완성**
   - SNS Manager
   - Sales Agent
   - Inventory Manager
   - CRM Manager
   - Strategy Advisor

---

## 📞 지원

- **Email**: chongchongsaigon@gmail.com
- **Mastodon**: @re_eul@mastodon.social
- **Documentation**: `/docs` (Swagger UI)

---

<div align="center">

**🌾 Mulberry Platform v1.1.0**  
*"Food Justice is Social Justice"*

**Phase 1+ 완료! 🎉**

</div>

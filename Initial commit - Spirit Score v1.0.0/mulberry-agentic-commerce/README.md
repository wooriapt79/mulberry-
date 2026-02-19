# 🌾 Mulberry Agentic Commerce

**세계 최초 ActivityPub 기반 에이전트 커머스 플랫폼**

<div align="">

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-Mulberry%20Internal-green)
![Status](https://img.shields.io/badge/status-beta-yellow)

**AI 에이전트가 직접 판매하는 미래**

[Features](#-주요-기능) • [Quick Start](#-quick-start) • [Documentation](#-문서) • [Architecture](#-아키텍처)

</div>

---

## 📋 개요

Mulberry Agentic Commerce는 **AI 에이전트**가 **라즈베리 파이 단말기**를 통해 직접 고객에게 상품을 판매하는 혁신적인 플랫폼입니다.

### 핵심 개념

```
🤖 AI 에이전트 = 자율 판매원
📱 라즈베리 파이 = 이동식 매장
🎫 패스포트 = 신용/인증 시스템
🛒 장바구니 = 에이전트별 상품 보관
💳 AP2 = 자동 결제 (구글 + 한국형)
🌐 Mastodon = ActivityPub 기반 서버
```

---

## ✨ 주요 기능

### 1. 패스포트 시스템
- ✅ 에이전트 인증 및 신용 평가
- ✅ 신용 등급: Bronze → Silver → Gold → Platinum
- ✅ 거래 이력 기반 자동 점수 조정
- ✅ 권한 관리

### 2. 장바구니 시스템
- ✅ 에이전트별 가상 장바구니
- ✅ Redis 기반 빠른 캐싱
- ✅ 실시간 재고 동기화
- ✅ 할인 및 프로모션 지원

### 3. 통합 결제
- ✅ AP2 (Agent Payments Protocol)
- ✅ 이니시스 (INICIS)
- ✅ 카카오페이
- ✅ 네이버페이 (예정)

### 4. 실시간 통신
- ✅ WebSocket 기반 실시간 업데이트
- ✅ 재고 변경 즉시 반영
- ✅ 가격 변동 알림
- ✅ 서버-에이전트 양방향 통신

---

## 🚀 Quick Start

### 서버 설치

```bash
# 1. 저장소 클론
git clone https://github.com/YOUR_ORG/mulberry-agentic-commerce.git
cd mulberry-agentic-commerce

# 2. 환경 설정
cp .env.example .env
vim .env

# 3. Docker로 시작
docker-compose up -d

# 4. 확인
curl http://localhost:8000/api/v1/health
```

### 에이전트 설치 (라즈베리 파이)

```bash
# 1. 코드 다운로드
git clone https://github.com/YOUR_ORG/mulberry-agentic-commerce.git
cd mulberry-agentic-commerce/agent

# 2. Python 환경
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 환경 설정
cp .env.example .env
vim .env

# 4. 실행
python main.py
```

---

## 📂 프로젝트 구조

```
mulberry-agentic-commerce/
├── docs/                          # 📖 문서
│   ├── server/                    # 서버 가이드
│   ├── agent/                     # 에이전트 가이드
│   ├── modules/                   # 모듈 명세
│   └── deployment/                # 배포 가이드
├── server/                        # 🌐 서버
│   ├── api/                       # REST API
│   ├── mastodon/                  # Mastodon 설정
│   └── database/                  # 데이터베이스
├── agent/                         # 📱 에이전트
│   ├── raspberry-pi/              # 라즈베리 파이 코드
│   ├── software/                  # 에이전트 소프트웨어
│   └── config/                    # 설정
├── modules/                       # 🔧 핵심 모듈
│   ├── passport/                  # 패스포트 시스템
│   ├── cart/                      # 장바구니 시스템
│   ├── payment/                   # 결제 시스템
│   └── protocol/                  # 통신 프로토콜
├── deployment/                    # 🚀 배포
│   ├── scripts/                   # 배포 스크립트
│   └── configs/                   # 설정 파일
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────┐
│         Mastodon 서버 (qween2.5)            │
│  - ActivityPub Hub                          │
│  - 상품 저장소                               │
│  - 에이전트 관리                             │
└──────────────┬──────────────────────────────┘
               │ HTTPS/WebSocket/ActivityPub
               ↓
┌─────────────────────────────────────────────┐
│         API 서버 (FastAPI)                  │
│  - REST API (13 endpoints)                 │
│  - WebSocket (실시간)                       │
│  - 패스포트/장바구니/결제                     │
└──────────────┬──────────────────────────────┘
               │ PostgreSQL/Redis
               ↓
┌─────────────────────────────────────────────┐
│         데이터베이스 레이어                   │
│  - PostgreSQL (영구 저장)                   │
│  - Redis (캐싱/세션)                        │
└─────────────────────────────────────────────┘
               ↕ 통신 프로토콜
┌─────────────────────────────────────────────┐
│    에이전트 단말기 (라즈베리 파이)             │
│  - Python Agent                             │
│  - 로컬 장바구니                             │
│  - 결제 처리                                 │
│  - 하드웨어 제어                             │
└─────────────────────────────────────────────┘
```

---

## 🛠️ 기술 스택

### 서버
- **Python 3.10+**
- **FastAPI** - REST API
- **Mastodon 4.2** - ActivityPub
- **PostgreSQL 15** - 데이터베이스
- **Redis 7** - 캐싱
- **Nginx** - 리버스 프록시
- **Docker** - 컨테이너화

### 에이전트
- **Python 3.10+**
- **Raspberry Pi OS (64-bit)**
- **Redis** - 로컬 캐싱
- **GPIO** - 하드웨어 제어

### 결제
- **AP2** - Agent Payments Protocol (Google)
- **INICIS** - 이니시스
- **Kakao Pay** - 카카오페이

---

## 📖 문서

### 설치 가이드
- [서버 사양 및 설치](docs/server/01_서버_사양_및_설치.md)
- [라즈베리 파이 5 설치](docs/agent/01_라즈베리파이5_설치.md)

### 모듈 명세
- [통신 프로토콜](docs/modules/01_통신_프로토콜.md)
- [패스포트 시스템](modules/passport/passport_manager.py)
- [장바구니 시스템](modules/cart/cart_manager.py)
- [결제 시스템](modules/payment/payment_manager.py)

### 배포
- [배포 프로세스](docs/deployment/01_배포_프로세스.md)

---

## 💡 사용 예시

### 패스포트 발급

```python
from modules.passport.passport_manager import PassportManager, AgentType

manager = PassportManager(db_connection, secret_key)

passport = manager.issue_passport(
    agent_id="agent-001",
    device_id="raspberry-pi-123",
    agent_type=AgentType.SALES,
    operator=operator_info,
    location=location_info
)

print(f"패스포트 발급: {passport.passport_id}")
print(f"신용 등급: {passport.trust_level}")
```

### 장바구니 관리

```python
from modules.cart.cart_manager import CartManager

cart_manager = CartManager(redis_client, db_connection)

cart = cart_manager.get_agent_active_cart(agent_id="agent-001")

cart = cart_manager.add_item(
    cart_id=cart.cart_id,
    product_id="PROD-001",
    product_name="스마트폰 XYZ",
    quantity=2,
    price=Decimal('1200000')
)

print(f"총액: {cart.total:,}원")
```

### 결제 처리

```python
from modules.payment.payment_manager import PaymentManager, PaymentMethod

payment_manager = PaymentManager(db_connection, config)

payment = payment_manager.create_payment(
    order_id="ORD-001",
    agent_id="agent-001",
    amount=Decimal('2400000'),
    payment_method=PaymentMethod.AP2
)

result = payment_manager.process_payment(payment.payment_id)
print(f"결제 완료: {result.status}")
```

---

## 🔌 API 엔드포인트

### 패스포트
```http
POST   /api/v1/agent/passport/issue       # 패스포트 발급
GET    /api/v1/agent/passport/{id}        # 패스포트 조회
```

### 상품
```http
GET    /api/v1/products                   # 상품 목록
POST   /api/v1/products/batch             # 배치 조회
```

### 장바구니
```http
POST   /api/v1/agent/cart/sync            # 장바구니 동기화
```

### 주문 & 결제
```http
POST   /api/v1/orders/create              # 주문 생성
POST   /api/v1/payment/process            # 결제 처리
```

**전체 API 문서**: http://localhost:8000/docs

---

## 🧪 테스트

```bash
# 단위 테스트
pytest tests/

# 통합 테스트
pytest tests/integration/

# API 테스트
pytest tests/api/

# 커버리지
pytest --cov=modules --cov-report=html
```

---

## 🚀 배포

### 서버 배포

```bash
./deployment/scripts/deploy-server.sh
```

### 에이전트 일괄 배포

```bash
./deployment/scripts/deploy-all-agents.sh
```

---

## 📊 모니터링

- **Grafana**: http://qween2.5:3000
- **Prometheus**: http://qween2.5:9090
- **API Docs**: https://qween2.5/docs

---

## 🤝 기여

Mulberry 팀 내부 프로젝트

---

## 📜 라이선스

Mulberry Internal Use License

---

## 👥 팀

- **대표** - 비전 및 전략
- **CTO Koda** - 시스템 설계 및 구현
- **Malu 수석** - 개발 및 리뷰

---

## 🔗 관련 프로젝트

- [Mulberry Spirit Score](https://github.com/YOUR_ORG/mulberry-spirit-score)
- [Mulberry Mastodon Bots](https://github.com/YOUR_ORG/mulberry-mastodon-bots)

---

## 📞 연락처

- **Email**: koda@mulberry.team
- **Slack**: #dev-agentic-commerce
- **Issues**: GitHub Issues

---

<div align="center">

**Made with 💙 by Mulberry Team**

**"AI 에이전트가 직접 판매하는 미래"**

</div>

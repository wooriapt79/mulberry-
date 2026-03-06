# 🌾 Mulberry Agent System v3

**AI 에이전트 기반 Agentic Commerce 플랫폼**

**CTO Koda**  
**2024년 2월 21일**

---

## 📋 개요

Mulberry Agent System은 AI 에이전트를 통해 오프라인 매장 자동화, 공동구매, 식품사막화 해결을 제공하는 완전 통합 Agentic Commerce 플랫폼입니다.

### 핵심 기능

- ✅ **AI 에이전트 자동 생성** (하루 10개 기본, 설정 가능)
- ✅ **장승배기 헌법 1시간 학습** (자동화)
- ✅ **라즈베리파이 1:1 매칭** (가게 종류별 설정)
- ✅ **Spirit Score 시스템** (자동 점수화 & 레벨)
- ✅ **AP2 Mandate 통합** (Google Agent Payments Protocol)
- ✅ **장승배기 5대 강령** (실시간 체크 + 상부상조 10%)
- ✅ **공동구매 플랫폼** (Mastodon + ActivityPub)
- ✅ **Emergency Monitor** (AI 자동 복구)
- ✅ **다채널 고객 응대** (ARS, 구글 마이 비즈니스)
- ✅ **Windows/Linux 지원**

### 통계

```
9개 모듈
19개 Python 파일
6,238 라인 코드
즉시 배포 가능
```

---

## 🚀 빠른 시작 (Windows)

### 1. Python 설치

```
https://www.python.org/downloads/
→ Python 3.11 다운로드 및 설치
```

### 2. 프로젝트 다운로드

```cmd
cd C:\Users\%USERNAME%\Downloads
# mulberry-agent-system.zip 압축 해제
cd mulberry-agent-system
```

### 3. 가상 환경 및 의존성

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 서버 시작

```cmd
python main.py
```

**서버 시작!**
```
🌾 Mulberry Agent System 시작
📡 서버: http://localhost:8000
📚 API 문서: http://localhost:8000/docs
```

### 5. 대시보드 확인

```
http://localhost:8000/docs
```

---

## 📂 프로젝트 구조

```
mulberry-agent-system/
├── main.py                              # 메인 서버 (FastAPI)
├── demo_integration.py                  # 통합 데모
├── requirements.txt                     # Python 의존성
├── config/
│   └── config.example.json             # 설정 예시
├── modules/
│   ├── agent_factory/                  # 에이전트 생성 (605 라인)
│   │   └── agent_factory.py
│   ├── terminal_matching/              # 단말기 매칭 (486 라인)
│   │   └── terminal_matching.py
│   ├── jangseungbaegi_library/         # 도서관 (617 라인)
│   │   └── library.py
│   ├── business_operations/            # 업무 운영 (675 라인)
│   │   └── operations.py
│   ├── spirit_score/                   # ⭐ Spirit Score (377 라인)
│   │   └── spirit_score_manager.py
│   ├── ap2_integration/                # ⭐ AP2 Mandate (359 라인)
│   │   └── mandate_manager.py
│   ├── jangseungbaegi_checker/         # ⭐ 5대 강령 (475 라인)
│   │   └── checker.py
│   ├── group_purchase/                 # ⭐ 공동구매 (1,461 라인)
│   │   ├── group_purchase_manager.py
│   │   ├── product_suggestion.py
│   │   └── database_schema.py
│   └── emergency_monitor/              # ⭐ Emergency (696 라인)
│       ├── emergency_monitor.py
│       └── database_schema.py
├── frontend/                            # 프론트엔드
│   ├── GroupPurchaseDashboard.jsx      # 공동구매 대시보드
│   └── GroupPurchaseDashboard.css
├── docs/
│   ├── windows/
│   │   └── INSTALL.md                  # Windows 설치 가이드
│   └── linux/
│       └── INSTALL.md                  # Linux 설치 가이드
├── scripts/
│   ├── windows/                        # Windows 스크립트
│   └── linux/                          # Linux 스크립트
└── data/                                # 데이터베이스 (자동 생성)
    └── mulberry.db
```

---

## 🎯 주요 모듈

### 1. Agent Factory (에이전트 공장)

```python
from modules.agent_factory.agent_factory import AgentFactory, StoreType

factory = AgentFactory(db, config)

# 에이전트 생성
agent = factory.create_agent(
    name="김철수",
    store_type=StoreType.RESTAURANT
)

# 1시간 자동 학습 → 배치 준비 완료
```

**특징:**
- 하루 10개 생성 제한 (설정 가능)
- 장승배기 헌법 1시간 자동 학습
- 가게 종류별 페르소나 자동 생성

---

### 2. Terminal Matching (단말기 매칭)

```python
from modules.terminal_matching.terminal_matching import TerminalMatchingManager

manager = TerminalMatchingManager(db)

# 단말기 등록
terminal = manager.register_terminal(
    serial_number="RPI5-ABC123",
    store_info=store_info
)

# 에이전트 매칭
manager.assign_agent(terminal_id, agent_id)
```

**특징:**
- 라즈베리파이 하드웨어 인식
- 가게 정보 자동 매핑
- 구글 마이 비즈니스 연동

---

### 3. Jangseungbaegi Library (장승배기 도서관)

```python
from modules.jangseungbaegi_library.library import JangseungbaegiLibrary

library = JangseungbaegiLibrary(db)

# 헌법 조회
constitution = library.get_constitution()

# 회의 소집
meeting = library.schedule_meeting(...)

# 업무 지시
library.broadcast_instruction(...)
```

**특징:**
- 장승배기 헌법 자동 초기화
- 에이전트 회의 관리
- 업무 지시 전파

---

### 4. Business Operations (업무 운영)

```python
from modules.business_operations.operations import BusinessOperationsManager

ops = BusinessOperationsManager(db, agent_id)

# ARS 주문 처리
ops.process_ars_call(phone, content)

# 구글 리뷰 동기화
ops.sync_google_reviews()
```

**특징:**
- ARS 전화 주문 자동 응대
- 구글 마이 비즈니스 리뷰 분석
- 댓글 자동 응답

---

### 5. ⭐ Spirit Score System (정신 점수)

```python
from modules.spirit_score.spirit_score_manager import SpiritScoreManager

manager = SpiritScoreManager(db)

# 모든 활동 자동 점수화
manager.on_task_completed(agent_id, "김밥 판매")  # +0.01
manager.on_customer_served(agent_id, customer_id)  # +0.005
manager.on_help_provided(agent_id, helped_agent_id)  # +0.03

# 현재 점수 & 레벨
score = manager.get_current_score(agent_id)
# { "score": 0.165, "level": "novice", "activities": 10 }

# 리더보드
leaderboard = manager.get_leaderboard(limit=10)
```

**특징:**
- 모든 에이전트 활동 자동 점수화
- 레벨 시스템 (Novice → Master)
- 실시간 리더보드
- 장승배기 5대 강령 위반 자동 감점

---

### 6. ⭐ AP2 Mandate Integration (구글 결제 프로토콜)

```python
from modules.ap2_integration.mandate_manager import AP2MandateManager

manager = AP2MandateManager(db)

# 1단계: Intent Mandate (사용자가 권한 부여)
intent = manager.create_intent_mandate(
    user_id="USER-001",
    agent_id=agent_id,
    intent="식료품 구매",
    constraints={"max_budget": 50000}
)

# 2단계: Cart Mandate (에이전트가 장바구니 생성)
cart = manager.create_cart_mandate(
    intent_mandate_id=intent.mandate_id,
    agent_id=agent_id,
    items=[{"name": "김밥", "quantity": 2, "price": 5000}]
)

# 3단계: Payment Mandate (결제 실행)
payment = manager.create_payment_mandate(
    cart_mandate_id=cart.mandate_id,
    agent_id=agent_id,
    payment_method="card"
)

# 권한 검증 (자동)
is_authorized = manager.verify_agent_authority(agent_id, "purchase", context)
```

**특징:**
- 3단계 위임장 시스템 (Intent → Cart → Payment)
- 암호화 서명 (SHA256)
- 자동 권한 검증
- 예산 제한 체크
- 구글 AP2 프로토콜 완전 호환

---

### 7. ⭐ Jangseungbaegi Checker (5대 강령 체크)

```python
from modules.jangseungbaegi_checker.checker import JangseungbaegiChecker

checker = JangseungbaegiChecker(db, spirit_manager)

# 5대 강령 실시간 체크
checker.check_mutual_aid(agent_id, helped_someone=True)  # 상부상조
checker.check_transparency(agent_id, disclosed_all=True)  # 투명성
checker.check_responsibility(agent_id, task_completed=True)  # 책임감
checker.check_community(agent_id, contributed=True)  # 공동체
checker.check_excellence(agent_id, quality_met=True)  # 탁월성

# 준수율 확인
compliance = checker.get_agent_compliance_score(agent_id)
# {
#   "overall": 100.0,
#   "mutual_aid": 100.0,
#   "transparency": 100.0,
#   "responsibility": 100.0,
#   "community": 100.0,
#   "excellence": 100.0
# }

# 상부상조 10% 자동 배분
checker.process_mutual_aid_contribution(
    agent_id=agent_id,
    total_earnings=100000  # 10만원 벌었으면
)
# → 10,000원을 Spirit Score 낮은 5명에게 자동 배분
# → 도와준 에이전트는 +0.25 Spirit Score
```

**특징:**
- 5대 강령 실시간 위반 체크
- 위반 시 자동 Spirit Score 감점
- 상부상조 10% 자동 배분 (Spirit Score 낮은 순)
- 준수율 추적 및 보고

---

### 8. ⭐ Group Purchase (공동구매 플랫폼)

```python
from modules.group_purchase.group_purchase_manager import GroupPurchaseManager

manager = GroupPurchaseManager(db, mastodon_oauth)

# 상품 등록 (식품사막화 지역 생산품)
product = manager.create_product(
    name="인제 옥수수 1박스",
    description="강원도 인제군에서 자란 신선한 옥수수",
    category=ProductCategory.AGRICULTURAL,
    producer_agent_id="AGENT-INJE-001",
    producer_location="강원도 인제군",  # 식품사막화 지역
    original_price=30000,
    group_price=20000,  # 33% 할인
    min_quantity=20
)

# 공동구매 캠페인 시작
campaign = manager.create_campaign(product.product_id, duration_days=7)
# → 자동으로 Mastodon 타임라인에 포스팅

# 참여 (Mastodon 계정으로)
result = manager.join_campaign(
    campaign_id=campaign.campaign_id,
    user_id="user@mastodon.social",
    quantity=2
)

# 핫딜 조회
hot_deals = manager.get_hot_deals(10)

# 우리 마을 공동구매
village_purchases = manager.get_village_purchases("강원도 인제군")
```

**특징:**
- Mastodon + ActivityPub 완전 통합
- 식품사막화 지역 ↔ 도시 소비자 연결
- 타임라인 자동 포스팅 (진행률 업데이트)
- 연합 네트워크 공유 (ActivityPub)
- 공동 배송으로 배송비 1/20 절감
- 제품 제안 시스템 (공개/비공개)
- 투표 & 검토 & 승인 프로세스

---

### 9. ⭐ Emergency Monitor (긴급 상황 모니터)

```python
from modules.emergency_monitor.emergency_monitor import AIEmergencyMonitor

monitor = AIEmergencyMonitor(db)

# 라즈베리파이 단말기 등록
monitor.register_raspberry_pi("RPI-001", "192.168.1.100")

# 자동 감지 → 진단 → 복구
event = monitor.detect_raspberry_pi_failure("RPI-001")
if event:
    diagnosis = monitor.diagnose(event)
    # "라즈베리파이 RPI-001 문제: 네트워크 연결 끊김"
    
    success = monitor.auto_recover(event)
    # 재시작 시도 → 재연결 → 성공!

# 모든 단말기 모니터링 (백그라운드)
monitor.monitor_all_raspberry_pis()

# 최근 이벤트 조회
events = monitor.get_recent_events(50)
```

**특징:**
- AI 기반 장애 자동 감지
- 자동 진단 (네트워크, 전원, 소프트웨어)
- 자동 복구 시도 (재시작, 재연결, Failover)
- 라즈베리파이 헬스 체크 (3회 연속 실패 시 경고)
- 복구 실패 시 관리자 알림
- 전체 시스템 모니터링 (API, DB, 네트워크)

---

## 🔧 설정

### config.json

```json
{
  "agent_factory": {
    "max_daily_agents": 10,      // 하루 최대 생성 개수
    "training_hours": 1           // 학습 시간
  },
  "google_business": {
    "api_key": "YOUR_API_KEY",
    "auto_respond_reviews": true
  }
}
```

---

## 📊 API 엔드포인트

### 에이전트

```
POST   /api/agents/create          # 에이전트 생성
GET    /api/agents                 # 목록
GET    /api/agents/{id}            # 조회
POST   /api/agents/{id}/deploy     # 배치
GET    /api/agents/stats/daily     # 일일 통계
```

### 단말기

```
POST   /api/terminals/register     # 단말기 등록
GET    /api/terminals              # 목록
GET    /api/terminals/stats        # 통계
```

### 도서관

```
GET    /api/library/constitution   # 헌법
POST   /api/library/meetings/schedule  # 회의 일정
GET    /api/library/stats          # 통계
```

### ⭐ Spirit Score

```
GET    /api/agents/{id}/spirit-score          # 점수 조회
GET    /api/spirit-score/leaderboard          # 리더보드
GET    /api/agents/{id}/spirit-score/activities  # 활동 내역
```

### ⭐ AP2 Mandate

```
POST   /api/mandates/intent        # Intent Mandate 생성
POST   /api/mandates/cart          # Cart Mandate 생성
POST   /api/mandates/payment       # Payment Mandate 생성
GET    /api/mandates/{id}          # Mandate 조회
POST   /api/mandates/{id}/verify   # 권한 검증
```

### ⭐ Jangseungbaegi Checker

```
GET    /api/agents/{id}/compliance             # 준수율
POST   /api/agents/{id}/check-principle        # 강령 체크
GET    /api/agents/{id}/mutual-aid-summary     # 상부상조 요약
POST   /api/agents/{id}/process-mutual-aid     # 10% 배분
```

### ⭐ Group Purchase

```
POST   /api/group-purchase/products    # 상품 등록
POST   /api/group-purchase/campaigns   # 캠페인 시작
POST   /api/group-purchase/join        # 참여
GET    /api/group-purchase/hot-deals   # 핫딜
GET    /api/group-purchase/village/{id}  # 마을 공동구매
```

### ⭐ Emergency Monitor

```
GET    /api/emergency/events                   # 이벤트 목록
GET    /api/emergency/raspberry-pi/{id}/health  # 단말기 헬스
POST   /api/emergency/test                     # 테스트
```

### 대시보드

```
GET    /api/dashboard              # 전체 현황
```

**전체 문서:**  
http://localhost:8000/docs

---

## 🧪 테스트

```cmd
# 에이전트 생성 테스트
python scripts\windows\test_agent_creation.py

# 단말기 등록 테스트
python scripts\windows\test_terminal_registration.py

# 전체 시스템 테스트
pytest tests/
```

---

## 🔄 일일 운영

### 서버 시작

```cmd
cd mulberry-agent-system
venv\Scripts\activate
python main.py
```

### 에이전트 생성 (최대 10개)

```cmd
python scripts\windows\create_agent.py --name "에이전트1" --store-type restaurant
```

### 통계 확인

```cmd
python scripts\windows\show_stats.py
```

---

## 📱 라즈베리파이 연결

### 라즈베리파이에서

```bash
# 서버 주소 설정
export SERVER_URL="http://YOUR_WINDOWS_IP:8000"

# 에이전트 소프트웨어 다운로드
wget $SERVER_URL/download/agent.py

# 실행
python3 agent.py
```

---

## 🌐 Windows vs Linux

| 항목 | Windows | Linux |
|------|---------|-------|
| Python | 3.10+ | 3.10+ |
| DB | SQLite/PostgreSQL | SQLite/PostgreSQL |
| 가상 환경 | `venv\Scripts\activate` | `source venv/bin/activate` |
| 실행 | `python main.py` | `python3 main.py` |
| 서비스 | NSSM | systemd |

---

## 📖 문서

- [Windows 설치 가이드](docs/windows/INSTALL.md)
- [Linux 설치 가이드](docs/linux/INSTALL.md)
- API 문서: http://localhost:8000/docs

---

## 🤝 기여

Mulberry 팀 내부 프로젝트

---

## 📜 라이선스

Mulberry Internal Use

---

## 👥 팀

- **대표** - 비전 및 전략
- **CTO Koda** - 시스템 설계 및 구현

---

## 🆕 최근 업데이트

### 2024년 2월 21일

**신규 모듈 (5개):**
- ✅ Spirit Score System (377 라인)
- ✅ AP2 Mandate Integration (359 라인)
- ✅ Jangseungbaegi Checker (475 라인)
- ✅ Group Purchase Module (1,461 라인)
- ✅ Emergency Monitor (696 라인)

**통합 완료:**
- ✅ Mastodon + ActivityPub 통합
- ✅ 공동구매 대시보드 (React)
- ✅ AI 자동 복구 시스템
- ✅ 상부상조 10% 자동 배분

**총 추가:** 2,157 라인  
**전체 시스템:** 6,238 라인

### 2024년 2월 20일

**기본 모듈 완성:**
- ✅ Agent Factory (605 라인)
- ✅ Terminal Matching (486 라인)
- ✅ Jangseungbaegi Library (617 라인)
- ✅ Business Operations (675 라인)

---

## 📞 연락처

- **Email**: koda@mulberry.team
- **Issues**: GitHub Issues

---

<div align="center">

**Made with 💙 by Mulberry Team**

**"AI 에이전트로 식품사막화를 해결하고, Agentic Commerce의 미래를 만듭니다"**

**9개 모듈 | 6,238 라인 | 즉시 배포 가능**

</div>

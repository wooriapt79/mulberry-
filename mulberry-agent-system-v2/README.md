      Mulberry Agent System 
# 🌾 Mulberry Agent System v2

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Lines](https://img.shields.io/badge/Lines-4.8K-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

Complete Integration: AP2 + Spirit Score + Jangseungbaegi

**AI 에이전트 기반 오프라인 매장 자동화 시스템**

**CTO Koda**  
**2024년 2월 20일**

---

## 📋 개요

Mulberry Agent System은 AI 에이전트를 생성하고 라즈베리파이 단말기와 연결하여 오프라인 매장을 자동화하는 시스템입니다.

### 핵심 기능

- ✅ **AI 에이전트 자동 생성** (하루 10개 기본, 설정 가능)
- ✅ **장승배기 헌법 1시간 학습** (자동화)
- ✅ **라즈베리파이 1:1 매칭** (가게 종류별 설정)
- ✅ **장승배기 도서관** (헌법, 회의, 업무 지시)
- ✅ **다채널 고객 응대** (ARS, 구글 마이 비즈니스)
- ✅ **Windows/Linux 지원**

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
├── main.py                              # 메인 서버
├── requirements.txt                     # Python 의존성
├── config/
│   └── config.example.json             # 설정 예시
├── modules/
│   ├── agent_factory/                  # 에이전트 생성
│   │   └── agent_factory.py
│   ├── terminal_matching/              # 단말기 매칭
│   │   └── terminal_matching.py
│   ├── jangseungbaegi_library/         # 도서관
│   │   └── library.py
│   └── business_operations/            # 업무 운영
│       └── operations.py
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

## 📞 연락처

- **Email**: koda@mulberry.team
- **Issues**: GitHub Issues

---

<div align="center">

**Made with 💙 by Mulberry Team**

**"AI 에이전트로 모든 가게를 스마트하게"**

</div>

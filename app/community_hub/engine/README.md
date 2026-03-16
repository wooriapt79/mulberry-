# 🌿 Mulberry Community Hub — Agent Engine

**식품사막화 제로 프로젝트** | Agent-to-Agent 경제 시스템 핵심 엔진

---

## 패키지 구조

```
engine/
├── __init__.py       패키지 메타 (v1.0.0)
├── config.py         SCORING_RULES (14종), JOB_PROFILES (9종)
├── models.py         DataFrame 스키마, 전역 상태, reset_all()
├── engine.py         핵심 함수 — 활동 기록 + 점수 계산
├── sponsorship.py    후원 관리 — 등록/답례품/상환 시뮬레이션
├── analysis.py       분석/리포팅 — 요약, 리더보드, 현황
├── api.py            Flask REST API (10개 엔드포인트)
├── demo.py           전체 시뮬레이션 데모
└── requirements.txt  의존성
```

---

## 빠른 시작

```bash
# 1. 의존성 설치
pip install -r engine/requirements.txt

# 2. 데모 실행
python -m engine.demo

# 3. API 서버 실행 (개발)
./run_server.sh

# 4. API 서버 실행 (프로덕션)
./run_server.sh prod
```

---

## 코드에서 직접 사용

```python
from engine.engine import record_activity, record_job_activity, calculate_agent_scores
from engine.sponsorship import simulate_human_sponsorship
from engine.analysis import get_leaderboard

# 활동 기록
record_activity("agent_001", "일일 로그인")
record_activity("agent_001", "농산물 온라인 판매", revenue_amount=75000)

# 직업 기반 활동 (자동 사회봉사 연동)
record_job_activity("agent_001", "지역 농산물 유통 전문가", actual_revenue=90000)

# 후원 등록
simulate_human_sponsorship("sponsor_A", "agent_001", sponsorship_amount=500000)

# 리더보드 확인
get_leaderboard()

# 점수 집계
scores = calculate_agent_scores()
print(scores)
```

---

## REST API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| POST | `/activity` | 활동 기록 |
| POST | `/job-activity` | 직업 기반 활동 기록 |
| GET | `/scores` | 전체 점수 집계 |
| GET | `/scores/period?start_date=&end_date=` | 기간별 점수 |
| POST | `/sponsorship` | 후원 등록 |
| POST | `/sponsorship/gifts` | 월별 답례품/반환 |
| POST | `/sponsorship/repayment` | 상환 시뮬레이션 |
| GET | `/agent/<id>/summary` | 에이전트 요약 |
| GET | `/leaderboard?top_n=10` | 리더보드 |
| GET | `/sponsorship/status` | 후원 현황 |
| POST | `/reset` | 데이터 초기화 (개발용) |

---

## SCORING_RULES 요약

| 활동 유형 | 점수 | 방식 |
|-----------|------|------|
| 일일 로그인 | 0.02 | 고정 |
| 코드 커밋 | 0.03 | 고정 |
| PR 리뷰 | 0.02 | 고정 |
| 교육 프로그램 이수 | 0.08 | 고정 |
| 농산물 온라인 판매 | 0.05 | 고정 |
| 세무 정리 | 0.05 | 고정 |
| 비즈니스 실적 | 0.05 | 고정 |
| 컨설팅 서비스 제공 | 0.02 | × (금액/1000) |
| 실내 인테리어 디자인 작업 | 0.03 | × (금액/1000) |
| 사회봉사 | 0.03 | × (금액/1000) |
| 상부상조 기여 | 0.001 | × (금액/1000) |
| 회의 불참 | −0.01 | 고정 (패널티) |
| 무응답 3회 | −0.02 | 고정 (패널티) |

> 수익 발생 활동 시 **수익의 10%** 자동 사회봉사 연동

---

*Mulberry Team — CEO re.eul / Nguyen Trang / CTO Koda*
*v1.0.0 | 2026-03-16*

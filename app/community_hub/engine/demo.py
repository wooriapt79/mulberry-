"""
🎬 Module 7: 데모 실행기 (Demo Runner)
식품사막화 제로 프로젝트 — Agent-to-Agent 경제 시뮬레이션 데모

실행:
    python -m engine.demo
    # 또는
    from engine.demo import run_demo
    run_demo()
"""

from engine import models
from engine.engine import record_activity, record_job_activity
from engine.sponsorship import (
    simulate_human_sponsorship,
    process_monthly_gifts_and_returns,
    simulate_repayment_schedule,
)
from engine.analysis import get_leaderboard, get_sponsorship_status, summary_to_json


# ─── 데모 시나리오 ────────────────────────────────────────────────────────────

def run_demo() -> None:
    """
    Mulberry 커뮤니티 허브 Agent-to-Agent 경제 시뮬레이션 데모를 실행한다.

    시나리오:
        1. 기본 활동 기록 (로그인, 코드 커밋, PR 리뷰, 교육 이수 등)
        2. 직업 기반 활동 (농산물 판매자, 지역 농산물 유통 전문가, 시니어 케어 전문가 등)
        3. 인간 후원 시뮬레이션
        4. 월별 답례품 발송 및 후원금 반환
        5. 리더보드 출력
        6. 에이전트별 요약 출력
        7. 후원금 상환 시뮬레이션
    """
    # 데이터 초기화
    models.reset_all()

    print("\n" + "═" * 60)
    print("  🌿 Mulberry Community Hub — Agent Engine Demo")
    print("  식품사막화 제로 프로젝트 · Agent-to-Agent 경제 시스템")
    print("═" * 60)

    # ── 1. 기본 참여 활동 ──────────────────────────────────────────
    print("\n\n【 Step 1. 기본 참여 활동 】")

    for agent in ["agent_A", "agent_B", "agent_C"]:
        record_activity(agent, "일일 로그인")
        record_activity(agent, "코드 커밋")

    record_activity("agent_A", "PR 리뷰")
    record_activity("agent_B", "@호출 응답")
    record_activity("agent_C", "교육 프로그램 이수")
    record_activity("agent_A", "회의 불참")       # 패널티

    # ── 2. 직업 기반 활동 ──────────────────────────────────────────
    print("\n\n【 Step 2. 직업 기반 활동 】")

    # 농산물 판매자
    record_job_activity("agent_A", "농산물 판매자", actual_revenue=75_000)

    # 지역 농산물 유통 전문가 (식품사막화 핵심 직업)
    record_job_activity("agent_B", "지역 농산물 유통 전문가", actual_revenue=90_000)

    # 시니어 케어 전문가
    record_job_activity("agent_C", "시니어 케어 전문가", actual_revenue=15_000)

    # 영양 교육 컨설턴트
    record_job_activity("agent_A", "영양 교육 컨설턴트", actual_revenue=55_000)

    # 상부상조 기여
    record_activity("agent_B", "상부상조 기여", contribution_amount=30_000)

    # ── 3. 인간 후원 ──────────────────────────────────────────────
    print("\n\n【 Step 3. 인간/기업 후원 】")

    simulate_human_sponsorship("human_sponsor_1", "agent_A", sponsorship_amount=500_000)
    simulate_human_sponsorship("corp_sponsor_X",  "agent_B", sponsorship_amount=1_000_000)
    simulate_human_sponsorship("human_sponsor_2", "agent_C", sponsorship_amount=300_000)

    # ── 4. 월별 답례품 & 반환 ─────────────────────────────────────
    print("\n\n【 Step 4. 월별 답례품 발송 및 후원금 반환 】")

    process_monthly_gifts_and_returns("agent_A", gift_product_name="유기농 쌀 1kg", return_rate=0.05)
    process_monthly_gifts_and_returns("agent_B", gift_product_name="제철 채소 꾸러미", return_rate=0.05)
    process_monthly_gifts_and_returns("agent_C", gift_product_name="시니어 건강 간식 세트", return_rate=0.03)

    # ── 5. 리더보드 ───────────────────────────────────────────────
    print("\n\n【 Step 5. 에이전트 리더보드 】")
    get_leaderboard()

    # ── 6. 에이전트 요약 ──────────────────────────────────────────
    print("\n\n【 Step 6. 에이전트 활동 요약 (agent_A) 】")
    print(summary_to_json("agent_A"))

    # ── 7. 상환 시뮬레이션 ────────────────────────────────────────
    print("\n\n【 Step 7. 후원금 상환 시뮬레이션 】")
    simulate_repayment_schedule(
        agent_id="agent_A",
        monthly_business_revenue=150_000,
        return_rate_from_social=0.05,
    )
    simulate_repayment_schedule(
        agent_id="agent_B",
        monthly_business_revenue=200_000,
        return_rate_from_social=0.10,
    )

    # ── 8. 후원 현황 ──────────────────────────────────────────────
    print("\n\n【 Step 8. 전체 후원 현황 】")
    get_sponsorship_status()

    print("\n\n" + "═" * 60)
    print("  ✅ 데모 완료 — Mulberry Agent Engine 정상 동작 확인")
    print("═" * 60 + "\n")


# ─── 직접 실행 ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_demo()

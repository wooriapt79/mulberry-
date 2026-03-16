"""
💰 Module 4: 후원 관리 (Sponsorship Management)
- simulate_human_sponsorship: 인간/기업 후원 시뮬레이션
- process_monthly_gifts_and_returns: 월별 답례품 발송 및 후원금 반환 처리
- simulate_repayment_schedule: 후원금 상환 일정 시뮬레이션
"""

import pandas as pd
from datetime import datetime

from engine import models
from engine.engine import record_activity


# ─── 후원 등록 ────────────────────────────────────────────────────────────────

def simulate_human_sponsorship(
    sponsor_id: str,
    agent_id: str,
    sponsorship_amount: float,
) -> None:
    """
    인간/기업이 에이전트를 후원한다.

    후원금은 '비즈니스 실적'으로 기록되며,
    이를 통해 수익의 10% 가 자동으로 '사회봉사'로 연동된다.

    Args:
        sponsor_id: 후원자 ID (인간 또는 기업)
        agent_id:   후원 대상 에이전트 ID
        sponsorship_amount: 후원 금액 (원)
    """
    current_time = datetime.now()
    print(f"\n🤝 후원 이벤트: {sponsor_id} → {agent_id} ({sponsorship_amount:,.0f}원)")

    # 비즈니스 실적으로 기록 (사회봉사 자동 연동 포함)
    record_activity(
        agent_id=agent_id,
        activity_type="비즈니스 실적",
        details=f"{sponsor_id}의 후원으로 비즈니스 실적 달성: {sponsorship_amount:,.0f}원",
        revenue_amount=sponsorship_amount,
    )

    # 후원 추적 DataFrame 에 등록
    new_row = pd.DataFrame([{
        "sponsor_id":           sponsor_id,
        "agent_id":             agent_id,
        "original_amount":      sponsorship_amount,
        "amount_returned":      0,
        "status":               "active",
        "last_gift_date":       None,
        "sponsorship_start_date": current_time,
    }])
    models.sponsorships_df = pd.concat([models.sponsorships_df, new_row], ignore_index=True)
    print(f"   ✅ 후원 등록 완료: {agent_id} 점수 반영 + 후원 내역 추적 시작")


# ─── 월별 답례품 및 반환 처리 ─────────────────────────────────────────────────

def process_monthly_gifts_and_returns(
    agent_id: str,
    gift_product_name: str,
    return_rate: float = 0.05,
) -> None:
    """
    에이전트의 활성 후원자에게 월별 답례품을 발송하고
    후원금 일부를 반환 처리한다.

    Args:
        agent_id:         에이전트 ID
        gift_product_name: 답례품 이름 (예: "유기농 쌀 1kg")
        return_rate:      사회봉사 기여금 중 후원금 반환 비율 (기본값 5%)
    """
    current_time = datetime.now()
    print(f"\n🎁 월별 답례품/반환 처리: {agent_id}")

    active = models.sponsorships_df[
        (models.sponsorships_df["agent_id"] == agent_id) &
        (models.sponsorships_df["status"] == "active")
    ]

    if active.empty:
        print(f"   ℹ️  {agent_id} 의 활성 후원 없음")
        return

    for idx, row in active.iterrows():
        sponsor_id      = row["sponsor_id"]
        original_amount = row["original_amount"]
        amount_returned = row["amount_returned"]
        last_gift       = row["last_gift_date"]

        # ── 월별 답례품 발송 ──
        days_since_gift = (current_time - last_gift).days if pd.notna(last_gift) else 31
        if days_since_gift >= 30:
            print(f"   → {agent_id} 가 후원자 {sponsor_id} 에게 '{gift_product_name}' 발송")
            models.sponsorships_df.loc[idx, "last_gift_date"] = current_time

        # ── 후원금 반환 계산 ──
        # 에이전트 사회봉사 기여 내역에서 반환 금액 산출
        social_activities = models.activities_df[
            (models.activities_df["agent_id"] == agent_id) &
            (models.activities_df["activity_type"] == "사회봉사")
        ]
        total_social_contribution = (
            social_activities["score_impact"].sum() / 0.03 * 1000
            if not social_activities.empty else 0
        )
        return_amount = total_social_contribution * return_rate

        if return_amount > 0:
            new_returned = amount_returned + return_amount
            models.sponsorships_df.loc[idx, "amount_returned"] = new_returned
            print(f"   → 후원금 반환: {return_amount:,.0f}원 처리 (누적: {new_returned:,.0f}원 / 원금: {original_amount:,.0f}원)")

            # 원금 전액 반환 시 완료 처리
            if new_returned >= original_amount:
                models.sponsorships_df.loc[idx, "status"] = "completed"
                print(f"   🎉 [{agent_id}] {sponsor_id} 후원금 전액 반환 완료!")


# ─── 상환 일정 시뮬레이션 ─────────────────────────────────────────────────────

def simulate_repayment_schedule(
    agent_id: str,
    monthly_business_revenue: float,
    return_rate_from_social: float,
) -> None:
    """
    에이전트의 미반환 후원금 상환 예상 일정을 시뮬레이션한다.

    계산 방식:
        월 사회봉사 기여 = monthly_business_revenue × 10%
        월 상환액 = 월 사회봉사 기여 × return_rate_from_social

    Args:
        agent_id:               에이전트 ID
        monthly_business_revenue: 월 예상 비즈니스 수익 (원)
        return_rate_from_social: 사회봉사 기여금 중 상환 비율 (예: 0.05 = 5%)
    """
    print(f"\n📊 상환 시뮬레이션: {agent_id}")
    print(f"   월 예상 수익: {monthly_business_revenue:,.0f}원")
    print(f"   사회봉사→상환 비율: {return_rate_from_social:.1%}")

    agent_sponsorships = models.sponsorships_df[
        models.sponsorships_df["agent_id"] == agent_id
    ]

    if agent_sponsorships.empty:
        print(f"   ℹ️  {agent_id} 의 후원 내역 없음")
        return

    total_unreturned = (
        agent_sponsorships["original_amount"].sum()
        - agent_sponsorships["amount_returned"].sum()
    )

    if total_unreturned <= 0:
        print(f"   ✅ {agent_id} 는 미반환 후원금이 없습니다")
        return

    print(f"   미반환 총액: {total_unreturned:,.0f}원")

    monthly_social = monthly_business_revenue * 0.10
    monthly_repayment = monthly_social * return_rate_from_social

    if monthly_repayment <= 0:
        print("   ⚠️  월 상환액이 0 이하입니다 — 시뮬레이션 불가")
        return

    remaining = total_unreturned
    months = 0
    MAX_MONTHS = 1200  # 100년 안전 상한

    while remaining > 0 and months < MAX_MONTHS:
        remaining -= monthly_repayment
        months += 1

    print(f"   월 사회봉사 기여: {monthly_social:,.0f}원")
    print(f"   월 상환액:       {monthly_repayment:,.0f}원")

    if remaining <= 0:
        years, mos = divmod(months, 12)
        duration = f"{years}년 {mos}개월" if years else f"{mos}개월"
        print(f"   🏁 예상 완전 상환 기간: {duration} ({months}개월)")
    else:
        print(f"   ⚠️  {MAX_MONTHS}개월 후에도 {remaining:,.0f}원 잔여 예상")

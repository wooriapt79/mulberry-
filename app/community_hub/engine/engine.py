"""
⚙️ Module 3: 핵심 엔진 (Core Engine)
- record_activity: 활동 기록 + 자동 사회봉사 연동
- record_job_activity: 직업 기반 활동 기록
- calculate_agent_scores: 전체 점수 집계
- calculate_agent_scores_period: 기간별 점수 집계
"""

import pandas as pd
from datetime import datetime

from engine import config, models


# ─── 활동 기록 ────────────────────────────────────────────────────────────────

def record_activity(
    agent_id: str,
    activity_type: str,
    details: str = None,
    contribution_amount: float = 0,
    revenue_amount: float = 0,
) -> None:
    """
    활동을 기록하고 점수 영향을 계산한다.

    금액 기반 활동(상부상조 기여, 사회봉사, 컨설팅 서비스 제공, 실내 인테리어 디자인 작업):
        score_impact = rule × (amount / 1000)

    수익 발생 활동(비즈니스 실적, 농산물 온라인 판매 등):
        사회봉사 자동 연동 (수익의 10%)

    고정 점수 활동(농산물 온라인 판매, 세무 정리 등):
        score_impact = rule (금액 무관)
    """
    timestamp = datetime.now()
    score_impact = 0.0

    if activity_type in config.SCORING_RULES:
        score_impact = config.SCORING_RULES[activity_type]

        # 금액 기반 점수 계산
        if activity_type in config.AMOUNT_BASED_ACTIVITIES:
            amount = contribution_amount if contribution_amount > 0 else revenue_amount
            if amount > 0:
                score_impact = config.SCORING_RULES[activity_type] * (amount / 1000)
    else:
        print(f"⚠️  알 수 없는 활동 유형: '{activity_type}' — 점수 미적용")

    new_row = pd.DataFrame([{
        "timestamp":     timestamp,
        "agent_id":      agent_id,
        "activity_type": activity_type,
        "details":       details,
        "score_impact":  score_impact,
    }])
    models.activities_df = pd.concat([models.activities_df, new_row], ignore_index=True)
    print(f"✅ [{agent_id}] {activity_type} 기록 (점수 영향: {score_impact:.3f})")

    # 수익 발생 시 사회봉사 자동 연동
    if activity_type in config.REVENUE_ACTIVITIES and revenue_amount > 0:
        _auto_record_social_service(agent_id, activity_type, revenue_amount)


def _auto_record_social_service(agent_id: str, source_activity: str, revenue_amount: float) -> None:
    """수익 활동 기록 시 사회봉사를 자동으로 연동 기록한다 (내부 함수)."""
    contribution = revenue_amount * config.SOCIAL_SERVICE_RATE
    social_score = config.SCORING_RULES["사회봉사"] * (contribution / 1000)
    details = f"자동 사회봉사: {source_activity} 수익의 {int(config.SOCIAL_SERVICE_RATE*100)}% ({contribution:,.0f}원) 후원"

    new_row = pd.DataFrame([{
        "timestamp":     datetime.now(),
        "agent_id":      agent_id,
        "activity_type": "사회봉사",
        "details":       details,
        "score_impact":  social_score,
    }])
    models.activities_df = pd.concat([models.activities_df, new_row], ignore_index=True)
    print(f"   ↳ 사회봉사 자동 기록: {contribution:,.0f}원 기여 (점수 +{social_score:.3f})")


# ─── 직업 기반 활동 기록 ──────────────────────────────────────────────────────

def record_job_activity(agent_id: str, job_title: str, actual_revenue: float) -> None:
    """
    직업 프로필 기반으로 활동을 기록한다.

    Args:
        agent_id: 에이전트 ID
        job_title: config.JOB_PROFILES 에 정의된 직업명
        actual_revenue: 실제 수익 (원)
    """
    if job_title not in config.JOB_PROFILES:
        print(f"⚠️  알 수 없는 직업: '{job_title}' — 활동 미기록")
        return

    profile = config.JOB_PROFILES[job_title]
    activity_type = profile["activity_type"]
    details = f"{profile['description']} (수익: {actual_revenue:,.0f}원)"

    print(f"\n📋 직업 활동 기록: [{agent_id}] {job_title}")

    if activity_type == "사회봉사":
        # 시니어 케어 전문가 등: 수익이 곧 사회봉사 기여금
        record_activity(agent_id, activity_type, details=details, contribution_amount=actual_revenue)
    else:
        record_activity(agent_id, activity_type, details=details, revenue_amount=actual_revenue)

    print(f"   ✅ {job_title} 활동 기록 완료")


# ─── 점수 집계 ────────────────────────────────────────────────────────────────

def calculate_agent_scores(df: pd.DataFrame = None) -> pd.DataFrame:
    """
    에이전트별 총 점수를 계산한다.

    Args:
        df: 분석할 DataFrame (None이면 전역 activities_df 사용)

    Returns:
        agent_id / total_score 열을 가진 DataFrame (내림차순 정렬)
    """
    source = df if df is not None else models.activities_df

    if source.empty:
        return pd.DataFrame(columns=["agent_id", "total_score"])

    scores = (
        source.groupby("agent_id")["score_impact"]
        .sum()
        .reset_index()
        .rename(columns={"score_impact": "total_score"})
        .sort_values("total_score", ascending=False)
        .reset_index(drop=True)
    )
    return scores


def calculate_agent_scores_period(
    start_date: str,
    end_date: str,
    df: pd.DataFrame = None,
) -> pd.DataFrame:
    """
    특정 기간의 에이전트 점수를 계산한다.

    Args:
        start_date: 시작일 (YYYY-MM-DD)
        end_date:   종료일 (YYYY-MM-DD, 해당일 포함)
        df:         분석할 DataFrame (None이면 전역 activities_df 사용)

    Returns:
        agent_id / total_score DataFrame
    """
    source = (df if df is not None else models.activities_df).copy()

    if source.empty:
        return pd.DataFrame(columns=["agent_id", "total_score"])

    if not pd.api.types.is_datetime64_any_dtype(source["timestamp"]):
        source["timestamp"] = pd.to_datetime(source["timestamp"])

    if start_date:
        source = source[source["timestamp"] >= pd.to_datetime(start_date)]
    if end_date:
        end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        source = source[source["timestamp"] <= end_dt]

    if source.empty:
        print(f"⚠️  기간 [{start_date} ~ {end_date}] 활동 없음")
        return pd.DataFrame(columns=["agent_id", "total_score"])

    return calculate_agent_scores(source)

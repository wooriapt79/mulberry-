"""
📊 Module 5: 분석 & 리포팅 (Analysis & Reporting)
- get_agent_activity_summary: 에이전트별 종합 활동 요약
- get_leaderboard: 점수 순위표 출력
- get_sponsorship_status: 후원 현황 요약
"""

import json
import pandas as pd

from engine import models
from engine.engine import calculate_agent_scores


# ─── 에이전트 활동 요약 ────────────────────────────────────────────────────────

def get_agent_activity_summary(agent_id: str, df: pd.DataFrame = None) -> dict:
    """
    특정 에이전트의 종합 활동 요약을 반환한다.

    Returns:
        {
          "agent_id": str,
          "total_score": float,
          "activity_breakdown": [{"activity_type": str, "total_score_for_type": float}, ...],
          "detailed_activities": [{"timestamp": str, "activity_type": str, "details": str, "score_impact": float}, ...],
        }
    """
    source = df if df is not None else models.activities_df
    agent_df = source[source["agent_id"] == agent_id]

    summary: dict = {"agent_id": agent_id}

    # 총 점수
    scores = calculate_agent_scores(agent_df)
    summary["total_score"] = float(scores["total_score"].iloc[0]) if not scores.empty else 0.0

    # 활동 유형별 점수 합계
    breakdown = (
        agent_df.groupby("activity_type")["score_impact"]
        .sum()
        .reset_index()
        .rename(columns={"score_impact": "total_score_for_type"})
    )
    summary["activity_breakdown"] = breakdown.to_dict(orient="records")

    # 상세 활동 내역 (timestamp → ISO string)
    detail_df = agent_df[["timestamp", "activity_type", "details", "score_impact"]].copy()
    detail_df["timestamp"] = pd.to_datetime(detail_df["timestamp"]).apply(
        lambda x: x.isoformat()
    )
    summary["detailed_activities"] = detail_df.to_dict(orient="records")

    return summary


# ─── 리더보드 ──────────────────────────────────────────────────────────────────

def get_leaderboard(df: pd.DataFrame = None, top_n: int = 10) -> pd.DataFrame:
    """
    상위 N명의 에이전트 점수 순위표를 반환한다.

    Args:
        df:    분석할 DataFrame (None이면 전역 activities_df 사용)
        top_n: 표시할 상위 인원 수 (기본값 10)

    Returns:
        rank / agent_id / total_score DataFrame
    """
    scores = calculate_agent_scores(df)

    if scores.empty:
        print("⚠️  집계할 활동 데이터가 없습니다")
        return scores

    board = scores.head(top_n).reset_index(drop=True)
    board.index = board.index + 1
    board.index.name = "rank"

    print(f"\n🏆 에이전트 리더보드 (Top {min(top_n, len(board))})")
    print("─" * 40)
    for rank, row in board.iterrows():
        print(f"  {rank:2}위  {row['agent_id']:<20} {row['total_score']:.3f}점")
    print("─" * 40)

    return board.reset_index()


# ─── 후원 현황 ─────────────────────────────────────────────────────────────────

def get_sponsorship_status(agent_id: str = None) -> pd.DataFrame:
    """
    후원 현황을 요약한다.

    Args:
        agent_id: 특정 에이전트 ID (None이면 전체)

    Returns:
        후원 상태가 포함된 DataFrame
    """
    df = models.sponsorships_df.copy()

    if agent_id:
        df = df[df["agent_id"] == agent_id]

    if df.empty:
        print("ℹ️  후원 내역 없음")
        return df

    df["original_amount"]  = pd.to_numeric(df["original_amount"],  errors="coerce").fillna(0)
    df["amount_returned"]  = pd.to_numeric(df["amount_returned"],  errors="coerce").fillna(0)
    df["remaining"] = df["original_amount"] - df["amount_returned"]
    df["return_pct"] = (df["amount_returned"] / df["original_amount"].replace(0, float("nan")) * 100).round(1).fillna(0)

    print(f"\n💳 후원 현황{'(' + agent_id + ')' if agent_id else ' (전체)'}")
    print("─" * 60)
    for _, row in df.iterrows():
        status_icon = "✅" if row["status"] == "completed" else "🔄"
        print(
            f"  {status_icon} {row['sponsor_id']} → {row['agent_id']} | "
            f"원금: {row['original_amount']:,.0f}원 | "
            f"반환: {row['return_pct']}% | "
            f"잔여: {row['remaining']:,.0f}원"
        )
    print("─" * 60)

    return df


# ─── JSON 직렬화 헬퍼 ─────────────────────────────────────────────────────────

def summary_to_json(agent_id: str, df: pd.DataFrame = None, indent: int = 2) -> str:
    """에이전트 요약을 JSON 문자열로 반환한다 (Control Tower UI 연동용)."""
    summary = get_agent_activity_summary(agent_id, df)
    return json.dumps(summary, ensure_ascii=False, indent=indent)

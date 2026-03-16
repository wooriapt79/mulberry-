"""
🗄️ Module 2: 데이터 모델 (Data Models)
- DataFrame 스키마 정의
- 초기화 함수
"""

import pandas as pd


# ─── DataFrame 스키마 ────────────────────────────────────────────────

ACTIVITIES_COLUMNS = ["timestamp", "agent_id", "activity_type", "details", "score_impact"]

SPONSORSHIPS_COLUMNS = [
    "sponsor_id", "agent_id", "original_amount", "amount_returned",
    "status", "last_gift_date", "sponsorship_start_date",
]


def make_activities_df() -> pd.DataFrame:
    """빈 activities DataFrame 반환"""
    return pd.DataFrame(columns=ACTIVITIES_COLUMNS)


def make_sponsorships_df() -> pd.DataFrame:
    """빈 sponsorships DataFrame 반환"""
    return pd.DataFrame(columns=SPONSORSHIPS_COLUMNS)


# ─── 전역 상태 (런타임 공유용) ───────────────────────────────────────
# 직접 import해서 사용: from engine.models import activities_df

activities_df   = make_activities_df()
sponsorships_df = make_sponsorships_df()


def reset_all():
    """모든 데이터를 초기화 (테스트/재시작용)"""
    global activities_df, sponsorships_df
    activities_df   = make_activities_df()
    sponsorships_df = make_sponsorships_df()
    print("✅ 모든 데이터 초기화 완료")

"""
intent_router.py — 질문 의도 → kakao-posts 카테고리 매핑
Issue #12 | Luna RAG 연동 Step 3

luna_event.intent 필드 값 기준으로 참조할 폴더를 결정합니다.
"""

from typing import List, Optional

# intent → category 매핑 테이블
# luna_event_v1_1.schema.json의 intent 필드 값과 연동
INTENT_CATEGORY_MAP: dict[str, str] = {
    # 공동구매
    "coop_request":       "coop-buy",
    "product_inquiry":    "coop-buy",
    "price_inquiry":      "coop-buy",
    "purchase_request":   "coop-buy",
    # 이벤트·행사
    "event_inquiry":      "events",
    "schedule_inquiry":   "events",
    "festival_inquiry":   "events",
    # 공지
    "notice_inquiry":     "notices",
    "service_inquiry":    "notices",
    "update_inquiry":     "notices",
    # 생산자
    "producer_inquiry":   "producers",
    "farm_inquiry":       "producers",
}

# 키워드 기반 fallback 매핑 (intent가 null이거나 미매핑 시)
KEYWORD_CATEGORY_MAP: list[tuple[list[str], str]] = [
    (["공동구매", "구매", "가격", "할인", "신청", "주문", "얼마"], "coop-buy"),
    (["이벤트", "행사", "페스티벌", "언제", "일정", "체험"],      "events"),
    (["공지", "업데이트", "변경", "서비스", "안내"],              "notices"),
    (["생산자", "농부", "농장", "어디서", "누가"],                "producers"),
]


def resolve_category(intent: Optional[str], user_text: Optional[str] = None) -> Optional[str]:
    """
    intent 값 또는 user_text 키워드로 참조할 카테고리 결정.
    매핑 실패 시 None 반환 (전체 카테고리 검색 fallback).
    """
    if intent and intent in INTENT_CATEGORY_MAP:
        return INTENT_CATEGORY_MAP[intent]

    if user_text:
        text_lower = user_text.lower()
        for keywords, category in KEYWORD_CATEGORY_MAP:
            if any(kw in text_lower for kw in keywords):
                return category

    return None


def resolve_categories(intent: Optional[str], user_text: Optional[str] = None) -> List[str]:
    """
    단일 카테고리 또는 전체 카테고리 목록 반환.
    매핑 실패 시 모든 카테고리 반환 (넓게 검색).
    """
    from luna.rag.kakao_posts_fetcher import CATEGORIES
    cat = resolve_category(intent, user_text)
    if cat:
        return [cat]
    return list(CATEGORIES)

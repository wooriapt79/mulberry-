"""
prompt_injector.py — Luna 프롬프트에 kakao-posts 참조 데이터 삽입
Issue #12 | Luna RAG 연동 Step 4

동작:
  1. intent_router로 카테고리 결정
  2. 캐시에서 해당 카테고리 포스팅 조회
  3. 최신 N개 포스팅 summary를 시스템 프롬프트에 삽입
  4. Luna가 자연스럽게 최신 소식을 참조해 답변
"""

from typing import Optional
from luna.rag.kakao_posts_fetcher import get_cache, auto_refresh_if_stale
from luna.rag.intent_router import resolve_categories

MAX_POSTS_PER_CATEGORY = 3
MAX_CONTEXT_CHARS = 1500


def build_rag_context(intent: Optional[str], user_text: Optional[str] = None) -> str:
    """
    사용자 의도에 맞는 최신 포스팅 요약을 RAG 컨텍스트 문자열로 반환.
    Luna 시스템 프롬프트 끝에 삽입하여 사용.
    """
    auto_refresh_if_stale()
    cache = get_cache()
    categories = resolve_categories(intent, user_text)

    sections = []
    total_chars = 0

    for cat in categories:
        posts = cache.get(cat)
        if not posts:
            continue

        # 최신순 정렬 (date 기준)
        sorted_posts = sorted(posts, key=lambda p: p.get("date", ""), reverse=True)
        selected = [p for p in sorted_posts if p.get("status") in ("active", "upcoming", "published")]
        selected = selected[:MAX_POSTS_PER_CATEGORY]

        if not selected:
            continue

        cat_label = {
            "coop-buy":  "공동구매 안내",
            "events":    "이벤트·행사",
            "notices":   "서비스 공지",
            "producers": "생산자 소개",
        }.get(cat, cat)

        lines = [f"[{cat_label}]"]
        for post in selected:
            title = post.get("title", "")
            summary = post.get("summary", post.get("content", "")[:200])
            date = post.get("date", "")
            lines.append(f"- ({date}) {title}: {summary}")

        section = "\n".join(lines)
        if total_chars + len(section) > MAX_CONTEXT_CHARS:
            break

        sections.append(section)
        total_chars += len(section)

    if not sections:
        return ""

    last_updated = cache.last_updated() or "알 수 없음"
    header = f"[Mulberry 최신 소식 — {last_updated[:10]} 기준]\n"
    return header + "\n\n".join(sections)


def inject_into_system_prompt(base_prompt: str, intent: Optional[str], user_text: Optional[str] = None) -> str:
    """
    기존 Luna 시스템 프롬프트에 RAG 컨텍스트 추가.
    컨텍스트가 없으면 원본 프롬프트 그대로 반환.
    """
    rag_context = build_rag_context(intent, user_text)
    if not rag_context:
        return base_prompt
    return f"{base_prompt}\n\n---\n{rag_context}\n---"


# 테스트 시나리오 5개
TEST_SCENARIOS = [
    {"intent": "coop_request",   "text": "이번 주 공동구매 있어요?",      "expect_cat": "coop-buy"},
    {"intent": "event_inquiry",  "text": "이벤트 언제예요?",              "expect_cat": "events"},
    {"intent": "notice_inquiry", "text": "서비스 업데이트 뭐가 있나요?",   "expect_cat": "notices"},
    {"intent": "producer_inquiry","text": "농부님 누구예요?",              "expect_cat": "producers"},
    {"intent": None,             "text": "블루베리 가격이 얼마예요?",      "expect_cat": "coop-buy"},
]

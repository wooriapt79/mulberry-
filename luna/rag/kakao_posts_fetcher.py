"""
kakao_posts_fetcher.py — GitHub data/kakao-posts/ 데이터 fetch + 캐시 관리
Issue #12 | Luna RAG 연동 Step 2

동작:
  - Railway 서버 시작 시 1회 fetch (warm-up)
  - 6시간마다 자동 fetch (cron)
  - /refresh 엔드포인트로 온디맨드 fetch 지원
"""

import json
import os
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com/repos/wooriapt79/mulberry-/contents/data/kakao-posts"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
CACHE_TTL_SECONDS = 6 * 60 * 60  # 6시간

CATEGORIES = ["coop-buy", "events", "notices", "producers"]


class KakaoPostsCache:
    def __init__(self):
        self._data: Dict[str, List[dict]] = {cat: [] for cat in CATEGORIES}
        self._last_fetched: Optional[float] = None
        self._fetching = False

    def is_stale(self) -> bool:
        if self._last_fetched is None:
            return True
        return (time.time() - self._last_fetched) > CACHE_TTL_SECONDS

    def get(self, category: str) -> List[dict]:
        return self._data.get(category, [])

    def get_all(self) -> Dict[str, List[dict]]:
        return dict(self._data)

    def refresh(self) -> bool:
        if self._fetching:
            return False
        self._fetching = True
        try:
            new_data = _fetch_all_categories()
            self._data = new_data
            self._last_fetched = time.time()
            total = sum(len(v) for v in new_data.values())
            logger.info(f"[KakaoPostsCache] fetch 완료 — 총 {total}개 포스팅")
            return True
        except Exception as e:
            logger.error(f"[KakaoPostsCache] fetch 실패: {e}")
            return False
        finally:
            self._fetching = False

    def last_updated(self) -> Optional[str]:
        if self._last_fetched is None:
            return None
        return datetime.fromtimestamp(self._last_fetched, tz=timezone.utc).isoformat()


def _github_request(url: str) -> dict | list:
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def _fetch_category(category: str) -> List[dict]:
    url = f"{GITHUB_API_BASE}/{category}"
    try:
        items = _github_request(url)
    except URLError:
        logger.warning(f"[KakaoPostsCache] {category} 폴더 fetch 실패 — 빈 목록 반환")
        return []

    posts = []
    for item in items:
        if not item.get("name", "").endswith(".json"):
            continue
        try:
            file_info = _github_request(item["url"])
            import base64
            content = base64.b64decode(file_info["content"]).decode("utf-8")
            post = json.loads(content)
            posts.append(post)
        except Exception as e:
            logger.warning(f"[KakaoPostsCache] {item['name']} 파싱 실패: {e}")
    return posts


def _fetch_all_categories() -> Dict[str, List[dict]]:
    result = {}
    for cat in CATEGORIES:
        result[cat] = _fetch_category(cat)
    return result


# 싱글턴 캐시 인스턴스
_cache = KakaoPostsCache()


def get_cache() -> KakaoPostsCache:
    return _cache


def auto_refresh_if_stale() -> None:
    if _cache.is_stale():
        _cache.refresh()

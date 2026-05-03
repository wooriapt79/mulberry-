# core/blogger_profiler.py
"""
블로거 프로파일러 — 사용자 행동 신호로 아키타입 분류
인제군 공동구매 맥락에서 최적 접근 타이밍과 메시지 톤 결정
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger("BloggerProfiler")


class BloggerArchetype(Enum):
    """v2.0 사용자 아키타입"""
    MINIMALIST         = "minimalist"          # 심플, 핵심만
    TRENDSETTER        = "trendsetter"         # 신상품, 트렌드 민감
    CONSCIOUS_CONSUMER = "conscious_consumer"  # 로컬·윤리 소비 중시
    COMMUNITY_BUILDER  = "community_builder"   # 이웃·관계 중심
    LOCAL_ADVOCATE     = "local_advocate"      # 지역 경제 지지자


# 아키타입별 최적 접근 전략
ARCHETYPE_APPROACH: dict[str, dict] = {
    BloggerArchetype.MINIMALIST.value: {
        "tone": "concise",
        "opening": "인제 감자 10kg, 15,000원. 지금 참여 가능합니다.",
        "trigger_threshold": 0.65,
        "image_style": "clean_minimal",
    },
    BloggerArchetype.TRENDSETTER.value: {
        "tone": "enthusiastic",
        "opening": "이번 시즌 핫한 인제 고랭지 감자, 공동구매 오픈했어요!",
        "trigger_threshold": 0.55,
        "image_style": "vibrant_modern",
    },
    BloggerArchetype.CONSCIOUS_CONSUMER.value: {
        "tone": "authentic",
        "opening": "농부 직거래, 인제 감자 공동구매입니다. 중간 유통 없이 직접 연결해요.",
        "trigger_threshold": 0.60,
        "image_style": "harvest_event",
    },
    BloggerArchetype.COMMUNITY_BUILDER.value: {
        "tone": "warm_jeong",
        "opening": "이웃들과 함께하는 인제 감자 공동구매. 10명 모으면 함께 받아요 :)",
        "trigger_threshold": 0.50,
        "image_style": "cooperative_purchase",
    },
    BloggerArchetype.LOCAL_ADVOCATE.value: {
        "tone": "purposeful",
        "opening": "인제군 농민을 직접 돕는 공동구매입니다. 지역경제에 함께해요.",
        "trigger_threshold": 0.55,
        "image_style": "direct_trade",
    },
}


@dataclass
class BehavioralSignal:
    """사용자 행동 신호 수집 단위"""
    time_on_page_sec:  float = 0.0   # 페이지 체류 시간
    scroll_depth_pct:  float = 0.0   # 스크롤 깊이 (0~1)
    cursor_hover_pct:  float = 0.0   # 구매 영역 커서 호버 비율
    exit_intent:       bool  = False  # 뒤로가기/탭 전환 의도 감지
    revisit_count:     int   = 0      # 재방문 횟수
    local_keyword_hit: bool  = False  # 인제/강원 키워드 반응 여부
    community_click:   bool  = False  # 공동구매 링크 클릭 여부

    @property
    def engagement_score(self) -> float:
        """0.0~1.0 사이 종합 참여도 점수"""
        score = 0.0
        score += min(self.time_on_page_sec / 120.0, 0.25)  # 2분 기준 최대 0.25
        score += self.scroll_depth_pct * 0.20
        score += self.cursor_hover_pct * 0.20
        score += 0.15 if self.exit_intent else 0.0         # 이탈 직전 = 높은 관심
        score += min(self.revisit_count * 0.05, 0.10)
        score += 0.05 if self.local_keyword_hit else 0.0
        score += 0.05 if self.community_click else 0.0
        return round(min(score, 1.0), 3)


@dataclass
class ProfilerResult:
    """프로파일링 결과"""
    archetype:        BloggerArchetype
    confidence:       float                  # 0~1
    engagement_score: float
    should_trigger:   bool
    approach_config:  dict = field(default_factory=dict)
    signals:          Optional[BehavioralSignal] = None


class BloggerProfiler:
    """
    행동 신호 기반 블로거 아키타입 분류 및 접근 타이밍 결정
    """

    def profile(self, signals: BehavioralSignal) -> ProfilerResult:
        """
        행동 신호를 분석하여 아키타입과 접근 여부 결정

        Args:
            signals: 수집된 행동 신호

        Returns:
            ProfilerResult — 아키타입, 신뢰도, 접근 여부
        """
        archetype, confidence = self._classify(signals)
        approach_cfg = ARCHETYPE_APPROACH[archetype.value]
        threshold = approach_cfg["trigger_threshold"]
        should_trigger = signals.engagement_score >= threshold

        logger.info(
            "프로파일링 완료 — archetype=%s confidence=%.2f engagement=%.3f trigger=%s",
            archetype.value, confidence, signals.engagement_score, should_trigger,
        )

        return ProfilerResult(
            archetype=archetype,
            confidence=confidence,
            engagement_score=signals.engagement_score,
            should_trigger=should_trigger,
            approach_config=approach_cfg,
            signals=signals,
        )

    def _classify(self, s: BehavioralSignal) -> tuple[BloggerArchetype, float]:
        """신호 패턴으로 아키타입 분류 (규칙 기반 점수 시스템)"""
        scores: dict[BloggerArchetype, float] = {a: 0.0 for a in BloggerArchetype}

        # 지역 키워드 반응 → LOCAL_ADVOCATE / CONSCIOUS_CONSUMER
        if s.local_keyword_hit:
            scores[BloggerArchetype.LOCAL_ADVOCATE]     += 0.35
            scores[BloggerArchetype.CONSCIOUS_CONSUMER] += 0.20

        # 공동구매 링크 클릭 → COMMUNITY_BUILDER
        if s.community_click:
            scores[BloggerArchetype.COMMUNITY_BUILDER] += 0.40
            scores[BloggerArchetype.LOCAL_ADVOCATE]    += 0.15

        # 빠른 스크롤 + 짧은 체류 → MINIMALIST
        if s.scroll_depth_pct > 0.8 and s.time_on_page_sec < 30:
            scores[BloggerArchetype.MINIMALIST] += 0.35

        # 긴 체류 + 깊은 스크롤 → CONSCIOUS_CONSUMER
        if s.time_on_page_sec > 90 and s.scroll_depth_pct > 0.6:
            scores[BloggerArchetype.CONSCIOUS_CONSUMER] += 0.30

        # 재방문 2회 이상 → TRENDSETTER
        if s.revisit_count >= 2:
            scores[BloggerArchetype.TRENDSETTER] += 0.30

        # 커서 호버 높음 → COMMUNITY_BUILDER (구체적 참여 의향)
        if s.cursor_hover_pct > 0.5:
            scores[BloggerArchetype.COMMUNITY_BUILDER] += 0.25

        best = max(scores, key=lambda a: scores[a])
        total = sum(scores.values()) or 1.0
        confidence = round(scores[best] / total, 2)

        # 점수가 모두 0이면 기본값
        if scores[best] == 0.0:
            return BloggerArchetype.COMMUNITY_BUILDER, 0.40

        return best, confidence

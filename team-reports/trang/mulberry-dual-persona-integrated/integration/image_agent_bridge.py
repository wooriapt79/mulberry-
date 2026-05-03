# integration/image_agent_bridge.py
"""
Image Agent Bridge — DualPersonaAgent ↔ HybridPipeline 연결

ENGAGING 상태 전환 시 아키타입에 맞는 이미지 패키지를 자동 생성.
promotion_type은 BloggerArchetype.approach_config["image_style"]에서 결정됨.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# 이미지 에이전트 MVP 경로 등록
_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_root / "mulberry-image-agent-mvp"))

logger = logging.getLogger("ImageAgentBridge")


class ImageAgentBridge:
    """
    HybridPipeline을 DualPersonaAgent에서 호출하는 브릿지 클래스.

    아키타입별 image_style → HybridPipeline promotion_type 매핑:
      cooperative_purchase → "cooperative_purchase"
      harvest_event        → "harvest_event"
      direct_trade         → "direct_trade"
      clean_minimal        → "cooperative_purchase" (심플 변형)
      vibrant_modern       → "cooperative_purchase" (트렌디 변형)
    """

    # image_style → (promotion_type, extra_keywords)
    STYLE_MAP = {
        "cooperative_purchase": ("cooperative_purchase", ["정겨운", "이웃", "함께"]),
        "harvest_event":        ("harvest_event",        ["가을걷이", "인제", "함께"]),
        "direct_trade":         ("direct_trade",         ["직거래", "로컬푸드", "신뢰"]),
        "clean_minimal":        ("cooperative_purchase", ["인제 감자", "공동구매"]),
        "vibrant_modern":       ("cooperative_purchase", ["인제 감자", "이웃", "함께"]),
    }

    def __init__(
        self,
        openai_api_key: str = None,
        output_dir: str = "output/dual_persona",
    ):
        self.openai_api_key = openai_api_key
        self.output_dir = output_dir
        self._pipeline = None

    def generate(
        self,
        campaign: dict,
        promotion_type: str = "cooperative_purchase",
        season: str = None,
    ) -> dict:
        """
        아키타입 스타일에 맞는 HybridPipeline 실행

        Args:
            campaign: 공동구매 캠페인 정보
            promotion_type: BloggerArchetype image_style 값
            season: 계절 (None이면 자동 감지)

        Returns:
            HybridPipeline.run() 결과 딕셔너리
        """
        mapped_type, extra_kw = self.STYLE_MAP.get(
            promotion_type,
            ("cooperative_purchase", ["정겨운", "이웃", "함께"]),
        )

        logger.info(
            "ImageAgentBridge.generate — style=%s → type=%s campaign=%s",
            promotion_type, mapped_type, campaign.get("campaign_id"),
        )

        pipeline = self._get_pipeline()
        result = pipeline.run(
            campaign=campaign,
            season=season,
            promotion_type=mapped_type,
            extra_keywords=extra_kw,
        )

        logger.info(
            "이미지 생성 완료 — code=%s verified=%s",
            result.get("purchase_code"), result.get("metadata_verified"),
        )
        return result

    def decode_image(self, image_path: str) -> Optional[dict]:
        """수신 이미지에서 공동구매 메타데이터 추출"""
        from stage1_model2_mvp.metadata_encoder import MetadataDecoder
        return MetadataDecoder().decode(image_path)

    def _get_pipeline(self):
        if self._pipeline is None:
            from stage3_hybrid.hybrid_pipeline import HybridPipeline
            self._pipeline = HybridPipeline(
                openai_api_key=self.openai_api_key,
                output_dir=self.output_dir,
            )
        return self._pipeline

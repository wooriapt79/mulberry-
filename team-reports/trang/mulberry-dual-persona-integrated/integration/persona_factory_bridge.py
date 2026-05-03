# integration/persona_factory_bridge.py
"""
Persona Factory Bridge — DualPersonaAgent ↔ AgentFactory 연결

BloggerArchetype에 맞는 페르소나를 PersonaReferenceAdapter + EthicsGate로
검증하고 KoreanPersonaExtractor로 특성을 추출합니다.

아키타입별 페르소나 특성:
  COMMUNITY_BUILDER → jeong_sensitivity 높음, 노인 존중 톤
  LOCAL_ADVOCATE    → 지역 방언(gangwon), 직거래 강조
  CONSCIOUS_CONSUMER → 정직 투명 강조
  MINIMALIST        → 간결 핵심 전달
  TRENDSETTER       → 젊은 트렌드 언어
"""

import logging
import sys
from pathlib import Path
from typing import Optional

_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_root / "mulberry-agent-factory-final" / "src"))

logger = logging.getLogger("PersonaFactoryBridge")

# 아키타입별 기본 페르소나 템플릿
ARCHETYPE_PERSONA_TEMPLATES: dict[str, dict] = {
    "community_builder": {
        "id": "mulberry_community_builder",
        "profile": {
            "name": "이웃 연결자",
            "age_group": "40-60",
            "region": "gangwon",
            "values": ["이웃", "함께", "정"],
            "tone": "warm_jeong",
        },
        "dialogues": [
            "이웃들과 함께하는 공동구매입니다. 존중하고 배려하며 진행해요.",
        ],
    },
    "local_advocate": {
        "id": "mulberry_local_advocate",
        "profile": {
            "name": "지역 지지자",
            "age_group": "30-50",
            "region": "gangwon",
            "values": ["인제", "로컬푸드", "직거래", "지역경제"],
            "tone": "purposeful",
        },
        "dialogues": [
            "인제군 농민을 직접 지원하는 공동구매입니다. 자율적 선택을 존중합니다.",
        ],
    },
    "conscious_consumer": {
        "id": "mulberry_conscious_consumer",
        "profile": {
            "name": "의식있는 소비자",
            "age_group": "25-45",
            "region": "gangwon",
            "values": ["직거래", "투명", "로컬푸드"],
            "tone": "authentic",
        },
        "dialogues": [
            "중간 유통 없이 농부에게서 직접 옵니다. 안전하게 배려하며 진행해요.",
        ],
    },
    "minimalist": {
        "id": "mulberry_minimalist",
        "profile": {
            "name": "핵심 전달자",
            "age_group": "20-40",
            "region": "gangwon",
            "values": ["효율", "정직"],
            "tone": "concise",
        },
        "dialogues": ["핵심만 전달합니다."],
    },
    "trendsetter": {
        "id": "mulberry_trendsetter",
        "profile": {
            "name": "트렌드 안내자",
            "age_group": "20-35",
            "region": "gangwon",
            "values": ["신선함", "트렌드", "지역"],
            "tone": "enthusiastic",
        },
        "dialogues": ["이번 시즌 핫한 인제 직거래입니다!"],
    },
}


class PersonaFactoryBridge:
    """
    AgentFactory(PersonaReferenceAdapter + KoreanPersonaExtractor)를
    DualPersonaAgent에 연결하는 브릿지.
    """

    def __init__(self, spirit_threshold: float = 0.75):
        self.spirit_threshold = spirit_threshold
        self._adapter = None
        self._extractor = None

    def get_validated_persona(
        self,
        archetype_value: str,
    ) -> Optional[dict]:
        """
        아키타입에 해당하는 페르소나를 EthicsGate 검증 후 반환

        Args:
            archetype_value: BloggerArchetype.value 문자열

        Returns:
            검증 통과 페르소나 dict, 실패 시 None
        """
        template = ARCHETYPE_PERSONA_TEMPLATES.get(archetype_value)
        if not template:
            logger.warning("알 수 없는 아키타입: %s", archetype_value)
            return None

        adapter = self._get_adapter()
        validated = adapter.adapt_reference(
            external_persona=template,
            source_note=f"mulberry_dual_persona_v2/{archetype_value}",
        )

        if validated is None:
            logger.warning("EthicsGate 검증 실패 — archetype=%s", archetype_value)
            return None

        logger.info("페르소나 검증 통과 — archetype=%s spirit=%.2f",
                    archetype_value,
                    validated["meta"]["spirit_score"])
        return validated

    def extract_korean_features(self, persona: dict) -> Optional[dict]:
        """
        검증된 페르소나에서 한국어 특성 추출 (KoreanPersonaExtractor)

        Returns:
            KoreanPersonaFeatures 딕셔너리 표현
        """
        extractor = self._get_extractor()
        profile = persona.get("profile", {})

        # KoreanPersonaExtractor는 외부 페르소나 형식이 아닌 Mulberry 형식을 입력으로 받음
        # profile 키 기반으로 직접 구성
        region = profile.get("region", "gangwon") if isinstance(profile, dict) else "gangwon"
        raw_persona = {
            "profile": {
                "region": region,
                "age_group": profile.get("age_group", "40-60") if isinstance(profile, dict) else "40-60",
                "values": profile.get("values", []) if isinstance(profile, dict) else [],
            }
        }

        try:
            features = extractor.extract(raw_persona)
            return {
                "dialect_region":       features.dialect_region,
                "jeong_sensitivity":    features.jeong_sensitivity,
                "honorific_preference": features.honorific_preference,
                "community_orientation": features.community_orientation,
            }
        except Exception as e:
            logger.warning("특성 추출 실패: %s", e)
            return None

    def _get_adapter(self):
        if self._adapter is None:
            from persona.persona_reference_adapter import PersonaReferenceAdapter
            self._adapter = PersonaReferenceAdapter(
                spirit_threshold=self.spirit_threshold
            )
        return self._adapter

    def _get_extractor(self):
        if self._extractor is None:
            from agentfactory.korean_persona_extractor import KoreanPersonaFeatureExtractor
            self._extractor = KoreanPersonaFeatureExtractor()
        return self._extractor

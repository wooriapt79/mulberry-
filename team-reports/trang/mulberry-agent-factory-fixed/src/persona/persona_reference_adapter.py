# src/persona/persona_reference_adapter.py
"""
외부 페르소나 데이터를 Mulberry 참고자료로 안전하게 변환
EthicsGate를 실제로 호출하여 윤리 검증을 수행합니다.
"""

import json
import logging
from typing import Optional, Dict
from src.persona.base_persona_adapter import BasePersonaAdapter
from src.persona.ethics_gate import EthicsGate

logger = logging.getLogger("PersonaReferenceAdapter")


class PersonaReferenceAdapter(BasePersonaAdapter):
    """
    Nemotron 등 외부 페르소나 데이터를 '설계 참고용'으로 변환하는 어댑터.
    EthicsGate를 통해 모든 페르소나의 윤리 기준을 강제합니다.
    """

    def __init__(self, spirit_threshold: float = 0.75, ethics_config_path: str = None):
        self.spirit_threshold = spirit_threshold
        # FIX: EthicsGate를 실제로 인스턴스화하여 연동
        self.ethics_gate = EthicsGate(config_path=ethics_config_path)
        self.mulberry_schema = self._load_schema()

    def _load_schema(self) -> Dict:
        """Mulberry 스키마 로더 (placeholder — 실제 구현 필요)"""
        return {}

    def adapt_reference(self, external_persona: Dict, source_note: str) -> Optional[Dict]:
        """
        외부 페르소나 → Mulberry 참고자료 변환

        Returns:
            Mulberry 형식의 페르소나 참고자료, 또는 검증 실패 시 None.
        """
        persona_id = external_persona.get("id", "unknown")

        # 1. EthicsGate 실제 호출 (원본은 간이 로직만 사용하고 EthicsGate 미연동)
        ethics_result = self.ethics_gate.check_persona_spirit(external_persona)
        spirit_score = ethics_result.get("spirit_score", 0.0)
        ethics_passed = ethics_result.get("passed", False)

        # EthicsGate가 명시적으로 passed=False를 반환하거나 spirit_score가 임계값 미달인 경우 모두 거부
        if not ethics_passed or spirit_score < self.spirit_threshold:
            logger.warning(
                "윤리 검증 실패 — id=%s spirit_score=%.2f (threshold=%.2f) issues=%s",
                persona_id, spirit_score, self.spirit_threshold, ethics_result.get("issues"),
            )
            return None

        logger.info("윤리 검증 통과 — id=%s spirit_score=%.2f", persona_id, spirit_score)

        # 2. 구조만 추출 (내용은 비움)
        adapted = {
            "persona_id": f"ref_{persona_id}",
            "meta": {
                "source": "reference_only",
                "source_note": source_note,
                "spirit_score": spirit_score,
                "spirit_score_baseline": self.spirit_threshold,
                "ethics_details": ethics_result.get("details", {}),
                "requires_field_validation": True,
            },
            "profile": self._extract_structure_only(external_persona.get("profile", {})),
            "behavioral_patterns": {},    # 현장 데이터로 채울 것
            "spirit_requirements": self._infer_spirit_requirements(external_persona),
            "sample_interactions": [],    # 인제군 데이터로 채울 것
            "_reference_note": {
                "usage": "구조 설계 참고용만 허용",
                "prohibited": ["직접 학습 데이터 사용", "원본 내용 복사", "라이선스 무시 배포"],
                "required_next_step": "인제군 현장 인터뷰 데이터로 프로파일 완성",
            },
        }

        return adapted

    def _extract_structure_only(self, profile: Dict) -> Dict:
        """내용은 비우고 키 구조만 추출"""
        return {key: None for key in profile.keys()}

    def _infer_spirit_requirements(self, persona: Dict) -> Dict:
        """페르소나 특성 기반 윤리 요구사항 추론"""
        age = str(persona.get("profile", {}).get("age_group", ""))
        profile_str = str(persona.get("profile", {}))

        if "65" in age or "elderly" in age:
            return {
                "tone": "respectful_elderly",
                "pace": "slow_with_pause",
                "redundancy": "allow_repetition",
            }
        elif "vulnerable" in profile_str:
            return {
                "tone": "empathetic_supportive",
                "safety_net": "always_offer_human_handoff",
            }
        return {"tone": "standard"}

    def save_as_reference(self, adapted: Dict, output_path: str) -> None:
        """참고자료용 JSON으로 저장"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(adapted, f, ensure_ascii=False, indent=2)
        logger.info("참고자료 저장: %s", output_path)

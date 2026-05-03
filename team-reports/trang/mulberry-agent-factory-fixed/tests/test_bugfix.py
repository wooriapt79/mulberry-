# tests/test_bugfix.py
"""
버그 수정 검증 테스트
- 버그1: AgentFactoryProfileConverter.AttributeError 수정 확인
- 버그2: gangwon 지역 dialect_region 매핑 오류 수정 확인
- 추가: EthicsGate 실제 연동 확인
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.agentfactory.korean_persona_extractor import KoreanPersonaFeatureExtractor
from src.agentfactory.agentfactory_converter import AgentFactoryProfileConverter
from src.persona.persona_reference_adapter import PersonaReferenceAdapter
from src.persona.ethics_gate import EthicsGate


# ─────────────────────────────────────────────
# 버그 1: AttributeError 수정 확인
# ─────────────────────────────────────────────

def test_bug1_no_attribute_error_on_convert():
    """
    원본: _estimate_conversion/retention 에서 features.communication 참조 → AttributeError
    수정: KoreanPersonaFeatures 필드 직접 참조로 변경
    """
    extractor = KoreanPersonaFeatureExtractor()
    converter = AgentFactoryProfileConverter()

    dialogues = [
        {"user": "고마워요, 함께 해주셔서요"},
        {"user": "이웃들과 같이 하고 싶어요"},
        {"user": "존중해주세요"},
    ]
    features = extractor.extract_from_dialogue(dialogues)
    features.confidence_score = 0.8  # 폴백 우회

    # AttributeError 없이 실행되어야 함
    profile = converter.convert_to_business_profile(features)

    assert "predicted_kpis" in profile
    assert "conversion_rate_estimate" in profile["predicted_kpis"]
    assert "retention_probability" in profile["predicted_kpis"]
    print(f"[PASS] 버그1: conversion={profile['predicted_kpis']['conversion_rate_estimate']:.2f}, "
          f"retention={profile['predicted_kpis']['retention_probability']:.2f}")


def test_bug1_fallback_profile_when_low_confidence():
    extractor = KoreanPersonaFeatureExtractor()
    converter = AgentFactoryProfileConverter()
    features = extractor._init_features()
    features.confidence_score = 0.3  # 낮은 신뢰도

    profile = converter.convert_to_business_profile(features)
    assert profile["meta"]["fallback_applied"] is True
    print("[PASS] 버그1: 폴백 프로필 정상 작동")


# ─────────────────────────────────────────────
# 버그 2: gangwon 지역 매핑 수정 확인
# ─────────────────────────────────────────────

def test_bug2_gangwon_region_not_gyeongsang():
    """
    원본: region="gangwon" → dialect_region="gyeongsang" (잘못된 매핑)
    수정: region="gangwon" → dialect_region="gangwon"
    """
    extractor = KoreanPersonaFeatureExtractor()
    nemotron_record = {
        "profile": {
            "age": "45",
            "region": "gangwon",
        }
    }
    features = extractor.extract_from_reference(nemotron_record)
    assert features.dialect_region == "gangwon", (
        f"버그2 미수정: dialect_region={features.dialect_region} (expected: gangwon)"
    )
    assert features.dialect_region != "gyeongsang"
    print(f"[PASS] 버그2: gangwon 매핑 정상 → dialect_region={features.dialect_region}")


def test_bug2_gyeongsang_region_still_works():
    """경상도 지역은 여전히 gyeongsang으로 매핑되어야 함"""
    extractor = KoreanPersonaFeatureExtractor()
    features = extractor.extract_from_reference({
        "profile": {"age": "50", "region": "gyeongnam"}
    })
    assert features.dialect_region == "gyeongsang"
    print(f"[PASS] 버그2: gyeongnam → gyeongsang 매핑 정상")


def test_bug2_elderly_in_gangwon():
    """인제군 고령자 — 강원도 매핑 + 경로 설정이 동시에 되어야 함"""
    extractor = KoreanPersonaFeatureExtractor()
    features = extractor.extract_from_reference({
        "profile": {"age": "65", "region": "gangwon"}
    })
    assert features.dialect_region == "gangwon"
    assert features.honorific_preference == "respectful_elderly"
    assert features.procedure_tolerance == 2
    print("[PASS] 버그2: 인제군 고령자 프로필 정상")


# ─────────────────────────────────────────────
# EthicsGate 실제 연동 확인
# ─────────────────────────────────────────────

def test_ethics_gate_integrated_in_adapter():
    """EthicsGate가 실제로 호출되어 spirit_score가 meta에 기록되어야 함"""
    adapter = PersonaReferenceAdapter(spirit_threshold=0.5)

    good_persona = {
        "id": "test_001",
        "profile": {
            "age_group": "40s",
            "region": "gangwon",
            "value": "존중과 배려를 중시합니다",
        },
        "sample_interactions": [],
    }
    result = adapter.adapt_reference(good_persona, "테스트 소스")

    # 결과가 있어야 하고, spirit_score가 meta에 포함되어야 함
    assert result is not None, "윤리 통과 페르소나가 None을 반환하면 안 됨"
    assert "spirit_score" in result["meta"], "spirit_score가 meta에 없음 — EthicsGate 미연동 의심"
    print(f"[PASS] EthicsGate 연동: spirit_score={result['meta']['spirit_score']:.2f}")


def test_ethics_gate_rejects_stereotype_persona():
    """고정관념 키워드 포함 페르소나는 거부되어야 함"""
    adapter = PersonaReferenceAdapter(spirit_threshold=0.75)

    bad_persona = {
        "id": "test_bad",
        "profile": {
            "description": "무지함과 게으름이 특징적인 집단",
        },
        "sample_interactions": [],
    }
    result = adapter.adapt_reference(bad_persona, "나쁜 소스")
    assert result is None, "고정관념 페르소나가 통과되면 안 됨"
    print("[PASS] EthicsGate: 고정관념 페르소나 거부 정상")


# ─────────────────────────────────────────────
# 실행
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("버그 수정 검증 테스트")
    print("=" * 50)

    test_bug1_no_attribute_error_on_convert()
    test_bug1_fallback_profile_when_low_confidence()
    test_bug2_gangwon_region_not_gyeongsang()
    test_bug2_gyeongsang_region_still_works()
    test_bug2_elderly_in_gangwon()
    test_ethics_gate_integrated_in_adapter()
    test_ethics_gate_rejects_stereotype_persona()

    print("=" * 50)
    print("모든 테스트 통과")

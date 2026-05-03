# tests/test_dual_persona_integration.py
"""
Dual Persona Agent v2.0 통합 테스트
API 호출 없이 전체 상태 머신 + 프로파일링 + 통합 흐름 검증
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.agent_state import (
    AgentState, PersonaMode, AgentStateMachine,
    STATE_PERSONA_MAP, StateTransitionError,
)
from core.blogger_profiler import BloggerProfiler, BehavioralSignal, BloggerArchetype
from core.dual_persona_agent import DualPersonaAgent

SAMPLE_CAMPAIGN = {
    "product": "potato",
    "product_kr": "인제 감자",
    "campaign_id": "INJE-TEST-001",
    "title": "인제 감자 공동구매",
    "price": 15000,
    "min_participants": 10,
    "deadline": "2026-05-31",
    "cta_url": "https://mulberry.inje/join/potato-test",
    "organizer": "인제군 농협",
}


def test_state_machine_transitions():
    """정상 전환 경로 검증: MONITORING → APPROACHING → WAITING → ENGAGING → ACTIVE"""
    sm = AgentStateMachine()
    assert sm.state == AgentState.MONITORING
    assert sm.persona == PersonaMode.MARKETER

    sm.transition(AgentState.APPROACHING, "behavioral_trigger")
    assert sm.state == AgentState.APPROACHING
    assert sm.persona == PersonaMode.MARKETER

    sm.transition(AgentState.WAITING, "message_sent")
    assert sm.state == AgentState.WAITING

    sm.transition(AgentState.ENGAGING, "user_responded")
    assert sm.state == AgentState.ENGAGING
    assert sm.persona == PersonaMode.ASSISTANT  # 페르소나 전환!

    sm.transition(AgentState.ACTIVE, "purchase_intent_confirmed")
    assert sm.state == AgentState.ACTIVE
    assert sm.persona == PersonaMode.ASSISTANT

    print("[PASS] 상태 전환 정상 경로")


def test_invalid_transition_raises():
    """잘못된 전환 시 StateTransitionError 발생 확인"""
    sm = AgentStateMachine()
    try:
        sm.transition(AgentState.ACTIVE, "invalid")
        assert False, "예외가 발생해야 함"
    except StateTransitionError:
        pass

    print("[PASS] 잘못된 전환 예외 처리")


def test_persona_switch_on_engaging():
    """APPROACHING → ENGAGING 전환 시 Marketer → Assistant 전환 확인"""
    sm = AgentStateMachine()
    sm.transition(AgentState.APPROACHING, "trigger")
    snap = sm.transition(AgentState.ENGAGING, "user_responded")

    assert snap.persona_switched is True
    assert snap.persona_mode == PersonaMode.ASSISTANT
    print("[PASS] 페르소나 자동 전환 (Marketer → Assistant)")


def test_persona_no_switch_within_marketer():
    """MONITORING → APPROACHING 은 페르소나 전환 없음 (둘 다 MARKETER)"""
    sm = AgentStateMachine()
    snap = sm.transition(AgentState.APPROACHING, "trigger")
    assert snap.persona_switched is False
    print("[PASS] Marketer 내 전환 - 페르소나 유지 확인")


def test_blogger_profiler_community_builder():
    """공동구매 클릭 + 지역 키워드 → COMMUNITY_BUILDER 분류"""
    profiler = BloggerProfiler()
    signals = BehavioralSignal(
        time_on_page_sec=60,
        scroll_depth_pct=0.5,
        cursor_hover_pct=0.6,
        exit_intent=False,
        revisit_count=1,
        local_keyword_hit=True,
        community_click=True,
    )
    result = profiler.profile(signals)
    assert result.archetype == BloggerArchetype.COMMUNITY_BUILDER
    assert result.should_trigger is True
    print(f"[PASS] COMMUNITY_BUILDER 분류 -score={result.engagement_score:.3f}")


def test_blogger_profiler_local_advocate():
    """지역 키워드 강한 반응, 공동구매 미클릭 → LOCAL_ADVOCATE"""
    profiler = BloggerProfiler()
    signals = BehavioralSignal(
        time_on_page_sec=75,
        scroll_depth_pct=0.65,
        cursor_hover_pct=0.3,
        local_keyword_hit=True,
        community_click=False,
    )
    result = profiler.profile(signals)
    # LOCAL_ADVOCATE 또는 CONSCIOUS_CONSUMER (둘 다 지역 키워드 반응)
    assert result.archetype in (BloggerArchetype.LOCAL_ADVOCATE, BloggerArchetype.CONSCIOUS_CONSUMER)
    print(f"[PASS] 지역 키워드 분류 -archetype={result.archetype.value}")


def test_blogger_profiler_minimalist():
    """빠른 스크롤 + 짧은 체류 → MINIMALIST"""
    profiler = BloggerProfiler()
    signals = BehavioralSignal(
        time_on_page_sec=18,
        scroll_depth_pct=0.9,
        cursor_hover_pct=0.1,
    )
    result = profiler.profile(signals)
    assert result.archetype == BloggerArchetype.MINIMALIST
    print(f"[PASS] MINIMALIST 분류 -engagement={result.engagement_score:.3f}")


def test_engagement_score_calculation():
    """BehavioralSignal engagement_score 계산 검증"""
    s = BehavioralSignal(
        time_on_page_sec=120,   # 최대 0.25
        scroll_depth_pct=1.0,   # 0.20
        cursor_hover_pct=1.0,   # 0.20
        exit_intent=True,       # 0.15
        revisit_count=2,        # 0.10
        local_keyword_hit=True, # 0.05
        community_click=True,   # 0.05
    )
    assert s.engagement_score == 1.0
    print(f"[PASS] engagement_score 만점 계산: {s.engagement_score}")


def test_dual_persona_agent_full_cycle():
    """
    DualPersonaAgent 전체 사이클 (API 없음 -mock 패키지)
    MONITORING → APPROACHING → WAITING → ENGAGING → ACTIVE
    """
    agent = DualPersonaAgent(openai_api_key=None)  # API 키 없음

    signals = BehavioralSignal(
        time_on_page_sec=90,
        scroll_depth_pct=0.7,
        cursor_hover_pct=0.5,
        revisit_count=1,
        local_keyword_hit=True,
        community_click=True,
    )

    result = agent.run_full_cycle(
        signals=signals,
        campaign=SAMPLE_CAMPAIGN,
        user_response="네, 공동구매 참여하고 싶어요",
    )

    assert "observe" in result
    assert result["observe"]["should_approach"] is True
    assert result["approach"]["persona"] == "marketer"
    assert result["engage"]["persona"] == "assistant"
    assert result["engage"]["persona_switched"] is True

    # mock 패키지 확인
    pkg = result["activate"]["package"]
    assert pkg is not None
    assert pkg["status"] == "mock"
    assert "INJE-TEST-001" in pkg["purchase_code"] or "MOCK" in pkg["purchase_code"]

    # 전환 이력 확인
    history = result["history"]
    assert len(history) >= 4
    persona_modes = [h["persona"] for h in history]
    assert "marketer" in persona_modes
    assert "assistant" in persona_modes

    print(f"[PASS] 전체 사이클 완료")
    print(f"       아키타입: {result['observe']['archetype']}")
    print(f"       오프닝: {result['approach']['opening_message']}")
    print(f"       SMS:\n{pkg['sms_text']}")


def test_dual_persona_no_trigger():
    """engagement_score 낮으면 MONITORING 유지"""
    agent = DualPersonaAgent()
    signals = BehavioralSignal(
        time_on_page_sec=5,
        scroll_depth_pct=0.1,
    )
    obs = agent.observe(signals)
    assert obs["should_approach"] is False
    assert agent.sm.state == AgentState.MONITORING
    print(f"[PASS] 낮은 engagement -접근 안 함 (score={obs['engagement_score']:.3f})")


def test_session_reset():
    """end_session 후 MONITORING 복귀"""
    agent = DualPersonaAgent()
    agent.sm.transition(AgentState.APPROACHING, "test")
    agent.sm.transition(AgentState.ENGAGING, "test")
    agent.end_session()
    assert agent.sm.state == AgentState.MONITORING
    print("[PASS] 세션 리셋 후 MONITORING 복귀")


if __name__ == "__main__":
    print("=" * 60)
    print("Mulberry Dual Persona Agent v2.0 통합 테스트")
    print("=" * 60)
    test_state_machine_transitions()
    test_invalid_transition_raises()
    test_persona_switch_on_engaging()
    test_persona_no_switch_within_marketer()
    test_blogger_profiler_community_builder()
    test_blogger_profiler_local_advocate()
    test_blogger_profiler_minimalist()
    test_engagement_score_calculation()
    test_dual_persona_agent_full_cycle()
    test_dual_persona_no_trigger()
    test_session_reset()
    print("=" * 60)
    print("모든 테스트 통과")

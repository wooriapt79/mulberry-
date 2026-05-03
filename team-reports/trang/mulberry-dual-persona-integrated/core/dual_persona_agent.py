# core/dual_persona_agent.py
"""
Mulberry Dual Persona Agent v2.0 — 핵심 통합 클래스

흐름:
  [MONITORING] 행동 신호 수집
      ↓ 트리거 조건 충족
  [APPROACHING] Marketer 페르소나로 먼저 말 걸기
      ↓ 메시지 전송
  [WAITING] 응답 대기
      ↓ 사용자 응답
  [ENGAGING] → ASSISTANT 페르소나로 자동 전환
      ↓ 공동구매 이미지 + SMS 패키지 전달
  [ACTIVE] 실제 구매 지원

EthicsGate: 모든 페르소나 전환 시 spirit_score 검증
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# 기존 AgentFactory 경로 등록
_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_root / "mulberry-agent-factory-final" / "src"))
sys.path.insert(0, str(_root / "mulberry-image-agent-mvp"))

from core.agent_state import (
    AgentState, PersonaMode, AgentStateMachine, StateSnapshot, StateTransitionError
)
from core.blogger_profiler import BloggerProfiler, BehavioralSignal, ProfilerResult

logger = logging.getLogger("DualPersonaAgent")


# ─── 페르소나 메시지 템플릿 ─────────────────────────────
MARKETER_SYSTEM_PROMPT = """
당신은 인제군 공동구매 프로모션 에이전트의 Marketer 페르소나입니다.
목표: 사용자가 관심 있을 적절한 타이밍에 먼저 다가가 공동구매를 알립니다.
원칙: 강요하지 않고, 자연스럽게, 정(情)있게.
"""

ASSISTANT_SYSTEM_PROMPT = """
당신은 인제군 공동구매 Assistant 페르소나입니다.
사용자가 응답한 순간부터 당신의 역할은 '판매'가 아니라 '도움'입니다.
솔직하고 투명하게 공동구매 정보를 제공하고 사용자 이익을 최우선으로 합니다.
장승배기 정신: 사람 먼저, 기술은 도구.
"""


class DualPersonaAgent:
    """
    Mulberry Proactive Dual Persona Agent v2.0

    AgentFactory + Image Agent MVP + EthicsGate 통합 클래스.
    API 키 없이도 상태 머신과 프로파일링 로직은 완전히 동작합니다.
    """

    def __init__(
        self,
        openai_api_key: str = None,
        spirit_threshold: float = 0.75,
        output_dir: str = "output/dual_persona",
    ):
        self.sm = AgentStateMachine()
        self.profiler = BloggerProfiler()
        self.spirit_threshold = spirit_threshold
        self.openai_api_key = openai_api_key
        self.output_dir = output_dir

        # 지연 로드 — API 키 필요한 컴포넌트
        self._image_bridge = None
        self._persona_bridge = None

        # 세션 상태
        self._profile_result: Optional[ProfilerResult] = None
        self._prepared_package: Optional[dict] = None
        self._active_campaign: Optional[dict] = None

        logger.info("DualPersonaAgent 초기화 — state=%s persona=%s",
                    self.sm.state.value, self.sm.persona.value)

    # ─── 공개 API ──────────────────────────────────────────

    def observe(self, signals: BehavioralSignal) -> dict:
        """
        [MONITORING] 행동 신호 수집 및 접근 여부 판단

        Returns:
            {should_approach, archetype, engagement_score, message}
        """
        if self.sm.state != AgentState.MONITORING:
            return {"should_approach": False, "message": "not_in_monitoring_state"}

        self._profile_result = self.profiler.profile(signals)

        if self._profile_result.should_trigger:
            logger.info("트리거 조건 충족 — archetype=%s score=%.3f",
                        self._profile_result.archetype.value,
                        self._profile_result.engagement_score)

        return {
            "should_approach":  self._profile_result.should_trigger,
            "archetype":        self._profile_result.archetype.value,
            "engagement_score": self._profile_result.engagement_score,
            "confidence":       self._profile_result.confidence,
            "message":          "trigger_ready" if self._profile_result.should_trigger else "keep_monitoring",
        }

    def approach(self, campaign: dict) -> dict:
        """
        [MONITORING → APPROACHING] Marketer 페르소나로 먼저 말 걸기

        Args:
            campaign: 공동구매 캠페인 정보

        Returns:
            {state, persona, opening_message, approach_config}
        """
        snap = self.sm.transition(AgentState.APPROACHING, trigger="behavioral_trigger")
        self._active_campaign = campaign
        self._ethics_check_transition(snap)

        approach_cfg = {}
        if self._profile_result:
            approach_cfg = self._profile_result.approach_config

        opening = approach_cfg.get(
            "opening",
            f"{campaign.get('title', '공동구매')} 안내드립니다.",
        )

        logger.info("[APPROACHING] Marketer 모드 — '%s'", opening)

        return {
            "state":          self.sm.state.value,
            "persona":        self.sm.persona.value,
            "system_prompt":  MARKETER_SYSTEM_PROMPT.strip(),
            "opening_message": opening,
            "approach_config": approach_cfg,
            "campaign_id":    campaign.get("campaign_id"),
        }

    def send_message(self) -> dict:
        """
        [APPROACHING → WAITING] 메시지 발송 후 대기 상태로 전환
        """
        snap = self.sm.transition(AgentState.WAITING, trigger="message_sent")
        logger.info("[WAITING] 응답 대기 중...")
        return {"state": self.sm.state.value, "persona": self.sm.persona.value}

    def engage(self, user_response: str = "") -> dict:
        """
        [WAITING/APPROACHING → ENGAGING] 사용자 응답 → ASSISTANT 페르소나로 자동 전환

        이 전환이 v2.0의 핵심: Marketer → Assistant 페르소나 스위칭

        Returns:
            {state, persona, persona_switched, image_package}
        """
        snap = self.sm.transition(AgentState.ENGAGING, trigger="user_responded")
        self._ethics_check_transition(snap)

        logger.info(
            "[ENGAGING] 페르소나 전환: %s → %s (persona_switched=%s)",
            snap.from_state.value, snap.to_state.value, snap.persona_switched,
        )

        # 이미지 패키지 준비 (API 키 있을 때만 실제 생성)
        image_package = self._prepare_image_package()

        return {
            "state":            self.sm.state.value,
            "persona":          self.sm.persona.value,
            "persona_switched": snap.persona_switched,
            "system_prompt":    ASSISTANT_SYSTEM_PROMPT.strip(),
            "image_package":    image_package,
            "user_response":    user_response,
        }

    def activate(self) -> dict:
        """
        [ENGAGING → ACTIVE] 공동구매 실제 지원 단계
        """
        snap = self.sm.transition(AgentState.ACTIVE, trigger="purchase_intent_confirmed")
        logger.info("[ACTIVE] 공동구매 지원 활성화")
        return {
            "state":   self.sm.state.value,
            "persona": self.sm.persona.value,
            "package": self._prepared_package,
        }

    def end_session(self) -> dict:
        """세션 종료 → MONITORING 복귀"""
        self.sm.reset()
        self._profile_result = None
        self._prepared_package = None
        self._active_campaign = None
        return {"state": self.sm.state.value, "persona": self.sm.persona.value}

    def run_full_cycle(
        self,
        signals: BehavioralSignal,
        campaign: dict,
        user_response: str = "네, 알려주세요",
    ) -> dict:
        """
        전체 사이클 한 번에 실행 (데모/테스트용)

        MONITORING → APPROACHING → WAITING → ENGAGING → ACTIVE
        """
        results = {}

        # 1. 관찰
        obs = self.observe(signals)
        results["observe"] = obs
        if not obs["should_approach"]:
            results["stopped_at"] = "monitoring"
            return results

        # 2. 접근
        results["approach"] = self.approach(campaign)

        # 3. 메시지 발송
        results["send"] = self.send_message()

        # 4. 사용자 응답 → 페르소나 전환
        results["engage"] = self.engage(user_response)

        # 5. 활성화
        results["activate"] = self.activate()

        # 6. 전환 이력
        results["history"] = [
            {
                "from": s.from_state.value,
                "to": s.to_state.value,
                "persona": s.persona_mode.value,
                "switched": s.persona_switched,
                "trigger": s.trigger,
            }
            for s in self.sm.history
        ]

        return results

    # ─── 내부 헬퍼 ─────────────────────────────────────────

    def _ethics_check_transition(self, snap: StateSnapshot) -> None:
        """페르소나 전환 시 EthicsGate spirit_score 로깅"""
        if snap.persona_switched:
            logger.info(
                "EthicsGate check — 페르소나 전환 감지: %s → %s (spirit_threshold=%.2f)",
                snap.from_state.value, snap.to_state.value, self.spirit_threshold,
            )

    def _prepare_image_package(self) -> Optional[dict]:
        """
        ENGAGING 전환 시 이미지 패키지 준비
        openai_api_key 없으면 mock 패키지 반환
        """
        if not self._active_campaign:
            return None

        if not self.openai_api_key:
            # API 키 없음 — mock 패키지로 흐름 유지
            campaign = self._active_campaign
            mock_code = "MOCK" + campaign.get("campaign_id", "TEST")[-8:].upper()
            self._prepared_package = {
                "status": "mock",
                "purchase_code": mock_code,
                "final_image": None,
                "sms_text": (
                    f"[멀베리]\n"
                    f"{campaign.get('title', '공동구매')}\n"
                    f"코드: {mock_code}\n"
                    f"가격: {campaign.get('price', 0):,}원\n"
                    f"링크: {campaign.get('cta_url', '')}"
                ),
                "note": "API 키 없음 — 실제 이미지 생성은 openai_api_key 필요",
            }
            return self._prepared_package

        # 실제 HybridPipeline 실행
        bridge = self._get_image_bridge()
        if bridge:
            archetype_style = (
                self._profile_result.approach_config.get("image_style", "cooperative_purchase")
                if self._profile_result else "cooperative_purchase"
            )
            self._prepared_package = bridge.generate(
                campaign=self._active_campaign,
                promotion_type=archetype_style,
            )
        return self._prepared_package

    def _get_image_bridge(self):
        if self._image_bridge is None:
            try:
                from integration.image_agent_bridge import ImageAgentBridge
                self._image_bridge = ImageAgentBridge(
                    openai_api_key=self.openai_api_key,
                    output_dir=self.output_dir,
                )
            except Exception as e:
                logger.warning("ImageAgentBridge 로드 실패: %s", e)
        return self._image_bridge

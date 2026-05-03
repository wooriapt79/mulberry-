# core/agent_state.py
"""
Dual Persona Agent v2.0 — 상태 머신 정의
Marketer(Monitoring/Approaching/Waiting) ↔ Assistant(Engaging/Active)
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class AgentState(Enum):
    """에이전트 운영 상태"""
    MONITORING  = "monitoring"   # 사용자 행동 신호 수집 중
    APPROACHING = "approaching"  # 최적 타이밍 포착, 말 걸기 준비
    WAITING     = "waiting"      # 메시지 전송 후 응답 대기
    ENGAGING    = "engaging"     # 사용자 응답 — 대화 활성
    ACTIVE      = "active"       # 실제 공동구매 지원 수행


class PersonaMode(Enum):
    """활성 페르소나 모드"""
    MARKETER  = "marketer"   # 전환 최적화 집중
    ASSISTANT = "assistant"  # 사용자 이익 우선


# 상태 → 페르소나 매핑 (v2.0 핵심 규칙)
STATE_PERSONA_MAP: dict[AgentState, PersonaMode] = {
    AgentState.MONITORING:  PersonaMode.MARKETER,
    AgentState.APPROACHING: PersonaMode.MARKETER,
    AgentState.WAITING:     PersonaMode.MARKETER,
    AgentState.ENGAGING:    PersonaMode.ASSISTANT,
    AgentState.ACTIVE:      PersonaMode.ASSISTANT,
}

# 허용된 상태 전환 테이블
VALID_TRANSITIONS: dict[AgentState, list[AgentState]] = {
    AgentState.MONITORING:  [AgentState.APPROACHING],
    AgentState.APPROACHING: [AgentState.WAITING, AgentState.ENGAGING, AgentState.MONITORING],
    AgentState.WAITING:     [AgentState.ENGAGING, AgentState.APPROACHING, AgentState.MONITORING],
    AgentState.ENGAGING:    [AgentState.ACTIVE, AgentState.MONITORING],
    AgentState.ACTIVE:      [AgentState.MONITORING],
}


@dataclass
class StateSnapshot:
    """상태 전환 기록 단위"""
    from_state:   AgentState
    to_state:     AgentState
    persona_mode: PersonaMode
    trigger:      str
    timestamp:    datetime = field(default_factory=datetime.now)

    @property
    def persona_switched(self) -> bool:
        """이 전환에서 페르소나가 바뀌었는가"""
        return (
            STATE_PERSONA_MAP[self.from_state] != STATE_PERSONA_MAP[self.to_state]
        )


class StateTransitionError(Exception):
    """허용되지 않은 상태 전환 시도"""
    pass


class AgentStateMachine:
    """
    v2.0 상태 머신
    허용되지 않은 전환 시도 시 StateTransitionError 발생
    """

    def __init__(self, initial: AgentState = AgentState.MONITORING):
        self.state = initial
        self.history: list[StateSnapshot] = []

    @property
    def persona(self) -> PersonaMode:
        return STATE_PERSONA_MAP[self.state]

    def transition(self, to: AgentState, trigger: str = "manual") -> StateSnapshot:
        if to not in VALID_TRANSITIONS[self.state]:
            raise StateTransitionError(
                f"Invalid transition: {self.state.value} → {to.value}"
            )
        snapshot = StateSnapshot(
            from_state=self.state,
            to_state=to,
            persona_mode=STATE_PERSONA_MAP[to],
            trigger=trigger,
        )
        self.state = to
        self.history.append(snapshot)
        return snapshot

    def reset(self) -> None:
        self.transition(AgentState.MONITORING, trigger="session_end")

    def last_transition(self) -> Optional[StateSnapshot]:
        return self.history[-1] if self.history else None

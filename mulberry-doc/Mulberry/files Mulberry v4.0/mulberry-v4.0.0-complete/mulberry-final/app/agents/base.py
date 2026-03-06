"""
Mulberry Phase 3 - AI Agent Base Architecture
5인 비서 군단의 기반 클래스 및 메시지 버스
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from loguru import logger


# ============================================
# Message Types & Structures
# ============================================

class MessageType(Enum):
    """에이전트 간 메시지 타입"""
    # 재고 관련
    INVENTORY_LOW = "inventory_low"
    INVENTORY_UPDATE = "inventory_update"
    
    # 주문/판매 관련
    ORDER_RECEIVED = "order_received"
    ORDER_COMPLETED = "order_completed"
    PROMOTION_REQUEST = "promotion_request"
    
    # 고객 관련
    CUSTOMER_PATTERN_DETECTED = "customer_pattern_detected"
    RECOMMENDATION_GENERATED = "recommendation_generated"
    
    # 전략 관련
    METRICS_UPDATE = "metrics_update"
    ALERT_SECURITY = "alert_security"
    ALERT_PERFORMANCE = "alert_performance"
    
    # SNS 관련
    POST_REQUEST = "post_request"
    POST_PUBLISHED = "post_published"
    
    # Sentinel 관련
    SENTINEL_ALERT = "sentinel_alert"
    SENTINEL_APPROVAL_REQUEST = "sentinel_approval_request"


@dataclass
class AgentMessage:
    """에이전트 간 메시지"""
    message_id: str
    message_type: MessageType
    from_agent: str
    to_agent: Optional[str] = None  # None이면 브로드캐스트
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    priority: int = 5  # 1(highest) - 10(lowest)
    requires_response: bool = False


# ============================================
# Message Bus (Event-Driven Architecture)
# ============================================

class MessageBus:
    """
    에이전트 간 메시지 버스
    - Pub/Sub 패턴
    - 비동기 메시지 전달
    - 메시지 큐잉
    - 🆕 Emergency Filter (Sentinel Priority Interrupt)
    """
    
    def __init__(self):
        """메시지 버스 초기화"""
        # 구독자 관리 {message_type: [callback_functions]}
        self.subscribers: Dict[MessageType, List[Callable]] = {}
        
        # 메시지 히스토리 (디버깅용)
        self.message_history: List[AgentMessage] = []
        self.max_history = 1000
        
        # 메시지 큐 (우선순위)
        self.message_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        
        # 긴급 메시지 큐 (Emergency Level 4 전용)
        self.emergency_queue: asyncio.Queue = asyncio.Queue()
        
        # 실행 중 플래그
        self.running = False
        
        # 🆕 긴급 모드 (Emergency Level 4 발생 시)
        self.emergency_mode = False
        self.emergency_event: Optional[Dict[str, Any]] = None
        
        # 🆕 SUSPEND 상태 에이전트
        self.suspended_agents: Set[str] = set()
        
        logger.info("✅ Message Bus initialized with Emergency Filter")
    
    async def publish(self, message: AgentMessage):
        """
        메시지 발행
        
        🆕 Emergency Filter 적용:
        - Emergency Level 4 메시지는 emergency_queue로 직행
        - 일반 메시지는 emergency_mode 확인 후 처리
        
        Args:
            message: 발행할 메시지
        """
        # 히스토리 저장
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
        
        # ============================================
        # 🆕 EMERGENCY FILTER (최상위 계층)
        # ============================================
        
        # 1. Emergency Level 4 메시지 감지
        is_emergency = False
        
        if message.message_type == MessageType.SENTINEL_ALERT:
            emergency_level = message.payload.get("emergency_level", 0)
            
            if emergency_level >= 4:
                is_emergency = True
                logger.critical(f"🚨 EMERGENCY LEVEL {emergency_level} DETECTED!")
                
                # 긴급 모드 활성화
                await self._activate_emergency_mode(message)
        
        # 2. 긴급 메시지는 emergency_queue로
        if is_emergency:
            await self.emergency_queue.put(message)
            logger.critical(f"🚨 Emergency message queued: {message.message_id}")
            return
        
        # 3. 긴급 모드 중에는 일반 메시지 차단
        if self.emergency_mode:
            logger.warning(f"⚠️ Emergency mode active. Message {message.message_id} suspended.")
            # 긴급 모드 종료 후 재처리를 위해 대기열에 추가
            # (향후 구현)
            return
        
        # 4. 일반 메시지는 우선순위 큐로
        await self.message_queue.put((
            message.priority,
            message.timestamp,
            message
        ))
        
        logger.debug(f"📤 Message published: {message.message_type.value} from {message.from_agent}")
    
    async def _activate_emergency_mode(self, emergency_message: AgentMessage):
        """
        긴급 모드 활성화
        
        모든 에이전트를 SUSPEND 모드로 전환하고
        자원을 Sentinel에 집중
        
        Args:
            emergency_message: 긴급 메시지
        """
        try:
            logger.critical("🚨 ACTIVATING EMERGENCY MODE!")
            logger.critical("🚨 ALL AGENTS SUSPENDING...")
            
            self.emergency_mode = True
            self.emergency_event = {
                "activated_at": datetime.now().isoformat(),
                "trigger_message": emergency_message.payload,
                "customer_phone": emergency_message.payload.get("customer_phone"),
                "emergency_level": emergency_message.payload.get("emergency_level")
            }
            
            # 모든 에이전트에게 SUSPEND 신호 전송
            suspend_message = AgentMessage(
                message_id=f"SUSPEND_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                message_type=MessageType.SENTINEL_ALERT,
                from_agent="Message_Bus",
                to_agent=None,  # 브로드캐스트
                payload={
                    "command": "SUSPEND",
                    "reason": "Emergency Level 4 detected",
                    "emergency_event": self.emergency_event
                },
                priority=0  # 최고 우선순위
            )
            
            # 긴급 큐에 SUSPEND 명령 추가
            await self.emergency_queue.put(suspend_message)
            
            # Sentinel에게 긴급 상황 보고
            sentinel_report = AgentMessage(
                message_id=f"SENTINEL_REPORT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                message_type=MessageType.SENTINEL_ALERT,
                from_agent="Message_Bus",
                to_agent="Sentinel",
                payload={
                    "alert_type": "EMERGENCY_MODE_ACTIVATED",
                    "severity": "critical",
                    "emergency_event": self.emergency_event,
                    "all_resources_allocated": True
                },
                priority=0
            )
            
            await self.emergency_queue.put(sentinel_report)
            
            logger.critical(f"🚨 Emergency mode activated. Event: {self.emergency_event}")
            
        except Exception as e:
            logger.error(f"❌ Failed to activate emergency mode: {str(e)}")
    
    async def deactivate_emergency_mode(self):
        """
        긴급 모드 해제
        
        Sentinel의 승인 후에만 호출 가능
        """
        try:
            logger.info("✅ Deactivating emergency mode...")
            
            self.emergency_mode = False
            self.suspended_agents.clear()
            
            # 모든 에이전트에게 RESUME 신호
            resume_message = AgentMessage(
                message_id=f"RESUME_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                message_type=MessageType.SENTINEL_ALERT,
                from_agent="Message_Bus",
                to_agent=None,
                payload={
                    "command": "RESUME",
                    "reason": "Emergency resolved"
                },
                priority=1
            )
            
            await self.message_queue.put((1, datetime.now().isoformat(), resume_message))
            
            logger.info("✅ Emergency mode deactivated. Normal operations resumed.")
            
        except Exception as e:
            logger.error(f"❌ Failed to deactivate emergency mode: {str(e)}")
    
    async def start(self):
        """메시지 버스 시작 (백그라운드 처리)"""
        self.running = True
        logger.info("🚀 Message Bus started")
        
        # 두 개의 큐 동시 처리
        asyncio.create_task(self._process_emergency_queue())
        asyncio.create_task(self._process_normal_queue())
    
    async def _process_emergency_queue(self):
        """긴급 메시지 큐 처리 (최우선)"""
        while self.running:
            try:
                # 긴급 큐에서 메시지 가져오기
                message = await asyncio.wait_for(
                    self.emergency_queue.get(),
                    timeout=1.0
                )
                
                logger.critical(f"🚨 Processing emergency message: {message.message_type.value}")
                
                # 긴급 메시지 전달
                callbacks = self.subscribers.get(message.message_type, [])
                
                for callback in callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(message)
                        else:
                            callback(message)
                    except Exception as e:
                        logger.error(f"❌ Emergency callback error: {str(e)}")
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Emergency queue error: {str(e)}")
    
    async def _process_normal_queue(self):
        """일반 메시지 큐 처리"""
        while self.running:
            try:
                # 긴급 모드 중에는 일반 큐 처리 중단
                if self.emergency_mode:
                    await asyncio.sleep(1)
                    continue
                
                # 큐에서 메시지 가져오기 (우선순위 순)
                priority, timestamp, message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                # 해당 타입의 구독자들에게 전달
                callbacks = self.subscribers.get(message.message_type, [])
                
                for callback in callbacks:
                    try:
                        # 비동기 콜백 실행
                        if asyncio.iscoroutinefunction(callback):
                            await callback(message)
                        else:
                            callback(message)
                    except Exception as e:
                        logger.error(f"❌ Callback error: {str(e)}")
                
                logger.debug(f"📥 Message delivered to {len(callbacks)} subscribers")
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Message Bus error: {str(e)}")
    
    async def stop(self):
        """메시지 버스 종료"""
        self.running = False
        logger.info("🛑 Message Bus stopped")
    
    def get_history(
        self,
        message_type: Optional[MessageType] = None,
        from_agent: Optional[str] = None,
        limit: int = 100
    ) -> List[AgentMessage]:
        """
        메시지 히스토리 조회
        
        Args:
            message_type: 메시지 타입 필터
            from_agent: 발신자 필터
            limit: 최대 개수
            
        Returns:
            list: 메시지 리스트
        """
        filtered = self.message_history
        
        if message_type:
            filtered = [m for m in filtered if m.message_type == message_type]
        
        if from_agent:
            filtered = [m for m in filtered if m.from_agent == from_agent]
        
        return filtered[-limit:]


# ============================================
# Base Agent Class
# ============================================

class BaseAgent(ABC):
    """
    모든 AI 에이전트의 기반 클래스
    
    공통 기능:
    - 메시지 버스 연동
    - 상태 관리
    - 로깅
    - 🆕 SUSPEND 모드 (긴급 상황)
    - 🆕 Profit-Cost Optimizer (수익 극대화)
    """
    
    def __init__(
        self,
        agent_name: str,
        message_bus: MessageBus,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        에이전트 초기화
        
        Args:
            agent_name: 에이전트 이름
            message_bus: 메시지 버스 인스턴스
            config: 설정
        """
        self.agent_name = agent_name
        self.message_bus = message_bus
        self.config = config or {}
        
        # 상태
        self.is_active = False
        self.is_suspended = False  # 🆕 SUSPEND 모드
        
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "tasks_completed": 0,
            "errors": 0,
            "started_at": None,
            # 🆕 수익 통계
            "total_profit": 0.0,
            "total_cost": 0.0,
            "profit_margin": 0.0
        }
        
        # 🆕 수익 최적화 설정
        self.profit_config = {
            "target_margin": 0.20,  # 목표 마진율 20%
            "min_margin": 0.10,  # 최소 마진율 10%
            "max_margin": 0.50,  # 최대 마진율 50%
            "cost_sensitivity": 1.0,  # 비용 민감도
            "revenue_priority": 1.0  # 매출 우선순위
        }
        
        # 메시지 핸들러 등록
        self._register_message_handlers()
        
        # 🆕 긴급 메시지 핸들러 등록
        self.message_bus.subscribe(
            MessageType.SENTINEL_ALERT,
            self._handle_sentinel_command
        )
        
        logger.info(f"✅ Agent '{agent_name}' initialized with Profit Optimizer")
    
    @abstractmethod
    def _register_message_handlers(self):
        """
        메시지 핸들러 등록 (각 에이전트가 구현)
        
        예:
        self.message_bus.subscribe(
            MessageType.ORDER_RECEIVED,
            self.handle_order_received
        )
        """
        pass
    
    @abstractmethod
    async def start(self):
        """에이전트 시작 (각 에이전트가 구현)"""
        self.is_active = True
        self.stats["started_at"] = datetime.now().isoformat()
        logger.info(f"🚀 Agent '{self.agent_name}' started")
    
    @abstractmethod
    async def stop(self):
        """에이전트 종료 (각 에이전트가 구현)"""
        self.is_active = False
        logger.info(f"🛑 Agent '{self.agent_name}' stopped")
    
    # ============================================
    # 🆕 SENTINEL PRIORITY INTERRUPT
    # ============================================
    
    async def _handle_sentinel_command(self, message: AgentMessage):
        """
        Sentinel 명령 처리
        
        SUSPEND: 모든 작업 중단, 자원 해제
        RESUME: 정상 작업 재개
        """
        try:
            command = message.payload.get("command")
            
            if command == "SUSPEND":
                await self._suspend()
            elif command == "RESUME":
                await self._resume()
            
        except Exception as e:
            logger.error(f"❌ Sentinel command error: {str(e)}")
    
    async def _suspend(self):
        """
        에이전트 일시 중단
        
        모든 비긴급 작업을 중단하고
        자원을 Sentinel에 반납
        """
        try:
            logger.warning(f"⏸️ Agent '{self.agent_name}' SUSPENDING...")
            
            self.is_suspended = True
            
            # 진행 중인 모든 비동기 작업 취소
            # (향후 구현: 실행 중인 태스크 추적 및 취소)
            
            # 메모리 정리
            # (향후 구현: 불필요한 캐시 삭제)
            
            logger.warning(f"⏸️ Agent '{self.agent_name}' SUSPENDED")
            
        except Exception as e:
            logger.error(f"❌ Suspend error: {str(e)}")
    
    async def _resume(self):
        """
        에이전트 재개
        
        정상 작업 재개
        """
        try:
            logger.info(f"▶️ Agent '{self.agent_name}' RESUMING...")
            
            self.is_suspended = False
            
            logger.info(f"▶️ Agent '{self.agent_name}' RESUMED")
            
        except Exception as e:
            logger.error(f"❌ Resume error: {str(e)}")
    
    # ============================================
    # 🆕 BUSINESS AGGRESSIVENESS (수익 극대화)
    # ============================================
    
    def calculate_optimal_price(
        self,
        base_cost: float,
        market_price: float,
        demand_level: float = 1.0,
        urgency: float = 1.0
    ) -> float:
        """
        최적 가격 계산 (수익 극대화)
        
        Args:
            base_cost: 기본 원가
            market_price: 시장 가격
            demand_level: 수요 수준 (0.0-2.0, 1.0=정상)
            urgency: 긴급도 (0.0-2.0, 1.0=정상)
            
        Returns:
            float: 최적 가격
        """
        try:
            # 기본 마진율
            target_margin = self.profit_config["target_margin"]
            min_margin = self.profit_config["min_margin"]
            max_margin = self.profit_config["max_margin"]
            
            # 수요에 따른 마진 조정
            # 수요 높음 → 마진 증가
            # 수요 낮음 → 마진 감소 (빠른 회전)
            demand_adjusted_margin = target_margin * demand_level
            
            # 긴급도에 따른 마진 조정
            # 긴급 → 마진 감소 (빠른 판매)
            urgency_adjusted_margin = demand_adjusted_margin / urgency
            
            # 최종 마진율 (범위 제한)
            final_margin = max(
                min_margin,
                min(max_margin, urgency_adjusted_margin)
            )
            
            # 최적 가격 계산
            optimal_price = base_cost * (1 + final_margin)
            
            # 시장 가격 대비 검증
            # 시장 가격보다 너무 높으면 조정
            if optimal_price > market_price * 1.3:
                optimal_price = market_price * 1.2
                final_margin = (optimal_price - base_cost) / base_cost
            
            logger.debug(f"💰 Optimal price: ₩{optimal_price:,.0f} (margin: {final_margin*100:.1f}%)")
            
            return optimal_price
            
        except Exception as e:
            logger.error(f"❌ Price calculation error: {str(e)}")
            # Fallback: 기본 마진 적용
            return base_cost * (1 + self.profit_config["target_margin"])
    
    def calculate_inventory_rotation_urgency(
        self,
        current_stock: int,
        days_until_expiry: Optional[int] = None,
        avg_daily_sales: float = 1.0
    ) -> float:
        """
        재고 회전 긴급도 계산
        
        손실(Loss) 최소화를 위한 재고 처리 우선순위
        
        Args:
            current_stock: 현재 재고량
            days_until_expiry: 유통기한까지 남은 일수
            avg_daily_sales: 일평균 판매량
            
        Returns:
            float: 긴급도 (0.0-2.0, 높을수록 긴급)
        """
        try:
            urgency = 1.0  # 기본값
            
            # 1. 유통기한 기반 긴급도
            if days_until_expiry is not None:
                if days_until_expiry <= 3:
                    urgency = 2.0  # 매우 긴급
                elif days_until_expiry <= 7:
                    urgency = 1.5  # 긴급
                elif days_until_expiry <= 14:
                    urgency = 1.2  # 약간 긴급
            
            # 2. 재고 과다 기반 긴급도
            if avg_daily_sales > 0:
                days_of_stock = current_stock / avg_daily_sales
                
                if days_of_stock > 30:
                    urgency = max(urgency, 1.8)  # 재고 과다
                elif days_of_stock > 14:
                    urgency = max(urgency, 1.3)
            
            logger.debug(f"📦 Inventory urgency: {urgency:.2f}")
            
            return urgency
            
        except Exception as e:
            logger.error(f"❌ Urgency calculation error: {str(e)}")
            return 1.0
    
    def calculate_delivery_cost_optimization(
        self,
        base_delivery_cost: float,
        distance_km: float,
        batch_size: int,
        time_sensitivity: float = 1.0
    ) -> Dict[str, float]:
        """
        배송 비용 최적화
        
        Args:
            base_delivery_cost: 기본 배송비
            distance_km: 거리 (km)
            batch_size: 배송 묶음 개수
            time_sensitivity: 시간 민감도 (1.0=정상, 2.0=긴급)
            
        Returns:
            dict: {
                "optimized_cost": 최적화된 배송비,
                "cost_per_item": 개당 배송비,
                "savings": 절감액
            }
        """
        try:
            # 거리 기반 비용
            distance_cost = distance_km * 100  # km당 100원
            
            # 묶음 배송 할인 (규모의 경제)
            batch_discount = 1.0 - (0.05 * min(batch_size - 1, 10))  # 최대 50% 할인
            
            # 시간 민감도 프리미엄
            time_premium = time_sensitivity
            
            # 최적화된 비용
            optimized_cost = (base_delivery_cost + distance_cost) * batch_discount * time_premium
            
            # 개당 비용
            cost_per_item = optimized_cost / batch_size
            
            # 절감액
            original_cost = (base_delivery_cost + distance_cost) * batch_size
            savings = original_cost - optimized_cost
            
            result = {
                "optimized_cost": round(optimized_cost, 0),
                "cost_per_item": round(cost_per_item, 0),
                "savings": round(savings, 0)
            }
            
            logger.debug(f"🚚 Delivery optimization: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Delivery cost optimization error: {str(e)}")
            return {
                "optimized_cost": base_delivery_cost,
                "cost_per_item": base_delivery_cost,
                "savings": 0.0
            }
    
    def update_profit_stats(self, revenue: float, cost: float):
        """
        수익 통계 업데이트
        
        Args:
            revenue: 매출
            cost: 비용
        """
        profit = revenue - cost
        
        self.stats["total_profit"] += profit
        self.stats["total_cost"] += cost
        
        total_revenue = self.stats["total_profit"] + self.stats["total_cost"]
        
        if total_revenue > 0:
            self.stats["profit_margin"] = self.stats["total_profit"] / total_revenue
        
        logger.debug(f"💰 Profit updated: ₩{profit:,.0f} (margin: {self.stats['profit_margin']*100:.1f}%)")
    
    async def send_message(
        self,
        message_type: MessageType,
        to_agent: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        priority: int = 5,
        requires_response: bool = False
    ):
        """
        메시지 발송
        
        🆕 SUSPEND 모드 체크 추가
        
        Args:
            message_type: 메시지 타입
            to_agent: 수신 에이전트 (None이면 브로드캐스트)
            payload: 메시지 내용
            priority: 우선순위 (1-10)
            requires_response: 응답 필요 여부
        """
        # SUSPEND 모드에서는 긴급 메시지만 발송
        if self.is_suspended and priority > 2:
            logger.warning(f"⏸️ Agent '{self.agent_name}' is suspended. Message blocked.")
            return
        
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            message_type=message_type,
            from_agent=self.agent_name,
            to_agent=to_agent,
            payload=payload or {},
            priority=priority,
            requires_response=requires_response
        )
        
        await self.message_bus.publish(message)
        self.stats["messages_sent"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """에이전트 통계 반환"""
        return {
            "agent_name": self.agent_name,
            "is_active": self.is_active,
            "is_suspended": self.is_suspended,  # 🆕
            "stats": self.stats,
            "config": self.config,
            "profit_margin": f"{self.stats['profit_margin']*100:.1f}%"  # 🆕
        }


# ============================================
# Agent Coordinator (Sentinel Interface)
# ============================================

class AgentCoordinator:
    """
    에이전트 코디네이터
    - 모든 에이전트 관리
    - Sentinel과의 인터페이스
    - 전체 시스템 상태 모니터링
    """
    
    def __init__(self, message_bus: MessageBus):
        """코디네이터 초기화"""
        self.message_bus = message_bus
        self.agents: Dict[str, BaseAgent] = {}
        
        # Sentinel 엔드포인트
        self.sentinel_endpoint = "https://sentinel.mulberry.kr/api/agent/report"
        
        logger.info("✅ Agent Coordinator initialized")
    
    def register_agent(self, agent: BaseAgent):
        """에이전트 등록"""
        self.agents[agent.agent_name] = agent
        logger.info(f"📋 Agent registered: {agent.agent_name}")
    
    async def start_all(self):
        """모든 에이전트 시작"""
        logger.info("🚀 Starting all agents...")
        
        for agent in self.agents.values():
            await agent.start()
        
        # 메시지 버스 시작
        asyncio.create_task(self.message_bus.start())
        
        logger.info("✅ All agents started")
    
    async def stop_all(self):
        """모든 에이전트 종료"""
        logger.info("🛑 Stopping all agents...")
        
        for agent in self.agents.values():
            await agent.stop()
        
        # 메시지 버스 종료
        await self.message_bus.stop()
        
        logger.info("✅ All agents stopped")
    
    def get_system_status(self) -> Dict[str, Any]:
        """전체 시스템 상태"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.is_active),
            "agents": {
                name: agent.get_stats()
                for name, agent in self.agents.items()
            },
            "message_bus": {
                "running": self.message_bus.running,
                "total_messages": len(self.message_bus.message_history),
                "subscribers": {
                    msg_type.value: len(callbacks)
                    for msg_type, callbacks in self.message_bus.subscribers.items()
                }
            }
        }
    
    async def report_to_sentinel(self):
        """
        Sentinel(Malu)에게 상태 보고
        
        정기적으로 호출하여 전체 시스템 상태 전송
        """
        try:
            status = self.get_system_status()
            
            # Sentinel API 호출 (향후 구현)
            logger.info(f"📊 Reporting to Sentinel: {status['active_agents']}/{status['total_agents']} agents active")
            
            # 실제로는 HTTP POST
            # response = await httpx.post(self.sentinel_endpoint, json=status)
            
        except Exception as e:
            logger.error(f"❌ Failed to report to Sentinel: {str(e)}")


# ============================================
# 싱글톤 인스턴스
# ============================================

_message_bus_instance: Optional[MessageBus] = None
_coordinator_instance: Optional[AgentCoordinator] = None


def get_message_bus() -> MessageBus:
    """싱글톤 메시지 버스"""
    global _message_bus_instance
    
    if _message_bus_instance is None:
        _message_bus_instance = MessageBus()
    
    return _message_bus_instance


def get_coordinator() -> AgentCoordinator:
    """싱글톤 코디네이터"""
    global _coordinator_instance
    
    if _coordinator_instance is None:
        _coordinator_instance = AgentCoordinator(get_message_bus())
    
    return _coordinator_instance


# ============================================
# 테스트용 샘플 에이전트
# ============================================

class TestAgent(BaseAgent):
    """테스트용 샘플 에이전트"""
    
    def _register_message_handlers(self):
        """메시지 핸들러 등록"""
        self.message_bus.subscribe(
            MessageType.ORDER_RECEIVED,
            self.handle_order
        )
    
    async def start(self):
        """시작"""
        await super().start()
        logger.info(f"🧪 Test Agent '{self.agent_name}' is ready")
    
    async def stop(self):
        """종료"""
        await super().stop()
    
    async def handle_order(self, message: AgentMessage):
        """주문 처리"""
        logger.info(f"📦 Test Agent received order: {message.payload}")
        self.stats["messages_received"] += 1
        self.stats["tasks_completed"] += 1


# ============================================
# 테스트
# ============================================

async def test_agent_system():
    """에이전트 시스템 테스트"""
    
    # 메시지 버스 생성
    bus = get_message_bus()
    
    # 코디네이터 생성
    coordinator = get_coordinator()
    
    # 테스트 에이전트 생성 및 등록
    agent1 = TestAgent("test_agent_1", bus)
    agent2 = TestAgent("test_agent_2", bus)
    
    coordinator.register_agent(agent1)
    coordinator.register_agent(agent2)
    
    # 모든 에이전트 시작
    await coordinator.start_all()
    
    # 테스트 메시지 발송
    await agent1.send_message(
        MessageType.ORDER_RECEIVED,
        payload={"order_id": 123, "items": ["사과", "배"]}
    )
    
    # 메시지 처리 대기
    await asyncio.sleep(2)
    
    # 시스템 상태 확인
    status = coordinator.get_system_status()
    logger.info(f"System Status: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    # 종료
    await coordinator.stop_all()


if __name__ == "__main__":
    asyncio.run(test_agent_system())

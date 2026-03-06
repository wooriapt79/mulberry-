"""
Mulberry Phase 3 - CRM Manager Agent
고객 관계 관리 및 맞춤형 추천
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger

from app.agents.base import BaseAgent, MessageBus, MessageType, AgentMessage


class CRMManagerAgent(BaseAgent):
    """
    CRM 관리 비서
    
    기능:
    - 어르신 구매 패턴 분석
    - 음성 특징 기록
    - "늘 먹던" 자동 추천
    - 단골 할인 관리
    """
    
    def __init__(self, message_bus: MessageBus, config: Optional[Dict[str, Any]] = None):
        """CRM Manager 초기화"""
        super().__init__(
            agent_name="CRM_Manager",
            message_bus=message_bus,
            config=config or {}
        )
        
        # 고객 프로필 (실제로는 DB)
        self.customer_profiles: Dict[str, Dict[str, Any]] = {}
        
        # 구매 이력
        self.purchase_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # 음성 특징 프로필
        self.voice_profiles: Dict[str, Dict[str, Any]] = {}
        
        # 단골 기준
        self.loyalty_tiers = {
            "bronze": {"min_orders": 3, "discount": 5},
            "silver": {"min_orders": 10, "discount": 10},
            "gold": {"min_orders": 30, "discount": 15},
            "platinum": {"min_orders": 50, "discount": 20}
        }
        
        logger.info("✅ CRM Manager initialized")
    
    def _register_message_handlers(self):
        """메시지 핸들러 등록"""
        # 주문 완료 → 구매 이력 업데이트
        self.message_bus.subscribe(
            MessageType.ORDER_COMPLETED,
            self.handle_order_completed
        )
        
        # 주문 접수 → 패턴 분석
        self.message_bus.subscribe(
            MessageType.ORDER_RECEIVED,
            self.handle_order_received
        )
    
    async def start(self):
        """CRM Manager 시작"""
        await super().start()
        
        # 정기 분석 작업 시작
        asyncio.create_task(self._run_periodic_analysis())
        
        logger.info("🚀 CRM Manager started with pattern analysis")
    
    async def stop(self):
        """CRM Manager 종료"""
        await super().stop()
    
    async def _run_periodic_analysis(self):
        """정기 고객 분석"""
        while self.is_active:
            try:
                # 매일 자정에 분석
                await asyncio.sleep(86400)
                
                await self.analyze_all_customers()
                
            except Exception as e:
                logger.error(f"❌ Periodic analysis error: {str(e)}")
    
    async def handle_order_received(self, message: AgentMessage):
        """
        주문 접수 처리 → 실시간 추천
        
        Payload:
        {
            "order_id": "...",
            "customer_phone": "010-1234-5678",
            "items": [...],
            "voice_features": {...}  # 음성 주문인 경우
        }
        """
        try:
            self.stats["messages_received"] += 1
            
            payload = message.payload
            customer_phone = payload.get("customer_phone")
            items = payload.get("items", [])
            voice_features = payload.get("voice_features")
            
            # 고객 프로필 확인/생성
            if customer_phone not in self.customer_profiles:
                await self.create_customer_profile(customer_phone)
            
            # 음성 특징 저장
            if voice_features:
                await self.update_voice_profile(customer_phone, voice_features)
            
            # 추천 생성 (구매 이력 기반)
            recommendations = await self.generate_recommendations(customer_phone)
            
            if recommendations:
                # 추천 발송
                await self.send_message(
                    MessageType.RECOMMENDATION_GENERATED,
                    to_agent="Sales_Agent",
                    payload={
                        "customer_phone": customer_phone,
                        "recommendations": recommendations
                    }
                )
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Order handling error: {str(e)}")
            self.stats["errors"] += 1
    
    async def handle_order_completed(self, message: AgentMessage):
        """
        주문 완료 처리 → 구매 이력 업데이트
        
        Payload:
        {
            "order_id": "...",
            "customer_phone": "010-1234-5678",
            "items": [...],
            "total_amount": 50000
        }
        """
        try:
            self.stats["messages_received"] += 1
            
            payload = message.payload
            customer_phone = payload.get("customer_phone")
            
            # 구매 이력 추가
            self.purchase_history[customer_phone].append({
                "order_id": payload.get("order_id"),
                "items": payload.get("items", []),
                "total_amount": payload.get("total_amount", 0),
                "completed_at": datetime.now().isoformat()
            })
            
            # 단골 등급 업데이트
            await self.update_loyalty_tier(customer_phone)
            
            # 구매 패턴 감지
            pattern = await self.detect_pattern(customer_phone)
            
            if pattern:
                await self.send_message(
                    MessageType.CUSTOMER_PATTERN_DETECTED,
                    payload={
                        "customer_phone": customer_phone,
                        "pattern": pattern
                    }
                )
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Order completion handling error: {str(e)}")
            self.stats["errors"] += 1
    
    async def create_customer_profile(self, customer_phone: str):
        """고객 프로필 생성"""
        self.customer_profiles[customer_phone] = {
            "phone": customer_phone,
            "created_at": datetime.now().isoformat(),
            "total_orders": 0,
            "total_spent": 0.0,
            "loyalty_tier": "bronze",
            "favorite_products": [],
            "last_order_date": None,
            "voice_recognized": False
        }
        
        logger.info(f"👤 Customer profile created: {customer_phone}")
    
    async def update_voice_profile(self, customer_phone: str, voice_features: Dict[str, Any]):
        """
        음성 특징 프로필 업데이트
        
        어르신의 목소리 특징을 저장하여
        향후 음성으로 고객 식별 가능
        """
        if customer_phone not in self.voice_profiles:
            self.voice_profiles[customer_phone] = {
                "samples": [],
                "avg_pitch_hz": 0,
                "avg_volume_db": 0,
                "avg_speech_rate": 0
            }
        
        profile = self.voice_profiles[customer_phone]
        
        # 샘플 추가
        profile["samples"].append(voice_features)
        
        # 평균 계산 (최근 10개 샘플)
        recent_samples = profile["samples"][-10:]
        
        profile["avg_pitch_hz"] = sum(s.get("pitch_hz", 0) for s in recent_samples) / len(recent_samples)
        profile["avg_volume_db"] = sum(s.get("volume_db", 0) for s in recent_samples) / len(recent_samples)
        profile["avg_speech_rate"] = sum(s.get("speech_rate", 0) for s in recent_samples) / len(recent_samples)
        
        # 고객 프로필 업데이트
        self.customer_profiles[customer_phone]["voice_recognized"] = True
        
        logger.info(f"🎙️ Voice profile updated: {customer_phone}")
    
    async def update_loyalty_tier(self, customer_phone: str):
        """단골 등급 업데이트"""
        if customer_phone not in self.customer_profiles:
            return
        
        profile = self.customer_profiles[customer_phone]
        total_orders = len(self.purchase_history.get(customer_phone, []))
        
        # 등급 결정
        new_tier = "bronze"
        
        for tier_name, tier_info in sorted(
            self.loyalty_tiers.items(),
            key=lambda x: x[1]["min_orders"],
            reverse=True
        ):
            if total_orders >= tier_info["min_orders"]:
                new_tier = tier_name
                break
        
        old_tier = profile.get("loyalty_tier")
        
        if new_tier != old_tier:
            profile["loyalty_tier"] = new_tier
            logger.info(f"🏆 Loyalty tier upgraded: {customer_phone} {old_tier} → {new_tier}")
            
            # 축하 메시지 (향후 SMS/알림)
    
    async def detect_pattern(self, customer_phone: str) -> Optional[Dict[str, Any]]:
        """
        구매 패턴 감지
        
        Returns:
            dict: 패턴 정보 (None이면 패턴 없음)
        """
        history = self.purchase_history.get(customer_phone, [])
        
        if len(history) < 3:
            return None  # 최소 3개 주문 필요
        
        # 최근 주문들의 상품 빈도 분석
        product_counts = defaultdict(int)
        
        for order in history[-10:]:  # 최근 10개 주문
            for item in order.get("items", []):
                product_name = item.get("product_name") or item.get("product")
                if product_name:
                    product_counts[product_name] += 1
        
        # 가장 많이 주문한 상품
        if not product_counts:
            return None
        
        favorite_product = max(product_counts, key=product_counts.get)
        frequency = product_counts[favorite_product]
        
        if frequency >= 3:  # 3번 이상 주문
            return {
                "type": "favorite_product",
                "product": favorite_product,
                "frequency": frequency,
                "customer_phone": customer_phone
            }
        
        # 정기 주문 패턴 감지 (향후 구현)
        # 예: 매주 토요일 사과 주문
        
        return None
    
    async def generate_recommendations(self, customer_phone: str) -> List[Dict[str, Any]]:
        """
        맞춤형 추천 생성
        
        Args:
            customer_phone: 고객 전화번호
            
        Returns:
            list: 추천 상품 리스트
        """
        recommendations = []
        
        # 구매 이력 확인
        history = self.purchase_history.get(customer_phone, [])
        
        if not history:
            return []
        
        # 최근 주문 분석
        recent_orders = history[-5:]  # 최근 5개 주문
        
        # 자주 구매하는 상품
        product_counts = defaultdict(int)
        
        for order in recent_orders:
            for item in order.get("items", []):
                product_name = item.get("product_name") or item.get("product")
                if product_name:
                    product_counts[product_name] += 1
        
        # 추천 생성
        for product, count in sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
            recommendations.append({
                "product": product,
                "reason": f"자주 구매하신 상품입니다 ({count}회)",
                "priority": count
            })
        
        logger.info(f"✅ Generated {len(recommendations)} recommendations for {customer_phone}")
        
        return recommendations
    
    async def handle_voice_query(
        self,
        customer_phone: str,
        query_text: str
    ) -> Optional[Dict[str, Any]]:
        """
        음성 쿼리 처리
        
        "늘 먹던 사과" → 과거 이력에서 사과 찾아서 추천
        
        Args:
            customer_phone: 고객 전화번호
            query_text: 음성 인식 텍스트
            
        Returns:
            dict: 추천 결과
        """
        try:
            # "늘 먹던", "항상 사는", "지난번에" 등 키워드 감지
            keywords = ["늘 먹던", "항상", "지난번", "전에 먹던", "늘 주문하던"]
            
            is_regular_order = any(keyword in query_text for keyword in keywords)
            
            if not is_regular_order:
                return None
            
            # 가장 자주 주문한 상품 찾기
            history = self.purchase_history.get(customer_phone, [])
            
            if not history:
                return None
            
            product_counts = defaultdict(int)
            
            for order in history:
                for item in order.get("items", []):
                    product_name = item.get("product_name") or item.get("product")
                    if product_name:
                        product_counts[product_name] += 1
            
            if not product_counts:
                return None
            
            # 가장 많이 주문한 상품
            favorite_product = max(product_counts, key=product_counts.get)
            
            # 마지막 주문 정보
            last_order_item = None
            for order in reversed(history):
                for item in order.get("items", []):
                    if (item.get("product_name") or item.get("product")) == favorite_product:
                        last_order_item = item
                        break
                if last_order_item:
                    break
            
            recommendation = {
                "product": favorite_product,
                "quantity": last_order_item.get("quantity", 1) if last_order_item else 1,
                "unit": last_order_item.get("unit", "개") if last_order_item else "개",
                "reason": f"늘 주문하시던 {favorite_product}입니다",
                "auto_fill": True  # 자동으로 장바구니에 추가
            }
            
            logger.info(f"🎯 Voice query matched: {query_text} → {favorite_product}")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"❌ Voice query handling error: {str(e)}")
            return None
    
    async def analyze_all_customers(self):
        """전체 고객 분석 (일일 작업)"""
        try:
            logger.info("📊 Analyzing all customers...")
            
            total_customers = len(self.customer_profiles)
            active_customers = 0
            
            for phone, profile in self.customer_profiles.items():
                # 활성 고객 (최근 30일 내 주문)
                last_order = profile.get("last_order_date")
                
                if last_order:
                    last_order_dt = datetime.fromisoformat(last_order)
                    if (datetime.now() - last_order_dt).days <= 30:
                        active_customers += 1
            
            # Strategy Advisor에게 보고
            await self.send_message(
                MessageType.METRICS_UPDATE,
                to_agent="Strategy_Advisor",
                payload={
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "total_customers": total_customers,
                    "active_customers": active_customers,
                    "loyalty_distribution": self._get_loyalty_distribution()
                }
            )
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Customer analysis error: {str(e)}")
    
    def _get_loyalty_distribution(self) -> Dict[str, int]:
        """단골 등급별 고객 수"""
        distribution = defaultdict(int)
        
        for profile in self.customer_profiles.values():
            tier = profile.get("loyalty_tier", "bronze")
            distribution[tier] += 1
        
        return dict(distribution)


# ============================================
# 싱글톤 인스턴스
# ============================================

_crm_manager_instance: Optional[CRMManagerAgent] = None


def get_crm_manager(message_bus: MessageBus) -> CRMManagerAgent:
    """싱글톤 CRM Manager"""
    global _crm_manager_instance
    
    if _crm_manager_instance is None:
        _crm_manager_instance = CRMManagerAgent(message_bus)
    
    return _crm_manager_instance

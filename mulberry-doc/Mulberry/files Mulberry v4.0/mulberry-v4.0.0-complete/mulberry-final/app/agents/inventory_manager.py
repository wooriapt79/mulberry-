"""
Mulberry Phase 3 - Inventory Manager Agent
실시간 재고 관리 및 프로모션 트리거
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.agents.base import BaseAgent, MessageBus, MessageType, AgentMessage
from app.services import get_delivery_optimizer


class InventoryManagerAgent(BaseAgent):
    """
    재고 관리 비서
    
    기능:
    - 농가별 실시간 재고 파악
    - 품절 임박 시 프로모션 요청
    - 재고 예측 (AI 기반)
    - 배송 최적화 연동
    """
    
    def __init__(self, message_bus: MessageBus, config: Optional[Dict[str, Any]] = None):
        """Inventory Manager 초기화"""
        super().__init__(
            agent_name="Inventory_Manager",
            message_bus=message_bus,
            config=config or {}
        )
        
        # 배송 최적화 서비스
        self.delivery_optimizer = get_delivery_optimizer()
        
        # 재고 데이터 (실제로는 DB 연동)
        self.inventory: Dict[int, Dict[str, Any]] = {}
        
        # 재고 임계값 설정
        self.thresholds = {
            "critical": 10,  # 10개 이하: 긴급
            "low": 30,  # 30개 이하: 프로모션
            "optimal": 100  # 100개 이상: 정상
        }
        
        # 재고 예측 모델 (간단한 이동평균)
        self.sales_history: Dict[int, List[float]] = {}
        
        logger.info("✅ Inventory Manager initialized")
    
    def _register_message_handlers(self):
        """메시지 핸들러 등록"""
        # 주문 접수 → 재고 감소
        self.message_bus.subscribe(
            MessageType.ORDER_RECEIVED,
            self.handle_order_received
        )
        
        # 재고 업데이트 (수확 등)
        self.message_bus.subscribe(
            MessageType.INVENTORY_UPDATE,
            self.handle_inventory_update
        )
    
    async def start(self):
        """Inventory Manager 시작"""
        await super().start()
        
        # 정기 재고 체크 시작
        asyncio.create_task(self._run_inventory_monitor())
        
        logger.info("🚀 Inventory Manager started with real-time monitoring")
    
    async def stop(self):
        """Inventory Manager 종료"""
        await super().stop()
    
    async def _run_inventory_monitor(self):
        """실시간 재고 모니터링"""
        while self.is_active:
            try:
                # 10분마다 재고 체크
                await asyncio.sleep(600)
                
                await self.check_all_inventories()
                
            except Exception as e:
                logger.error(f"❌ Inventory monitor error: {str(e)}")
    
    async def check_all_inventories(self):
        """
        모든 농장 재고 확인
        
        🆕 Business Aggressiveness 적용:
        - 재고 회전율 계산
        - 손실 최소화 전략
        - 긴급도 기반 프로모션 트리거
        """
        try:
            logger.info("📊 Checking all inventories...")
            
            # DB에서 재고 조회 (향후 구현)
            # 여기서는 샘플 데이터
            
            for farm_id, stock_data in self.inventory.items():
                for product, quantity in stock_data.items():
                    
                    # ============================================
                    # 🆕 BUSINESS AGGRESSIVENESS: 재고 회전율 최적화
                    # ============================================
                    
                    # 1. 일평균 판매량 조회
                    sales_key = f"{farm_id}_{product}"
                    avg_daily_sales = 5.0  # 샘플 (실제로는 판매 이력에서 계산)
                    
                    # 2. 유통기한 조회 (실제로는 DB에서)
                    days_until_expiry = None
                    
                    if product in ["사과", "배", "복숭아"]:  # 과일
                        days_until_expiry = 14  # 2주
                    elif product in ["배추", "무"]:  # 채소
                        days_until_expiry = 7  # 1주
                    
                    # 3. 재고 회전 긴급도 계산
                    urgency = self.calculate_inventory_rotation_urgency(
                        current_stock=quantity,
                        days_until_expiry=days_until_expiry,
                        avg_daily_sales=avg_daily_sales
                    )
                    
                    # 4. 재고 수준 판단
                    level = self._get_inventory_level(quantity)
                    
                    # 5. 손실 위험 계산
                    if days_until_expiry and avg_daily_sales > 0:
                        days_of_stock = quantity / avg_daily_sales
                        
                        # 손실 위험 = 재고 > 유통기한 내 판매 가능량
                        if days_of_stock > days_until_expiry:
                            potential_loss = (days_of_stock - days_until_expiry) * avg_daily_sales
                            loss_value = potential_loss * 5000  # 샘플 단가
                            
                            logger.warning(
                                f"⚠️ Loss risk: Farm {farm_id} - {product} "
                                f"{int(potential_loss)}개 폐기 예상 (₩{loss_value:,.0f})"
                            )
                            
                            # 손실 방지를 위한 긴급 프로모션
                            if potential_loss > 10:
                                await self._trigger_loss_prevention_sale(
                                    farm_id=farm_id,
                                    product=product,
                                    quantity=int(potential_loss),
                                    urgency=2.0,  # 매우 긴급
                                    discount_rate=30  # 30% 할인
                                )
                    
                    # ============================================
                    
                    # 6. 일반 재고 수준 체크
                    if level == "critical":
                        # 긴급 재고 부족
                        logger.warning(f"🚨 CRITICAL: Farm {farm_id} - {product} only {quantity} left!")
                        
                        await self.send_message(
                            MessageType.INVENTORY_LOW,
                            payload={
                                "farm_id": farm_id,
                                "product": product,
                                "quantity_left": quantity,
                                "level": "critical",
                                "urgency": urgency
                            },
                            priority=1  # 최고 우선순위
                        )
                        
                    elif level == "low":
                        # 프로모션 필요
                        logger.info(f"⚠️ LOW: Farm {farm_id} - {product} {quantity} left, triggering promotion")
                        
                        # 긴급도에 따른 할인율 결정
                        discount_rate = self._calculate_discount_rate(urgency)
                        
                        await self.send_message(
                            MessageType.PROMOTION_REQUEST,
                            to_agent="Sales_Agent",
                            payload={
                                "farm_id": farm_id,
                                "product": product,
                                "quantity_left": quantity,
                                "level": "low",
                                "urgency": urgency,
                                "recommended_discount": discount_rate
                            },
                            priority=3
                        )
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Inventory check error: {str(e)}")
            self.stats["errors"] += 1
    
    def _calculate_discount_rate(self, urgency: float) -> int:
        """
        긴급도 기반 할인율 계산
        
        Args:
            urgency: 긴급도 (0.0-2.0)
            
        Returns:
            int: 할인율 (%)
        """
        if urgency >= 1.8:
            return 30  # 30% 할인
        elif urgency >= 1.5:
            return 25  # 25% 할인
        elif urgency >= 1.2:
            return 20  # 20% 할인
        else:
            return 10  # 10% 할인
    
    async def _trigger_loss_prevention_sale(
        self,
        farm_id: int,
        product: str,
        quantity: int,
        urgency: float,
        discount_rate: int
    ):
        """
        손실 방지 긴급 세일
        
        유통기한 임박 상품을 빠르게 처리하여 손실 최소화
        
        Args:
            farm_id: 농장 ID
            product: 상품명
            quantity: 수량
            urgency: 긴급도
            discount_rate: 할인율
        """
        try:
            logger.warning(
                f"🔥 LOSS PREVENTION SALE: {product} {quantity}개 "
                f"{discount_rate}% 할인 (urgency: {urgency:.1f})"
            )
            
            # Sales Agent에게 긴급 할인 요청
            await self.send_message(
                MessageType.PROMOTION_REQUEST,
                to_agent="Sales_Agent",
                payload={
                    "farm_id": farm_id,
                    "product": product,
                    "quantity_left": quantity,
                    "level": "loss_prevention",
                    "urgency": urgency,
                    "recommended_discount": discount_rate,
                    "reason": f"유통기한 임박! 폐기 방지 긴급 세일"
                },
                priority=2  # 매우 높은 우선순위
            )
            
            # SNS Manager에게 홍보 요청
            await self.send_message(
                MessageType.PROMOTION_REQUEST,
                to_agent="SNS_Manager",
                payload={
                    "farm_id": farm_id,
                    "product": product,
                    "discount_rate": discount_rate,
                    "quantity": quantity,
                    "reason": f"🔥 긴급! 신선할 때 드세요! {discount_rate}% 대할인"
                },
                priority=2
            )
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Loss prevention sale error: {str(e)}")
    
    def _get_inventory_level(self, quantity: int) -> str:
        """
        재고 수준 판단
        
        Args:
            quantity: 현재 재고량
            
        Returns:
            str: critical, low, optimal
        """
        if quantity <= self.thresholds["critical"]:
            return "critical"
        elif quantity <= self.thresholds["low"]:
            return "low"
        else:
            return "optimal"
    
    async def handle_order_received(self, message: AgentMessage):
        """
        주문 접수 처리 → 재고 감소
        
        Payload:
        {
            "order_id": "ORD20240211...",
            "farm_id": 1,
            "items": [
                {"product": "사과", "quantity": 10}
            ]
        }
        """
        try:
            self.stats["messages_received"] += 1
            
            payload = message.payload
            farm_id = payload.get("farm_id")
            items = payload.get("items", [])
            
            for item in items:
                product = item.get("product_name") or item.get("product")
                quantity = item.get("quantity", 0)
                
                # 재고 감소
                await self.decrease_inventory(farm_id, product, quantity)
            
            # 배송 최적화 연동
            await self._optimize_delivery_route(payload)
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Order handling error: {str(e)}")
            self.stats["errors"] += 1
    
    async def handle_inventory_update(self, message: AgentMessage):
        """
        재고 업데이트 처리 (수확, 입고 등)
        
        Payload:
        {
            "farm_id": 1,
            "product": "사과",
            "quantity": 100,
            "operation": "add"  # add or set
        }
        """
        try:
            self.stats["messages_received"] += 1
            
            payload = message.payload
            farm_id = payload.get("farm_id")
            product = payload.get("product")
            quantity = payload.get("quantity")
            operation = payload.get("operation", "add")
            
            if operation == "add":
                await self.increase_inventory(farm_id, product, quantity)
            else:
                await self.set_inventory(farm_id, product, quantity)
            
            logger.info(f"✅ Inventory updated: Farm {farm_id} - {product} = {quantity}")
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Inventory update error: {str(e)}")
            self.stats["errors"] += 1
    
    async def decrease_inventory(self, farm_id: int, product: str, quantity: int):
        """재고 감소"""
        if farm_id not in self.inventory:
            self.inventory[farm_id] = {}
        
        current = self.inventory[farm_id].get(product, 0)
        new_quantity = max(0, current - quantity)
        self.inventory[farm_id][product] = new_quantity
        
        logger.info(f"📉 Inventory decreased: Farm {farm_id} - {product}: {current} → {new_quantity}")
        
        # 재고 수준 체크
        level = self._get_inventory_level(new_quantity)
        
        if level == "critical":
            await self.send_message(
                MessageType.INVENTORY_LOW,
                payload={
                    "farm_id": farm_id,
                    "product": product,
                    "quantity_left": new_quantity,
                    "level": "critical"
                },
                priority=1
            )
    
    async def increase_inventory(self, farm_id: int, product: str, quantity: int):
        """재고 증가"""
        if farm_id not in self.inventory:
            self.inventory[farm_id] = {}
        
        current = self.inventory[farm_id].get(product, 0)
        new_quantity = current + quantity
        self.inventory[farm_id][product] = new_quantity
        
        logger.info(f"📈 Inventory increased: Farm {farm_id} - {product}: {current} → {new_quantity}")
    
    async def set_inventory(self, farm_id: int, product: str, quantity: int):
        """재고 설정"""
        if farm_id not in self.inventory:
            self.inventory[farm_id] = {}
        
        self.inventory[farm_id][product] = quantity
        
        logger.info(f"📊 Inventory set: Farm {farm_id} - {product} = {quantity}")
    
    async def _optimize_delivery_route(self, order_data: Dict[str, Any]):
        """
        배송 경로 최적화
        
        Phase 2의 delivery_optimizer와 연동
        """
        try:
            order_id = order_data.get("order_id")
            farm_id = order_data.get("farm_id")
            delivery_address = order_data.get("delivery_address")
            
            logger.info(f"🚚 Optimizing delivery route for order {order_id}")
            
            # 배송 최적화 (향후 실제 위치 데이터로 구현)
            # route = await self.delivery_optimizer.find_optimal_route(
            #     start_location_id=f"farm_{farm_id}",
            #     end_location_id="customer_location"
            # )
            
            # 배송 예정 시간 계산 등
            
        except Exception as e:
            logger.error(f"❌ Delivery optimization error: {str(e)}")
    
    async def predict_stockout(self, farm_id: int, product: str) -> Optional[datetime]:
        """
        재고 소진 예측 (간단한 이동평균 기반)
        
        Args:
            farm_id: 농장 ID
            product: 상품명
            
        Returns:
            datetime: 예상 재고 소진 시각 (None이면 충분)
        """
        try:
            # 현재 재고
            current_stock = self.inventory.get(farm_id, {}).get(product, 0)
            
            if current_stock == 0:
                return datetime.now()
            
            # 판매 이력 (최근 7일)
            sales_key = f"{farm_id}_{product}"
            recent_sales = self.sales_history.get(sales_key, [])
            
            if not recent_sales:
                return None  # 데이터 부족
            
            # 일평균 판매량
            avg_daily_sales = sum(recent_sales) / len(recent_sales)
            
            if avg_daily_sales == 0:
                return None  # 판매 없음
            
            # 예상 소진 일수
            days_until_stockout = current_stock / avg_daily_sales
            
            stockout_date = datetime.now() + timedelta(days=days_until_stockout)
            
            logger.info(f"📊 Stockout prediction: {product} at farm {farm_id} in {days_until_stockout:.1f} days")
            
            return stockout_date
            
        except Exception as e:
            logger.error(f"❌ Prediction error: {str(e)}")
            return None
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """재고 요약"""
        total_farms = len(self.inventory)
        
        critical_items = []
        low_items = []
        
        for farm_id, stock_data in self.inventory.items():
            for product, quantity in stock_data.items():
                level = self._get_inventory_level(quantity)
                
                if level == "critical":
                    critical_items.append({
                        "farm_id": farm_id,
                        "product": product,
                        "quantity": quantity
                    })
                elif level == "low":
                    low_items.append({
                        "farm_id": farm_id,
                        "product": product,
                        "quantity": quantity
                    })
        
        return {
            "total_farms": total_farms,
            "critical_items": len(critical_items),
            "low_items": len(low_items),
            "critical_details": critical_items,
            "low_details": low_items
        }


# ============================================
# 싱글톤 인스턴스
# ============================================

_inventory_manager_instance: Optional[InventoryManagerAgent] = None


def get_inventory_manager(message_bus: MessageBus) -> InventoryManagerAgent:
    """싱글톤 Inventory Manager"""
    global _inventory_manager_instance
    
    if _inventory_manager_instance is None:
        _inventory_manager_instance = InventoryManagerAgent(message_bus)
    
    return _inventory_manager_instance

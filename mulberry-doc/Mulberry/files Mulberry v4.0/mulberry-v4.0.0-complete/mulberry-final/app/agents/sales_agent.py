"""
Mulberry Phase 3 - Sales Agent
주문 접수 및 리뷰 자동 답변
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from app.agents.base import BaseAgent, MessageBus, MessageType, AgentMessage
from app.services import get_google_service, get_qwen_service


class SalesAgent(BaseAgent):
    """
    영업 비서
    
    기능:
    - 거점 매장 주문 접수
    - 구글 리뷰 자동 답변 (농장주 말투)
    - 고객 문의 응대
    - 프로모션 실행
    - 🆕 Store_Mode / Home_Mode 구분
    """
    
    def __init__(self, message_bus: MessageBus, config: Optional[Dict[str, Any]] = None):
        """Sales Agent 초기화"""
        super().__init__(
            agent_name="Sales_Agent",
            message_bus=message_bus,
            config=config or {}
        )
        
        # Google Business 서비스
        self.google = get_google_service()
        
        # Qwen 서비스
        self.qwen = get_qwen_service()
        
        # 주문 통계
        self.order_stats = {
            "total_orders_today": 0,
            "total_revenue_today": 0.0,
            "pending_orders": 0,
            "completed_orders": 0
        }
        
        # 농장주 말투 프로필
        self.farmer_profiles = self._load_farmer_profiles()
        
        # ============================================
        # 🆕 거점 매장 전용 영업 모드
        # ============================================
        
        # 운영 모드: "store" (하나로마트 등) 또는 "home" (개인 가정)
        self.operation_mode = config.get("operation_mode", "store")
        
        # Store Mode 설정
        self.store_mode_config = {
            # 개인정보 보호
            "mask_customer_phone": True,  # 전화번호 마스킹 (010-****-5678)
            "mask_customer_name": True,  # 이름 마스킹 (김**)
            
            # 음성 출력 제한
            "voice_output_enabled": False,  # 공공장소에서 음성 출력 금지
            "text_display_only": True,  # 텍스트 화면 표시만
            
            # 점원 알림
            "clerk_notification_enabled": True,  # 점원 Push 알림
            "notification_channels": ["push", "display"],  # push, sms, display
            
            # 보안
            "log_customer_data": False,  # 고객 데이터 로그 최소화
            "auto_delete_after_hours": 24,  # 24시간 후 자동 삭제
        }
        
        # Home Mode 설정
        self.home_mode_config = {
            "voice_output_enabled": True,  # 가정에서는 음성 출력 허용
            "full_customer_info": True,  # 전체 고객 정보 표시
            "log_customer_data": True,  # 로그 보관
        }
        
        logger.info(f"✅ Sales Agent initialized (Mode: {self.operation_mode})")
    
    def _get_mode_config(self) -> Dict[str, Any]:
        """현재 운영 모드 설정 반환"""
        if self.operation_mode == "store":
            return self.store_mode_config
        else:
            return self.home_mode_config
    
    def _mask_customer_phone(self, phone: str) -> str:
        """
        전화번호 마스킹 (개인정보 보호)
        
        Args:
            phone: 010-1234-5678
            
        Returns:
            str: 010-****-5678
        """
        if not self._get_mode_config().get("mask_customer_phone", False):
            return phone
        
        # 010-1234-5678 → 010-****-5678
        parts = phone.split("-")
        if len(parts) == 3:
            return f"{parts[0]}-****-{parts[2]}"
        return phone
    
    def _mask_customer_name(self, name: str) -> str:
        """
        이름 마스킹 (개인정보 보호)
        
        Args:
            name: 김철수
            
        Returns:
            str: 김**
        """
        if not self._get_mode_config().get("mask_customer_name", False):
            return name
        
        # 김철수 → 김**
        if len(name) >= 2:
            return name[0] + "*" * (len(name) - 1)
        return name
    
    async def _send_clerk_notification(
        self,
        order_data: Dict[str, Any],
        notification_type: str = "new_order"
    ):
        """
        점원에게 Push 알림 전송
        
        Args:
            order_data: 주문 데이터
            notification_type: new_order, cancel, urgent
        """
        try:
            mode_config = self._get_mode_config()
            
            if not mode_config.get("clerk_notification_enabled", False):
                return
            
            # 알림 메시지 구성
            masked_phone = self._mask_customer_phone(order_data.get("customer_phone", ""))
            masked_name = self._mask_customer_name(order_data.get("customer_name", "고객"))
            
            if notification_type == "new_order":
                message = f"""
📦 새 주문 접수!

고객: {masked_name} ({masked_phone})
주문 번호: {order_data.get('order_id')}
금액: ₩{order_data.get('total_revenue', 0):,.0f}
항목: {len(order_data.get('items', []))}개

→ 화면을 확인해주세요.
"""
            elif notification_type == "urgent":
                message = f"""
🚨 긴급 주문!

고객: {masked_name}
주문 번호: {order_data.get('order_id')}
배송 희망: 오늘 중

→ 즉시 확인 필요!
"""
            else:
                message = f"알림: {notification_type}"
            
            # Push 알림 전송 (실제로는 FCM, APNs 등)
            channels = mode_config.get("notification_channels", ["push"])
            
            if "push" in channels:
                # Push notification 전송
                logger.info(f"📲 Push notification sent to clerk")
                # await self._send_push_notification(message)
            
            if "display" in channels:
                # 화면 알림 (점원용 디스플레이)
                logger.info(f"🖥️ Display notification: {message}")
            
            logger.info(f"✅ Clerk notification sent ({notification_type})")
            
        except Exception as e:
            logger.error(f"❌ Clerk notification error: {str(e)}")
    
    def _load_farmer_profiles(self) -> Dict[int, Dict[str, str]]:
        """
        농장주별 말투 프로필
        
        실제로는 DB에서 로드
        """
        return {
            1: {  # 푸른골농원
                "name": "김철수",
                "tone": "따뜻하고 정겹게",
                "signature": "항상 건강한 먹거리로 보답하겠습니다!",
                "greeting": "안녕하세요~ 푸른골농원 김철수입니다 😊"
            },
            2: {  # 청정농장
                "name": "박영희",
                "tone": "친절하고 상냥하게",
                "signature": "믿고 드실 수 있는 농산물을 만들겠습니다.",
                "greeting": "안녕하세요! 청정농장 박영희예요 ^^"
            }
        }
    
    def _register_message_handlers(self):
        """메시지 핸들러 등록"""
        # 프로모션 요청 처리
        self.message_bus.subscribe(
            MessageType.PROMOTION_REQUEST,
            self.handle_promotion_request
        )
        
        # 재고 부족 알림 → 대체 상품 제안
        self.message_bus.subscribe(
            MessageType.INVENTORY_LOW,
            self.handle_low_inventory
        )
    
    async def start(self):
        """Sales Agent 시작"""
        await super().start()
        
        # 정기 작업 시작
        asyncio.create_task(self._run_periodic_tasks())
        
        logger.info("🚀 Sales Agent started with auto-response enabled")
    
    async def stop(self):
        """Sales Agent 종료"""
        await super().stop()
    
    async def _run_periodic_tasks(self):
        """정기 작업 (리뷰 체크, 통계 업데이트 등)"""
        while self.is_active:
            try:
                # 1시간마다 실행
                await asyncio.sleep(3600)
                
                # 새 리뷰 확인 및 자동 답변
                await self.check_and_reply_reviews()
                
                # 일일 통계 업데이트
                await self.update_daily_stats()
                
            except Exception as e:
                logger.error(f"❌ Periodic task error: {str(e)}")
    
    async def process_order(
        self,
        customer_phone: str,
        farm_id: int,
        items: List[Dict[str, Any]],
        delivery_address: str
    ) -> Dict[str, Any]:
        """
        주문 처리
        
        🆕 Business Aggressiveness 적용:
        - 동적 가격 책정 (시장가, 수요, 긴급도 고려)
        - 최적 마진 계산
        - 배송비 최적화
        
        Args:
            customer_phone: 고객 전화번호
            farm_id: 농장 ID
            items: 주문 항목
            delivery_address: 배송 주소
            
        Returns:
            dict: 주문 결과
        """
        try:
            logger.info(f"📦 Processing order from {customer_phone}")
            
            # 주문 번호 생성
            order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # ============================================
            # 🆕 BUSINESS AGGRESSIVENESS: 동적 가격 책정
            # ============================================
            
            total_cost = 0.0  # 원가
            total_revenue = 0.0  # 매출
            optimized_items = []
            
            for item in items:
                product = item.get("product_name") or item.get("product")
                quantity = item.get("quantity", 0)
                base_unit_price = item.get("unit_price", 0)  # 기본 원가
                
                # 1. 시장 가격 조회 (실제로는 DB에서)
                market_price = base_unit_price * 1.3  # 샘플: 원가의 130%
                
                # 2. 수요 수준 판단 (재고 기반)
                # Inventory Manager로부터 받은 재고 정보 활용
                demand_level = 1.0  # 기본값
                
                # 재고가 적으면 수요 높다고 판단 → 가격 인상
                # (향후: Inventory Manager와 연동)
                
                # 3. 긴급도 (재고 회전율)
                urgency = 1.0  # 기본값
                
                # 4. 최적 가격 계산
                optimal_price = self.calculate_optimal_price(
                    base_cost=base_unit_price,
                    market_price=market_price,
                    demand_level=demand_level,
                    urgency=urgency
                )
                
                # 5. 총 비용 및 매출 계산
                item_cost = base_unit_price * quantity
                item_revenue = optimal_price * quantity
                
                total_cost += item_cost
                total_revenue += item_revenue
                
                optimized_items.append({
                    "product": product,
                    "quantity": quantity,
                    "unit_price": optimal_price,  # 최적 가격
                    "base_cost": base_unit_price,
                    "margin": ((optimal_price - base_unit_price) / base_unit_price) * 100,
                    "subtotal": item_revenue
                })
                
                logger.info(f"💰 {product}: ₩{base_unit_price:,.0f} → ₩{optimal_price:,.0f} (margin: {((optimal_price - base_unit_price) / base_unit_price) * 100:.1f}%)")
            
            # 6. 배송비 최적화
            delivery_cost_result = self.calculate_delivery_cost_optimization(
                base_delivery_cost=3000,  # 기본 3천원
                distance_km=10.0,  # 샘플 거리
                batch_size=len(items),
                time_sensitivity=1.0
            )
            
            delivery_cost = delivery_cost_result["optimized_cost"]
            total_cost += delivery_cost
            total_revenue += delivery_cost  # 배송비도 매출에 포함
            
            # 7. 최종 금액
            final_amount = total_revenue
            total_profit = total_revenue - total_cost
            profit_margin = (total_profit / total_revenue) * 100 if total_revenue > 0 else 0
            
            logger.info(f"💰 Order profit: ₩{total_profit:,.0f} (margin: {profit_margin:.1f}%)")
            
            # 8. 수익 통계 업데이트
            self.update_profit_stats(revenue=total_revenue, cost=total_cost)
            
            # ============================================
            
            # 주문 데이터
            order_data = {
                "order_id": order_id,
                "customer_phone": customer_phone,
                "customer_name": "고객님",  # 실제로는 DB에서 조회
                "farm_id": farm_id,
                "items": optimized_items,
                "delivery_address": delivery_address,
                "delivery_cost": delivery_cost,
                "delivery_optimization": delivery_cost_result,
                "total_cost": total_cost,  # 원가
                "total_revenue": total_revenue,  # 매출
                "total_profit": total_profit,  # 이익
                "profit_margin": profit_margin,  # 마진율
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            
            # ============================================
            # 🆕 STORE MODE: 개인정보 보호 및 점원 알림
            # ============================================
            
            mode_config = self._get_mode_config()
            
            # 1. 점원 알림 전송 (Store Mode)
            if mode_config.get("clerk_notification_enabled", False):
                # 배송 희망일이 긴급한 경우
                is_urgent = False  # 실제로는 order_data에서 판단
                
                notification_type = "urgent" if is_urgent else "new_order"
                await self._send_clerk_notification(order_data, notification_type)
            
            # 2. 음성 출력 제한 (Store Mode)
            if not mode_config.get("voice_output_enabled", True):
                logger.info("🔇 Voice output disabled (Store Mode)")
                # 음성 출력 대신 화면 표시만
            
            # 3. 로그 최소화 (Store Mode)
            if not mode_config.get("log_customer_data", True):
                # 개인정보 로그 최소화
                logger.info(f"✅ Order processed: {order_id} (₩{final_amount:,.0f}) [Privacy Protected]")
            else:
                logger.info(f"✅ Order processed: {order_id} ({customer_phone}, ₩{final_amount:,.0f}, margin: {profit_margin:.1f}%)")
            
            # ============================================
            
            # 주문 접수 메시지 발송
            await self.send_message(
                MessageType.ORDER_RECEIVED,
                payload=order_data,
                priority=3  # 높은 우선순위
            )
            
            # 통계 업데이트
            self.order_stats["total_orders_today"] += 1
            self.order_stats["total_revenue_today"] += total_revenue
            self.order_stats["pending_orders"] += 1
            
            self.stats["tasks_completed"] += 1
            
            # 🆕 Store Mode: 마스킹된 정보 반환
            display_phone = self._mask_customer_phone(customer_phone)
            display_name = self._mask_customer_name(order_data.get("customer_name", "고객님"))
            
            return {
                "success": True,
                "order_id": order_id,
                "customer_phone": display_phone,  # 마스킹됨
                "customer_name": display_name,  # 마스킹됨
                "total_amount": final_amount,
                "profit": total_profit,
                "profit_margin": f"{profit_margin:.1f}%",
                "items": optimized_items,
                "delivery_cost": delivery_cost,
                "message": f"주문이 접수되었습니다 (총 ₩{final_amount:,.0f})",
                "clerk_notified": mode_config.get("clerk_notification_enabled", False)  # 🆕
            }
            
        except Exception as e:
            logger.error(f"❌ Order processing error: {str(e)}")
            self.stats["errors"] += 1
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_and_reply_reviews(self):
        """
        구글 리뷰 확인 및 자동 답변
        
        모든 농장의 미답변 리뷰를 확인하고
        농장주 말투로 자동 답변
        """
        try:
            logger.info("🔍 Checking new Google reviews...")
            
            # DB에서 모든 농장 조회 (향후 구현)
            farm_ids = [1, 2]  # 샘플
            
            for farm_id in farm_ids:
                # 농장의 Location ID 가져오기 (향후 DB에서)
                location_id = f"location_{farm_id}"
                
                # 리뷰 조회
                reviews = await self.google.fetch_reviews(location_id, page_size=10)
                
                # 미답변 리뷰 필터
                unanswered = [r for r in reviews if not r.get("reply")]
                
                logger.info(f"📊 Farm {farm_id}: {len(unanswered)} unanswered reviews")
                
                for review in unanswered:
                    # 농장주 말투로 답변 생성
                    reply = await self._generate_farmer_reply(
                        farm_id=farm_id,
                        review_text=review.get("comment", ""),
                        star_rating=review.get("star_rating", 5),
                        reviewer_name=review.get("reviewer_name", "고객님")
                    )
                    
                    # 리뷰 답변 게시
                    success = await self.google.post_ai_reply(
                        location_id=location_id,
                        review_id=review.get("review_id"),
                        reply_text=reply
                    )
                    
                    if success:
                        logger.info(f"✅ Auto-replied to review: {review.get('review_id')}")
                        self.stats["tasks_completed"] += 1
                    
                    # API 레이트 리밋 고려
                    await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ Review check error: {str(e)}")
            self.stats["errors"] += 1
    
    async def _generate_farmer_reply(
        self,
        farm_id: int,
        review_text: str,
        star_rating: int,
        reviewer_name: str
    ) -> str:
        """
        농장주 말투로 리뷰 답변 생성
        
        Args:
            farm_id: 농장 ID
            review_text: 리뷰 내용
            star_rating: 별점
            reviewer_name: 리뷰 작성자
            
        Returns:
            str: 농장주 말투 답변
        """
        try:
            # 농장주 프로필
            profile = self.farmer_profiles.get(farm_id, {
                "name": "농장주",
                "tone": "따뜻하고 친절하게",
                "greeting": "안녕하세요~",
                "signature": "감사합니다!"
            })
            
            farmer_name = profile["name"]
            tone = profile["tone"]
            greeting = profile["greeting"]
            signature = profile["signature"]
            
            # Qwen AI 프롬프트
            prompt = f"""
당신은 {farmer_name} 농장주입니다.

고객 {reviewer_name}님이 다음과 같은 리뷰를 남겼습니다:
별점: {star_rating}/5
내용: "{review_text}"

이 리뷰에 대해 {tone} 답변을 작성해주세요.

조건:
1. 첫 인사: {greeting}
2. 말투: {tone}
3. 100자 이내
4. 마무리: {signature}
5. 리뷰 내용에 구체적으로 반응
6. 이모지 1-2개 사용

답변만 출력하세요:
"""
            
            # Qwen API 호출
            response = await self.qwen._call_qwen_api(
                messages=[
                    {"role": "system", "content": f"You are {farmer_name}, a warm and friendly farmer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            reply = response["choices"][0]["message"]["content"].strip()
            
            logger.info(f"✅ Farmer reply generated ({len(reply)} chars)")
            
            return reply
            
        except Exception as e:
            logger.error(f"❌ Reply generation error: {str(e)}")
            
            # Fallback 답변
            if star_rating >= 4:
                return f"{reviewer_name}님, {greeting} 소중한 후기 정말 감사드립니다! {signature}"
            else:
                return f"{reviewer_name}님, {greeting} 불편을 드려 죄송합니다. 더 나은 서비스로 보답하겠습니다. {signature}"
    
    async def handle_promotion_request(self, message: AgentMessage):
        """
        프로모션 요청 처리
        
        Inventory Manager로부터 품절 임박 알림 받으면
        즉시 할인 프로모션 실행
        """
        try:
            self.stats["messages_received"] += 1
            
            payload = message.payload
            product = payload.get("product")
            farm_id = payload.get("farm_id")
            quantity_left = payload.get("quantity_left")
            
            logger.info(f"🎁 Executing promotion for {product} (farm {farm_id})")
            
            # 할인율 결정
            if quantity_left < 10:
                discount_rate = 30  # 30% 할인
            elif quantity_left < 30:
                discount_rate = 20  # 20% 할인
            else:
                discount_rate = 10  # 10% 할인
            
            # SNS Manager에게 홍보 요청
            await self.send_message(
                MessageType.PROMOTION_REQUEST,
                to_agent="SNS_Manager",
                payload={
                    "farm_id": farm_id,
                    "product": product,
                    "discount_rate": discount_rate,
                    "reason": f"재고 {quantity_left}개 남음!"
                },
                priority=2
            )
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Promotion handling error: {str(e)}")
    
    async def handle_low_inventory(self, message: AgentMessage):
        """
        재고 부족 처리
        
        해당 상품 주문 시 대체 상품 추천
        """
        try:
            self.stats["messages_received"] += 1
            
            payload = message.payload
            product = payload.get("product")
            
            logger.info(f"⚠️ Low inventory alert: {product}")
            
            # 대체 상품 추천 로직 (향후 구현)
            # 예: 사과 품절 → 배 추천
            
        except Exception as e:
            logger.error(f"❌ Low inventory handling error: {str(e)}")
    
    async def update_daily_stats(self):
        """일일 통계 업데이트"""
        try:
            logger.info(f"📊 Daily stats: {self.order_stats['total_orders_today']} orders, {self.order_stats['total_revenue_today']}원")
            
            # Strategy Advisor에게 통계 전송
            await self.send_message(
                MessageType.METRICS_UPDATE,
                to_agent="Strategy_Advisor",
                payload={
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "total_orders": self.order_stats["total_orders_today"],
                    "total_revenue": self.order_stats["total_revenue_today"],
                    "pending_orders": self.order_stats["pending_orders"]
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Stats update error: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Sales Agent 통계"""
        stats = super().get_stats()
        stats["order_stats"] = self.order_stats
        return stats


# ============================================
# 싱글톤 인스턴스
# ============================================

_sales_agent_instance: Optional[SalesAgent] = None


def get_sales_agent(message_bus: MessageBus) -> SalesAgent:
    """싱글톤 Sales Agent"""
    global _sales_agent_instance
    
    if _sales_agent_instance is None:
        _sales_agent_instance = SalesAgent(message_bus)
    
    return _sales_agent_instance

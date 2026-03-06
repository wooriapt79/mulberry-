"""
Mulberry Phase 3 - SNS Manager Agent
마스토돈 자동 포스팅 및 감성 스토리텔링
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.agents.base import BaseAgent, MessageBus, MessageType, AgentMessage
from app.services import get_mastodon_service, get_qwen_service


class SNSManagerAgent(BaseAgent):
    """
    SNS 관리 비서
    
    기능:
    - 농장별 작업 현황 자동 포스팅
    - 특산물 감성 스토리텔링
    - 시즌별 프로모션 홍보
    - 리뷰/피드백 자동 공유
    """
    
    def __init__(self, message_bus: MessageBus, config: Optional[Dict[str, Any]] = None):
        """SNS Manager 초기화"""
        super().__init__(
            agent_name="SNS_Manager",
            message_bus=message_bus,
            config=config or {}
        )
        
        # 마스토돈 서비스
        self.mastodon = get_mastodon_service()
        
        # Qwen 서비스 (감성 스토리텔링)
        self.qwen = get_qwen_service()
        
        # 포스팅 스케줄
        self.post_schedule = {
            "daily_update": "09:00",  # 매일 아침 업데이트
            "promotion": "12:00",  # 점심 프로모션
            "story": "18:00"  # 저녁 스토리
        }
        
        # 포스팅 히스토리
        self.post_history: List[Dict[str, Any]] = []
        
        # 스토리텔링 템플릿
        self.story_templates = self._load_story_templates()
        
        logger.info("✅ SNS Manager Agent initialized")
    
    def _load_story_templates(self) -> Dict[str, str]:
        """스토리텔링 템플릿 로드"""
        return {
            "harvest": """
오늘 아침, {farm_name}의 {farmer_name} 농부님이 
정성껏 키운 {product}를 수확했습니다. 🍎

{weather}에도 불구하고,
{duration}일간의 땀과 사랑이 담긴 결실입니다.

인제군의 깨끗한 공기와 맑은 물로 키운
이 {product}는 특별합니다.

#인제군 #로컬푸드 #{product} #농장이야기
""",
            "season": """
{season} 인제군의 특산물 {product} 시즌이 돌아왔습니다! 🌿

{description}

지금이 가장 맛있을 때!
농장에서 바로 식탁으로 🚚

#계절음식 #{product} #인제특산물
""",
            "customer_story": """
{customer_name}님의 이야기 💚

"{review}"

{farm_name}의 {product}가 
{customer_name}님 댁의 식탁을 더 풍성하게 만들었습니다.

이런 이야기가 우리의 보람입니다.

#고객후기 #감사합니다
"""
        }
    
    def _register_message_handlers(self):
        """메시지 핸들러 등록"""
        # 재고 업데이트 → 수확 소식 포스팅
        self.message_bus.subscribe(
            MessageType.INVENTORY_UPDATE,
            self.handle_inventory_update
        )
        
        # 프로모션 요청 → 할인 홍보
        self.message_bus.subscribe(
            MessageType.PROMOTION_REQUEST,
            self.handle_promotion_request
        )
        
        # 주문 완료 → 감사 포스팅
        self.message_bus.subscribe(
            MessageType.ORDER_COMPLETED,
            self.handle_order_completed
        )
    
    async def start(self):
        """SNS Manager 시작"""
        await super().start()
        
        # 정기 포스팅 스케줄러 시작
        asyncio.create_task(self._run_scheduler())
        
        logger.info("🚀 SNS Manager started with scheduled posting")
    
    async def stop(self):
        """SNS Manager 종료"""
        await super().stop()
    
    async def _run_scheduler(self):
        """정기 포스팅 스케줄러"""
        while self.is_active:
            try:
                current_time = datetime.now().strftime("%H:%M")
                
                # 매일 아침 업데이트
                if current_time == self.post_schedule["daily_update"]:
                    await self.post_daily_update()
                
                # 점심 프로모션
                elif current_time == self.post_schedule["promotion"]:
                    await self.post_random_promotion()
                
                # 저녁 스토리
                elif current_time == self.post_schedule["story"]:
                    await self.post_farm_story()
                
                # 1분마다 체크
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Scheduler error: {str(e)}")
                await asyncio.sleep(60)
    
    async def handle_inventory_update(self, message: AgentMessage):
        """
        재고 업데이트 처리 → 수확 소식 포스팅
        
        Payload:
        {
            "farm_id": 1,
            "farm_name": "푸른골농원",
            "product": "사과",
            "quantity": 100,
            "harvest_date": "2024-02-11"
        }
        """
        try:
            self.stats["messages_received"] += 1
            
            payload = message.payload
            farm_name = payload.get("farm_name")
            product = payload.get("product")
            quantity = payload.get("quantity")
            
            logger.info(f"📸 Creating harvest story for {farm_name} - {product}")
            
            # AI 스토리텔링
            story = await self._generate_harvest_story(payload)
            
            # 마스토돈 포스팅
            post_result = await self.mastodon.post_status(
                status=story,
                visibility="public"
            )
            
            if post_result:
                self.post_history.append({
                    "type": "harvest",
                    "farm_name": farm_name,
                    "product": product,
                    "posted_at": datetime.now().isoformat()
                })
                
                self.stats["tasks_completed"] += 1
                
                # 포스팅 완료 알림
                await self.send_message(
                    MessageType.POST_PUBLISHED,
                    payload={
                        "post_type": "harvest",
                        "farm_name": farm_name,
                        "product": product
                    }
                )
            
        except Exception as e:
            logger.error(f"❌ Failed to handle inventory update: {str(e)}")
            self.stats["errors"] += 1
    
    async def _generate_harvest_story(self, data: Dict[str, Any]) -> str:
        """
        AI로 수확 스토리 생성
        
        Args:
            data: 농장 및 수확 정보
            
        Returns:
            str: 감성적인 포스팅 텍스트
        """
        try:
            farm_name = data.get("farm_name", "농장")
            product = data.get("product", "농산물")
            quantity = data.get("quantity", 0)
            
            prompt = f"""
인제군의 {farm_name}에서 오늘 {product} {quantity}개를 수확했습니다.

이 소식을 감성적이고 따뜻한 마스토돈 포스팅으로 작성해주세요.

조건:
1. 농장주의 정성과 노력을 강조
2. 인제군의 청정 자연 언급
3. 200자 이내
4. 해시태그 3-5개 포함
5. 이모지 1-2개 사용

포스팅:
"""
            
            # Qwen AI 호출
            response = await self.qwen._call_qwen_api(
                messages=[
                    {"role": "system", "content": "You are a warm and emotional storyteller for a local farm community."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            story = response["choices"][0]["message"]["content"].strip()
            
            logger.info(f"✅ AI story generated: {len(story)} chars")
            
            return story
            
        except Exception as e:
            logger.error(f"❌ Story generation error: {str(e)}")
            
            # Fallback 템플릿
            return f"""
오늘 {data.get('farm_name')}에서 신선한 {data.get('product')}를 수확했습니다! 🍎

인제군의 깨끗한 자연에서 자란 특별한 맛을 만나보세요.

#인제군 #로컬푸드 #{data.get('product')}
"""
    
    async def handle_promotion_request(self, message: AgentMessage):
        """
        프로모션 요청 처리 → 할인 홍보
        
        Payload:
        {
            "farm_id": 1,
            "product": "사과",
            "discount_rate": 20,
            "reason": "품절 임박"
        }
        """
        try:
            self.stats["messages_received"] += 1
            
            payload = message.payload
            product = payload.get("product")
            discount = payload.get("discount_rate", 10)
            reason = payload.get("reason", "특별 할인")
            
            logger.info(f"📢 Creating promotion post: {product} {discount}% off")
            
            # 프로모션 포스팅
            promo_text = f"""
🎉 긴급 할인! {product} {discount}% OFF

{reason}로 인해 특별 가격으로 제공합니다!

지금이 기회! 신선한 {product}를 만나보세요 🚚

주문: #Mulberry_주문
#할인이벤트 #인제특산물 #{product}
"""
            
            await self.mastodon.post_status(
                status=promo_text,
                visibility="public"
            )
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to handle promotion: {str(e)}")
            self.stats["errors"] += 1
    
    async def handle_order_completed(self, message: AgentMessage):
        """
        주문 완료 처리 → 감사 포스팅 (주기적)
        
        일정 주문 수 달성 시 감사 메시지
        """
        try:
            self.stats["messages_received"] += 1
            
            # 100번째 주문마다 감사 포스팅
            total_orders = message.payload.get("total_orders_today", 0)
            
            if total_orders % 100 == 0:
                thank_you_text = f"""
💚 감사합니다!

오늘 {total_orders}번째 주문이 완료되었습니다!

인제군 농가와 고객님을 연결해주는
Mulberry 플랫폼을 이용해주셔서 감사합니다.

항상 신선한 먹거리로 보답하겠습니다 🌾

#감사합니다 #인제군 #로컬푸드
"""
                
                await self.mastodon.post_status(
                    status=thank_you_text,
                    visibility="public"
                )
                
                self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to post thank you: {str(e)}")
    
    async def post_daily_update(self):
        """매일 아침 업데이트 포스팅"""
        try:
            logger.info("🌅 Posting daily update...")
            
            today = datetime.now().strftime("%Y년 %m월 %d일")
            
            daily_text = f"""
좋은 아침입니다! ☀️

{today} 인제군 농장에서 인사드립니다.

오늘도 신선한 농산물로 여러분의 식탁을 풍성하게 만들겠습니다 🌾

#인제군 #로컬푸드 #굿모닝
"""
            
            await self.mastodon.post_status(
                status=daily_text,
                visibility="public"
            )
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Daily update failed: {str(e)}")
    
    async def post_random_promotion(self):
        """랜덤 프로모션 포스팅"""
        # DB에서 재고 많은 상품 가져와서 프로모션
        # 향후 구현
        pass
    
    async def generate_senior_story(
        self,
        user_input: str,
        farm_name: Optional[str] = None,
        farmer_name: Optional[str] = None,
        photo_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[str]]:
        """
        시니어 친화형 스토리텔링 엔진
        
        투박한 단문/키워드를 감성적인 SNS 포스팅으로 변환
        
        🎯 목표:
        - 시니어의 간단한 입력 → 풍부한 스토리텔링
        - 계절감, 농부의 정성, 인제군 청정 이미지 반영
        - 마스토돈 규격 포맷팅 + 자동 해시태그
        
        Args:
            user_input: 시니어의 투박한 텍스트 (ex: "배추 수확함, 날씨 좋음")
            farm_name: 농장 이름 (ex: "푸른골농원")
            farmer_name: 농부 이름 (ex: "김철수")
            photo_metadata: 사진 메타데이터 {
                "date": "2024-02-12",
                "location": "인제군 기린면",
                "weather": "맑음",
                "temperature": "5°C"
            }
            
        Returns:
            dict: {
                "stories": [3가지 버전의 스토리],
                "hashtags": ["자동 생성된 해시태그"],
                "metadata": {...}
            }
        """
        try:
            logger.info(f"✍️ Generating senior story from: '{user_input}'")
            
            # 기본값 설정
            farm_name = farm_name or "우리 농장"
            farmer_name = farmer_name or "농부"
            
            # 사진 메타데이터 파싱
            context = self._parse_photo_context(photo_metadata)
            
            # ============================================
            # 🎨 AI 스토리텔링 (3가지 버전)
            # ============================================
            
            # Qwen AI 프롬프트
            prompt = f"""
당신은 따뜻하고 감성적인 농촌 스토리텔러입니다.

【시니어 입력】
"{user_input}"

【농장 정보】
- 농장: {farm_name}
- 농부: {farmer_name}

【상황 정보】
{context}

【미션】
위 간단한 입력을 감성적인 SNS 포스팅 3가지 버전으로 변환하세요.

【스타일 가이드】
1. 버전 A (따뜻한 일상): 농부의 일상을 따뜻하게 전달
2. 버전 B (계절 감성): 계절감과 자연의 아름다움 강조
3. 버전 C (정성과 자부심): 농부의 정성과 인제군 청정 이미지

【제약 조건】
- 각 버전 150자 이내
- 자연스럽고 진솔한 말투
- 이모지 2-3개 사용
- 인제군의 청정 자연 언급
- 해시태그는 별도로 출력

【출력 형식 (JSON)】
{{
  "version_a": "...",
  "version_b": "...",
  "version_c": "...",
  "hashtags": ["인제군", "로컬푸드", "..."]
}}

JSON만 출력하세요:
"""
            
            # Qwen API 호출
            start_time = time.time()
            
            response = await self.qwen._call_qwen_api(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a warm and emotional storyteller for rural farmers."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # 창의성 높게
                max_tokens=600
            )
            
            inference_time = (time.time() - start_time) * 1000
            
            # JSON 파싱
            output_text = response["choices"][0]["message"]["content"].strip()
            
            # JSON 추출
            if "```json" in output_text:
                output_text = output_text.split("```json")[1].split("```")[0]
            elif "```" in output_text:
                output_text = output_text.split("```")[1].split("```")[0]
            
            result = json.loads(output_text)
            
            stories = [
                result.get("version_a", ""),
                result.get("version_b", ""),
                result.get("version_c", "")
            ]
            
            hashtags = result.get("hashtags", [])
            
            # 기본 해시태그 추가
            default_hashtags = ["인제군", "로컬푸드", farm_name.replace(" ", "")]
            for tag in default_hashtags:
                if tag not in hashtags:
                    hashtags.append(tag)
            
            # 마스토돈 규격 포맷팅
            formatted_stories = []
            for story in stories:
                formatted = self._format_for_mastodon(story, hashtags)
                formatted_stories.append(formatted)
            
            logger.info(f"✅ Senior story generated in {inference_time:.1f}ms")
            logger.info(f"📝 Version A: {stories[0][:50]}...")
            logger.info(f"📝 Hashtags: {', '.join(['#' + h for h in hashtags])}")
            
            return {
                "success": True,
                "stories": formatted_stories,
                "original_stories": stories,
                "hashtags": hashtags,
                "metadata": {
                    "user_input": user_input,
                    "farm_name": farm_name,
                    "farmer_name": farmer_name,
                    "context": context,
                    "inference_time_ms": inference_time
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Senior story generation error: {str(e)}")
            
            # Fallback: 간단한 템플릿
            return self._generate_fallback_story(user_input, farm_name, farmer_name, photo_metadata)
    
    def _parse_photo_context(self, photo_metadata: Optional[Dict[str, Any]]) -> str:
        """
        사진 메타데이터를 문맥으로 변환
        
        Args:
            photo_metadata: 사진 정보
            
        Returns:
            str: 문맥 텍스트
        """
        if not photo_metadata:
            return "날짜: 오늘\n위치: 인제군\n날씨: 정보 없음"
        
        date = photo_metadata.get("date", "오늘")
        location = photo_metadata.get("location", "인제군")
        weather = photo_metadata.get("weather", "정보 없음")
        temperature = photo_metadata.get("temperature", "")
        
        context = f"""날짜: {date}
위치: {location}
날씨: {weather} {temperature}"""
        
        return context
    
    def _format_for_mastodon(self, story: str, hashtags: List[str]) -> str:
        """
        마스토돈 규격 포맷팅
        
        Args:
            story: 스토리 텍스트
            hashtags: 해시태그 리스트
            
        Returns:
            str: 포맷팅된 포스트
        """
        # 해시태그 추가
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
        
        # 마스토돈 최대 길이 (500자)
        max_length = 500
        
        # 스토리 + 해시태그
        formatted = f"{story}\n\n{hashtag_str}"
        
        # 길이 제한
        if len(formatted) > max_length:
            # 스토리 줄이기
            story_limit = max_length - len(hashtag_str) - 10
            story = story[:story_limit] + "..."
            formatted = f"{story}\n\n{hashtag_str}"
        
        return formatted
    
    def _generate_fallback_story(
        self,
        user_input: str,
        farm_name: str,
        farmer_name: str,
        photo_metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fallback: AI 실패 시 템플릿 기반 스토리
        
        Args:
            user_input: 사용자 입력
            farm_name: 농장 이름
            farmer_name: 농부 이름
            photo_metadata: 사진 메타데이터
            
        Returns:
            dict: Fallback 스토리
        """
        logger.warning("⚠️ Using fallback story template")
        
        # 간단한 템플릿
        stories = [
            f"{farm_name}의 {farmer_name}입니다.\n{user_input}\n인제군의 청정 자연에서 정성껏 키웠습니다. 🌾",
            f"오늘 {farm_name}에서 {user_input}\n깨끗한 인제의 공기와 물로 키운 특별한 맛입니다. 🍎",
            f"{user_input}\n{farm_name}에서 정성껏 준비했습니다. 늘 건강한 먹거리로 보답하겠습니다. 💚"
        ]
        
        hashtags = ["인제군", "로컬푸드", farm_name.replace(" ", ""), "농장이야기"]
        
        formatted_stories = [
            self._format_for_mastodon(story, hashtags)
            for story in stories
        ]
        
        return {
            "success": True,
            "stories": formatted_stories,
            "original_stories": stories,
            "hashtags": hashtags,
            "metadata": {
                "user_input": user_input,
                "fallback": True
            }
        }
    
    async def post_senior_story(
        self,
        user_input: str,
        farm_name: Optional[str] = None,
        farmer_name: Optional[str] = None,
        photo_metadata: Optional[Dict[str, Any]] = None,
        selected_version: int = 0
    ) -> Dict[str, Any]:
        """
        시니어 스토리 생성 → 즉시 포스팅
        
        Args:
            user_input: 시니어 입력
            farm_name: 농장 이름
            farmer_name: 농부 이름
            photo_metadata: 사진 메타데이터
            selected_version: 선택할 버전 (0, 1, 2)
            
        Returns:
            dict: 포스팅 결과
        """
        try:
            # 스토리 생성
            story_result = await self.generate_senior_story(
                user_input=user_input,
                farm_name=farm_name,
                farmer_name=farmer_name,
                photo_metadata=photo_metadata
            )
            
            if not story_result.get("success"):
                return story_result
            
            # 선택된 버전 포스팅
            stories = story_result["stories"]
            selected_story = stories[selected_version] if selected_version < len(stories) else stories[0]
            
            # 마스토돈 포스팅
            post_result = await self.mastodon.post_status(
                status=selected_story,
                visibility="public"
            )
            
            if post_result:
                logger.info(f"✅ Senior story posted successfully")
                
                self.post_history.append({
                    "type": "senior_story",
                    "user_input": user_input,
                    "selected_version": selected_version,
                    "posted_at": datetime.now().isoformat()
                })
                
                self.stats["tasks_completed"] += 1
                
                # 🆕 POST_PUBLISHED 메시지 발송 (Phase 3-C)
                await self.send_message(
                    MessageType.POST_PUBLISHED,
                    payload={
                        "post_type": "senior_story",
                        "farm_name": farm_name,
                        "user_type": "senior",
                        "reach_estimate": 100,  # 샘플
                        "hashtags": story_result["hashtags"]
                    }
                )
                
                return {
                    "success": True,
                    "posted_story": selected_story,
                    "all_versions": story_result["original_stories"],
                    "hashtags": story_result["hashtags"],
                    "message": "스토리가 성공적으로 게시되었습니다!"
                }
            else:
                return {
                    "success": False,
                    "error": "포스팅 실패"
                }
            
        except Exception as e:
            logger.error(f"❌ Senior story posting error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# ============================================
# 싱글톤 인스턴스
# ============================================

_sns_manager_instance: Optional[SNSManagerAgent] = None


def get_sns_manager(message_bus: MessageBus) -> SNSManagerAgent:
    """싱글톤 SNS Manager"""
    global _sns_manager_instance
    
    if _sns_manager_instance is None:
        _sns_manager_instance = SNSManagerAgent(message_bus)
    
    return _sns_manager_instance

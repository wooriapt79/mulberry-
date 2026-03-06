"""
Mulberry Phase 1+ - Google Business Profile Service
구글 마이 비즈니스(GMB) API 연동 및 리뷰/예약 관리
"""

import json
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.config import settings
from app.services.qwen_service import QwenService


class GoogleBusinessService:
    """
    구글 마이 비즈니스 API 연동 서비스
    - 리뷰 수집 및 AI 자동 답변
    - 음성 예약 처리 (Edge AI 연동)
    - 비즈니스 메트릭 수집
    """
    
    def __init__(self):
        """Google Business Profile API 클라이언트 초기화"""
        self.api_key = settings.google_api_key
        self.oauth_client_id = settings.google_oauth_client_id
        self.oauth_client_secret = settings.google_oauth_client_secret
        self.account_id = settings.google_business_account_id
        
        # Google Business Profile API v4 엔드포인트
        self.base_url = "https://mybusiness.googleapis.com/v4"
        
        # HTTP 클라이언트
        self.client = httpx.AsyncClient(
            timeout=30,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        # Qwen 서비스 (AI 답변 생성용)
        self.qwen_service = QwenService()
        
        logger.info("✅ Google Business Profile service initialized")
    
    async def close(self):
        """HTTP 클라이언트 종료"""
        await self.client.aclose()
        await self.qwen_service.close()
    
    # ============================================
    # 1. 리뷰 관리
    # ============================================
    
    async def fetch_reviews(
        self,
        location_id: str,
        page_size: int = 50,
        min_rating: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        특정 농장(location)의 구글 리뷰 수집
        
        Args:
            location_id: 구글 비즈니스 Location ID (accounts/{account_id}/locations/{location_id})
            page_size: 한 번에 가져올 리뷰 수
            min_rating: 최소 별점 필터 (1-5)
            
        Returns:
            list: 리뷰 목록
        """
        try:
            logger.info(f"🔍 Fetching GMB reviews for location: {location_id}")
            
            # API 엔드포인트
            url = f"{self.base_url}/accounts/{self.account_id}/locations/{location_id}/reviews"
            
            params = {
                "pageSize": page_size,
                "orderBy": "updateTime desc"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            reviews = data.get("reviews", [])
            
            # 별점 필터링
            if min_rating:
                reviews = [r for r in reviews if r.get("starRating", 0) >= min_rating]
            
            logger.info(f"✅ Fetched {len(reviews)} reviews from GMB")
            
            # 리뷰 데이터 정규화
            normalized_reviews = []
            for review in reviews:
                normalized_reviews.append({
                    "review_id": review.get("reviewId"),
                    "reviewer_name": review.get("reviewer", {}).get("displayName"),
                    "star_rating": review.get("starRating"),
                    "comment": review.get("comment"),
                    "reply": review.get("reviewReply", {}).get("comment"),
                    "create_time": review.get("createTime"),
                    "update_time": review.get("updateTime"),
                    "reply_update_time": review.get("reviewReply", {}).get("updateTime"),
                })
            
            return normalized_reviews
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ GMB API error: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"❌ Failed to fetch reviews: {str(e)}")
            return []
    
    async def generate_ai_reply(
        self,
        review_text: str,
        star_rating: int,
        farm_name: str,
        reviewer_name: Optional[str] = None
    ) -> str:
        """
        Qwen AI로 리뷰 답변 생성
        
        Args:
            review_text: 리뷰 내용
            star_rating: 별점 (1-5)
            farm_name: 농장 이름
            reviewer_name: 리뷰 작성자 이름
            
        Returns:
            str: 생성된 답변 텍스트
        """
        try:
            # 리뷰 감정 분석 및 답변 스타일 결정
            tone = "감사하고 친절한" if star_rating >= 4 else "사과하고 개선하려는"
            
            prompt = f"""
당신은 {farm_name} 농장의 고객 서비스 담당자입니다.
다음 구글 리뷰에 대해 진심 어린 답변을 작성해주세요.

【리뷰 정보】
- 작성자: {reviewer_name or '고객님'}
- 별점: {star_rating}/5
- 리뷰 내용: {review_text}

【답변 작성 가이드】
1. 리뷰어의 이름을 호칭하며 시작 (예: "{reviewer_name}님, 소중한 리뷰 감사합니다!")
2. 톤: {tone}
3. 구체적인 내용에 대해 언급
4. 100자 내외로 간결하게
5. 농장의 진정성과 따뜻함이 느껴지도록
6. 긍정적 리뷰면 재방문 요청, 부정적 리뷰면 개선 약속

답변만 출력하고 다른 설명은 추가하지 마세요.
"""
            
            # Qwen API 호출
            response = await self.qwen_service._call_qwen_api(
                messages=[
                    {"role": "system", "content": "You are a friendly farm customer service representative."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # 창의적인 답변을 위해 온도 높임
                max_tokens=200
            )
            
            reply_text = response["choices"][0]["message"]["content"].strip()
            
            logger.info(f"✅ AI reply generated for {star_rating}★ review")
            return reply_text
            
        except Exception as e:
            logger.error(f"❌ Failed to generate AI reply: {str(e)}")
            # Fallback 답변
            if star_rating >= 4:
                return f"{reviewer_name}님, 소중한 후기 감사합니다! 항상 신선하고 건강한 농산물로 보답하겠습니다. 😊"
            else:
                return f"{reviewer_name}님, 불편을 드려 죄송합니다. 더 나은 서비스로 찾아뵙겠습니다."
    
    async def post_ai_reply(
        self,
        location_id: str,
        review_id: str,
        reply_text: str
    ) -> bool:
        """
        Qwen이 생성한 답글을 구글 리뷰에 게시
        
        Args:
            location_id: Location ID
            review_id: Review ID
            reply_text: 답변 텍스트
            
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info(f"📤 Posting AI reply to review {review_id}")
            
            url = f"{self.base_url}/accounts/{self.account_id}/locations/{location_id}/reviews/{review_id}/reply"
            
            payload = {
                "comment": reply_text
            }
            
            response = await self.client.put(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"✅ AI reply posted successfully")
            return True
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Failed to post reply: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to post reply: {str(e)}")
            return False
    
    async def auto_reply_to_review(
        self,
        location_id: str,
        review_data: Dict[str, Any],
        farm_name: str
    ) -> bool:
        """
        리뷰에 AI 자동 답변 (전체 프로세스)
        
        Args:
            location_id: Location ID
            review_data: 리뷰 데이터
            farm_name: 농장 이름
            
        Returns:
            bool: 성공 여부
        """
        review_id = review_data.get("review_id")
        review_text = review_data.get("comment")
        star_rating = review_data.get("star_rating")
        reviewer_name = review_data.get("reviewer_name")
        
        # 이미 답변이 있으면 스킵
        if review_data.get("reply"):
            logger.info(f"⏭️ Review {review_id} already has a reply")
            return False
        
        # AI 답변 생성
        reply_text = await self.generate_ai_reply(
            review_text=review_text,
            star_rating=star_rating,
            farm_name=farm_name,
            reviewer_name=reviewer_name
        )
        
        # 답변 게시
        success = await self.post_ai_reply(
            location_id=location_id,
            review_id=review_id,
            reply_text=reply_text
        )
        
        return success
    
    # ============================================
    # 2. 음성 예약 처리 (Edge AI 연동)
    # ============================================
    
    async def handle_voice_reservation(
        self,
        call_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        GMB '전화 예약'을 통해 들어온 음성 데이터 처리
        Edge AI(라즈베리파이)에서 전처리된 데이터를 받아 예약 생성
        
        🆕 Emergency Level 감지 기능 추가
        
        Args:
            call_data: {
                "customer_phone": "010-1234-5678",
                "customer_name": "김철수",
                "farm_id": 1,
                "requested_items": [
                    {"product_name": "사과", "quantity": 10, "unit": "kg"}
                ],
                "delivery_address": "서울시 강남구...",
                "preferred_date": "2024-02-15",
                "notes": "문 앞에 놔주세요",
                "audio_transcription": "사과 10킬로 주문하고 싶어요...",
                "dialect": "경상도",
                "voice_features": {  # 🆕 음성 특징
                    "pitch_hz": 350,  # 주파수
                    "volume_db": 65,  # 음량
                    "speech_rate": 2.5,  # 말 속도 (음절/초)
                    "pause_duration_ms": 800  # 휴지 시간
                }
            }
            
        Returns:
            dict: 예약 결과
        """
        try:
            logger.info(f"📞 Voice Reservation Received from {call_data.get('customer_phone')}")
            
            customer_phone = call_data.get("customer_phone")
            customer_name = call_data.get("customer_name", "고객님")
            farm_id = call_data.get("farm_id")
            requested_items = call_data.get("requested_items", [])
            delivery_address = call_data.get("delivery_address")
            preferred_date = call_data.get("preferred_date")
            notes = call_data.get("notes", "")
            dialect = call_data.get("dialect")
            
            # 음성 인식 원본 (Edge AI에서 전처리됨)
            transcription = call_data.get("audio_transcription", "")
            voice_features = call_data.get("voice_features", {})
            
            # ============================================
            # 🆕 Emergency Level 감지 (감성 분석)
            # ============================================
            emergency_level = await self._detect_emergency_level(
                transcription=transcription,
                voice_features=voice_features,
                dialect=dialect
            )
            
            # Emergency Level에 따른 우선순위 배정
            priority = self._assign_priority(emergency_level)
            
            # 긴급 상황 시 Sentinel(Malu)에게 즉시 알림
            if emergency_level >= 3:  # Level 3 이상: 긴급
                await self._alert_sentinel(
                    customer_phone=customer_phone,
                    customer_name=customer_name,
                    emergency_level=emergency_level,
                    transcription=transcription,
                    voice_features=voice_features
                )
            
            # 예약 데이터 검증
            if not customer_phone or not farm_id or not requested_items:
                return {
                    "success": False,
                    "error": "필수 정보 누락 (전화번호, 농장ID, 주문 항목)"
                }
            
            # 예약 번호 생성 (타임스탬프 기반)
            reservation_number = f"RES{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # 예약 데이터 구조화
            reservation_data = {
                "reservation_number": reservation_number,
                "customer_phone": customer_phone,
                "customer_name": customer_name,
                "farm_id": farm_id,
                "items": requested_items,
                "delivery_address": delivery_address,
                "preferred_date": preferred_date,
                "notes": notes,
                "status": "pending",
                "created_via": "voice_call",
                "dialect_detected": dialect,
                "original_transcription": transcription,
                "created_at": datetime.now().isoformat(),
                # 🆕 감성 분석 결과
                "emergency_level": emergency_level,
                "priority": priority,
                "voice_analysis": {
                    "pitch_hz": voice_features.get("pitch_hz"),
                    "volume_db": voice_features.get("volume_db"),
                    "speech_rate": voice_features.get("speech_rate"),
                    "emotion_detected": self._detect_emotion(voice_features)
                }
            }
            
            logger.info(f"✅ Voice reservation processed: {reservation_number} (Priority: {priority}, Emergency: {emergency_level})")
            
            # 농장주에게 SMS/카카오톡 알림 발송 (향후 구현)
            await self._notify_farm_owner(farm_id, reservation_data)
            
            # 고객에게 확인 메시지 발송
            await self._send_customer_confirmation(customer_phone, reservation_data, dialect)
            
            return {
                "success": True,
                "reservation_number": reservation_number,
                "reservation_data": reservation_data,
                "message": f"{customer_name}님의 예약이 접수되었습니다. 예약번호: {reservation_number}",
                "emergency_level": emergency_level,
                "priority": priority
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to handle voice reservation: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _notify_farm_owner(
        self,
        farm_id: int,
        reservation_data: Dict[str, Any]
    ):
        """농장주에게 새 예약 알림"""
        logger.info(f"📲 Notifying farm owner (farm_id={farm_id}) about new reservation")
        # SMS/카카오톡 API 연동 (향후 구현)
        pass
    
    async def _send_customer_confirmation(
        self,
        customer_phone: str,
        reservation_data: Dict[str, Any],
        dialect: Optional[str] = None
    ):
        """고객에게 예약 확인 메시지 발송 (사투리 지원)"""
        logger.info(f"📲 Sending confirmation to {customer_phone}")
        
        # 사투리별 메시지 템플릿
        messages = {
            "경상도": f"{reservation_data['customer_name']}님, 주문이 잘 들어갔심더. 예약번호: {reservation_data['reservation_number']}",
            "전라도": f"{reservation_data['customer_name']}님, 주문이 잘 들어갔어라우. 예약번호: {reservation_data['reservation_number']}",
            "충청도": f"{reservation_data['customer_name']}님, 주문이 잘 들어갔유. 예약번호: {reservation_data['reservation_number']}",
            "default": f"{reservation_data['customer_name']}님, 주문이 접수되었습니다. 예약번호: {reservation_data['reservation_number']}"
        }
        
        message = messages.get(dialect, messages["default"])
        
        # SMS API 연동 (향후 구현)
        logger.debug(f"SMS: {message}")
        pass
    
    # ============================================
    # 🆕 Emergency Level 감지 시스템
    # ============================================
    
    async def _detect_emergency_level(
        self,
        transcription: str,
        voice_features: Dict[str, Any],
        dialect: Optional[str] = None
    ) -> int:
        """
        음성 데이터로부터 Emergency Level 감지
        
        Level 0: 일반 주문 (Normal)
        Level 1: 약간 급함 (Mild Urgency)
        Level 2: 서두름 (Moderate Urgency)
        Level 3: 긴급 (Urgent)
        Level 4: 매우 긴급 (Critical)
        
        Args:
            transcription: 음성 인식 텍스트
            voice_features: 음성 특징 (주파수, 음량, 속도)
            dialect: 사투리
            
        Returns:
            int: Emergency Level (0-4)
        """
        try:
            # 1. 텍스트 기반 긴급도 분석
            text_urgency = self._analyze_text_urgency(transcription, dialect)
            
            # 2. 음성 특징 기반 감정 분석
            voice_urgency = self._analyze_voice_urgency(voice_features)
            
            # 3. 종합 판단 (가중 평균)
            emergency_level = int(round((text_urgency * 0.6 + voice_urgency * 0.4)))
            
            # 4. AI 감성 분석 (Qwen)으로 재검증 (옵션)
            if emergency_level >= 3:
                ai_verified_level = await self._ai_verify_emergency(
                    transcription,
                    voice_features,
                    preliminary_level=emergency_level
                )
                emergency_level = max(emergency_level, ai_verified_level)
            
            logger.info(f"🚨 Emergency Level Detected: {emergency_level} (Text: {text_urgency}, Voice: {voice_urgency})")
            
            return min(emergency_level, 4)  # 최대 4
            
        except Exception as e:
            logger.error(f"❌ Emergency detection error: {str(e)}")
            return 0  # 오류 시 안전하게 일반 주문으로 처리
    
    def _analyze_text_urgency(self, text: str, dialect: Optional[str] = None) -> int:
        """
        텍스트 내용으로 긴급도 판단
        
        긴급 키워드:
        - Level 4: "죽", "살려", "위급", "아파", "응급"
        - Level 3: "급해", "빨리", "서둘러", "당장"
        - Level 2: "시간이", "늦었어", "곧", "바로"
        - Level 1: "오늘", "빨리", "가능하면"
        """
        text_lower = text.lower()
        
        # Level 4: 위급 상황
        critical_keywords = ["죽", "살려", "위급", "아파", "응급", "도와", "위험", "쓰러"]
        if any(keyword in text_lower for keyword in critical_keywords):
            return 4
        
        # Level 3: 긴급
        urgent_keywords = ["급해", "빨리빨리", "당장", "지금 당장", "서둘러"]
        if any(keyword in text_lower for keyword in urgent_keywords):
            return 3
        
        # Level 2: 서두름
        moderate_keywords = ["시간이", "늦었", "곧", "바로", "빠르게"]
        if any(keyword in text_lower for keyword in moderate_keywords):
            return 2
        
        # Level 1: 약간 급함
        mild_keywords = ["오늘", "빨리", "가능하면", "서두르"]
        if any(keyword in text_lower for keyword in moderate_keywords):
            return 1
        
        # Level 0: 일반
        return 0
    
    def _analyze_voice_urgency(self, voice_features: Dict[str, Any]) -> int:
        """
        음성 특징으로 긴급도 판단
        
        Parameters:
        - pitch_hz: 목소리 주파수 (높을수록 긴급)
        - volume_db: 음량 (클수록 긴급)
        - speech_rate: 말 속도 (빠를수록 긴급)
        - pause_duration_ms: 휴지 시간 (짧을수록 긴급)
        """
        pitch = voice_features.get("pitch_hz", 200)  # 평균 200Hz
        volume = voice_features.get("volume_db", 60)  # 평균 60dB
        speech_rate = voice_features.get("speech_rate", 2.0)  # 평균 2음절/초
        pause = voice_features.get("pause_duration_ms", 500)  # 평균 500ms
        
        urgency_score = 0
        
        # 1. 주파수 분석 (높은 목소리 = 긴급)
        if pitch > 400:
            urgency_score += 2
        elif pitch > 300:
            urgency_score += 1
        
        # 2. 음량 분석 (큰 소리 = 긴급)
        if volume > 80:
            urgency_score += 2
        elif volume > 70:
            urgency_score += 1
        
        # 3. 말 속도 분석 (빠른 말 = 긴급)
        if speech_rate > 4.0:
            urgency_score += 2
        elif speech_rate > 3.0:
            urgency_score += 1
        
        # 4. 휴지 시간 분석 (짧은 쉼 = 긴급)
        if pause < 200:
            urgency_score += 2
        elif pause < 300:
            urgency_score += 1
        
        # 점수를 0-4 레벨로 변환
        if urgency_score >= 6:
            return 4
        elif urgency_score >= 4:
            return 3
        elif urgency_score >= 2:
            return 2
        elif urgency_score >= 1:
            return 1
        else:
            return 0
    
    def _detect_emotion(self, voice_features: Dict[str, Any]) -> str:
        """
        음성 특징으로 감정 감지
        
        Returns:
            str: calm, worried, urgent, distressed
        """
        pitch = voice_features.get("pitch_hz", 200)
        volume = voice_features.get("volume_db", 60)
        speech_rate = voice_features.get("speech_rate", 2.0)
        
        # 감정 분류
        if pitch > 350 and volume > 75:
            return "distressed"  # 고통/스트레스
        elif pitch > 300 or speech_rate > 3.5:
            return "urgent"  # 긴급
        elif pitch > 250 or speech_rate > 2.5:
            return "worried"  # 걱정
        else:
            return "calm"  # 평온
    
    async def _ai_verify_emergency(
        self,
        transcription: str,
        voice_features: Dict[str, Any],
        preliminary_level: int
    ) -> int:
        """
        Qwen AI로 긴급도 재검증
        
        Args:
            transcription: 음성 텍스트
            voice_features: 음성 특징
            preliminary_level: 1차 판단 레벨
            
        Returns:
            int: AI 검증 레벨
        """
        try:
            prompt = f"""
다음은 어르신의 전화 주문 내용입니다. 긴급도를 0-4로 판단하세요.

【음성 텍스트】
{transcription}

【음성 특징】
- 목소리 주파수: {voice_features.get('pitch_hz')}Hz
- 음량: {voice_features.get('volume_db')}dB
- 말 속도: {voice_features.get('speech_rate')}음절/초

【1차 판단】
Emergency Level: {preliminary_level}

【긴급도 기준】
0: 일반 주문
1: 약간 급함
2: 서두름
3: 긴급 (즉시 대응 필요)
4: 매우 긴급 (위급 상황 가능)

**숫자만 출력하세요 (0-4):**
"""
            
            response = await self.qwen_service._call_qwen_api(
                messages=[
                    {"role": "system", "content": "You are an emergency detection AI for elderly care."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            ai_level_str = response["choices"][0]["message"]["content"].strip()
            ai_level = int(ai_level_str)
            
            logger.info(f"🤖 AI Emergency Verification: {ai_level}")
            
            return min(max(ai_level, 0), 4)  # 0-4 범위 보장
            
        except Exception as e:
            logger.error(f"❌ AI verification error: {str(e)}")
            return preliminary_level  # 오류 시 1차 판단 유지
    
    def _assign_priority(self, emergency_level: int) -> str:
        """
        Emergency Level을 우선순위로 변환
        
        Args:
            emergency_level: 0-4
            
        Returns:
            str: LOW, NORMAL, HIGH, URGENT, CRITICAL
        """
        priority_map = {
            0: "LOW",
            1: "NORMAL",
            2: "HIGH",
            3: "URGENT",
            4: "CRITICAL"
        }
        return priority_map.get(emergency_level, "NORMAL")
    
    async def _alert_sentinel(
        self,
        customer_phone: str,
        customer_name: str,
        emergency_level: int,
        transcription: str,
        voice_features: Dict[str, Any]
    ):
        """
        Sentinel (Malu 수석 실장)에게 긴급 알림
        
        Args:
            customer_phone: 고객 전화번호
            customer_name: 고객 이름
            emergency_level: 긴급도 (3-4)
            transcription: 음성 텍스트
            voice_features: 음성 특징
        """
        try:
            alert_message = f"""
🚨 **EMERGENCY ALERT** 🚨

**고객 정보**
- 이름: {customer_name}
- 전화: {customer_phone}

**긴급도**: Level {emergency_level} ({self._assign_priority(emergency_level)})

**음성 내용**
"{transcription}"

**음성 분석**
- 주파수: {voice_features.get('pitch_hz')}Hz
- 음량: {voice_features.get('volume_db')}dB
- 말 속도: {voice_features.get('speech_rate')}음절/초
- 감정: {self._detect_emotion(voice_features)}

**대응 요청**: 즉시 확인 필요
"""
            
            # Sentinel API 엔드포인트로 전송
            sentinel_endpoint = "https://sentinel.mulberry.kr/api/emergency/alert"
            
            try:
                response = await self.client.post(
                    sentinel_endpoint,
                    json={
                        "emergency_level": emergency_level,
                        "customer_phone": customer_phone,
                        "customer_name": customer_name,
                        "transcription": transcription,
                        "voice_features": voice_features,
                        "timestamp": datetime.now().isoformat(),
                        "alert_message": alert_message
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Sentinel alerted successfully")
                else:
                    logger.warning(f"⚠️ Sentinel alert failed: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to send Sentinel alert: {str(e)}")
            
            # 추가: SMS/카카오톡/Slack 등 다중 채널 알림
            logger.critical(f"🚨 EMERGENCY ALERT: {customer_name} ({customer_phone}) - Level {emergency_level}")
            
        except Exception as e:
            logger.error(f"❌ Alert Sentinel error: {str(e)}")
    
    # ============================================
    # 3. 비즈니스 메트릭 수집
    # ============================================
    
    async def fetch_business_metrics(
        self,
        location_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        구글 비즈니스 프로필 메트릭 수집
        - 조회수, 검색 노출, 액션(전화, 길찾기) 등
        
        Args:
            location_id: Location ID
            start_date: 시작 날짜 (기본: 30일 전)
            end_date: 종료 날짜 (기본: 오늘)
            
        Returns:
            dict: 메트릭 데이터
        """
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            logger.info(f"📊 Fetching business metrics for {location_id}")
            
            url = f"{self.base_url}/accounts/{self.account_id}/locations/{location_id}/reportInsights"
            
            payload = {
                "locationNames": [f"accounts/{self.account_id}/locations/{location_id}"],
                "basicRequest": {
                    "metricRequests": [
                        {"metric": "ALL"},
                    ],
                    "timeRange": {
                        "startTime": start_date.isoformat(),
                        "endTime": end_date.isoformat()
                    }
                }
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"✅ Metrics fetched successfully")
            
            return {
                "location_id": location_id,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "metrics": data
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch metrics: {str(e)}")
            return {}


# ============================================
# 싱글톤 인스턴스
# ============================================

_google_service_instance: Optional[GoogleBusinessService] = None


def get_google_service() -> GoogleBusinessService:
    """
    싱글톤 Google Business 서비스 인스턴스 반환
    
    Returns:
        GoogleBusinessService: 서비스 인스턴스
    """
    global _google_service_instance
    
    if _google_service_instance is None:
        _google_service_instance = GoogleBusinessService()
    
    return _google_service_instance


# ============================================
# 테스트용 메인 함수
# ============================================

async def test_google_service():
    """Google Business Service 테스트"""
    service = get_google_service()
    
    # 테스트 데이터
    test_location_id = "12345678901234567890"
    
    # 1. 리뷰 조회
    reviews = await service.fetch_reviews(test_location_id, page_size=5)
    logger.info(f"Fetched {len(reviews)} reviews")
    
    # 2. AI 답변 생성 (샘플 리뷰)
    if reviews:
        sample_review = reviews[0]
        reply = await service.generate_ai_reply(
            review_text=sample_review.get("comment", "맛있어요!"),
            star_rating=sample_review.get("star_rating", 5),
            farm_name="푸른골농원",
            reviewer_name=sample_review.get("reviewer_name", "고객님")
        )
        logger.info(f"AI Reply: {reply}")
    
    # 3. 음성 예약 처리
    voice_call_data = {
        "customer_phone": "010-1234-5678",
        "customer_name": "김철수",
        "farm_id": 1,
        "requested_items": [
            {"product_name": "사과", "quantity": 10, "unit": "kg"}
        ],
        "delivery_address": "서울시 강남구",
        "preferred_date": "2024-02-15",
        "audio_transcription": "사과 10킬로 주문하고 싶어요",
        "dialect": "경상도"
    }
    
    reservation_result = await service.handle_voice_reservation(voice_call_data)
    logger.info(f"Reservation Result: {reservation_result}")
    
    await service.close()


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    asyncio.run(test_google_service())

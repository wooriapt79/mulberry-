"""
Mulberry Business Operations
CTO Koda

에이전트 업무 범위:
- ARS 고객 주문 응대
- 구글 마이 비즈니스 관리
- 온라인 고객 댓글 분석 및 응답
"""

from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
import json


class ChannelType(str, Enum):
    """고객 접점 채널"""
    ARS = "ars"                        # 전화 ARS
    GOOGLE_BUSINESS = "google_business"  # 구글 마이 비즈니스
    ONLINE_REVIEW = "online_review"    # 온라인 리뷰
    IN_STORE = "in_store"             # 오프라인 매장


class InteractionType(str, Enum):
    """상호작용 종류"""
    ORDER = "order"                    # 주문
    INQUIRY = "inquiry"                # 문의
    COMPLAINT = "complaint"            # 불만
    REVIEW = "review"                  # 리뷰
    FEEDBACK = "feedback"              # 피드백


class SentimentType(str, Enum):
    """감정 분석"""
    POSITIVE = "positive"              # 긍정
    NEUTRAL = "neutral"                # 중립
    NEGATIVE = "negative"              # 부정


class CustomerInteraction:
    """고객 상호작용"""
    
    def __init__(
        self,
        interaction_id: str,
        agent_id: str,
        channel: ChannelType,
        interaction_type: InteractionType
    ):
        self.interaction_id = interaction_id
        self.agent_id = agent_id
        self.channel = channel
        self.interaction_type = interaction_type
        
        self.created_at = datetime.now()
        
        # 고객 정보
        self.customer_name: Optional[str] = None
        self.customer_phone: Optional[str] = None
        self.customer_id: Optional[str] = None
        
        # 내용
        self.content: str = ""
        self.agent_response: Optional[str] = None
        
        # 분석
        self.sentiment: Optional[SentimentType] = None
        self.keywords: List[str] = []
        
        # 상태
        self.is_resolved: bool = False
        self.resolved_at: Optional[datetime] = None
        
        # 평가
        self.customer_rating: Optional[int] = None  # 1-5
    
    def to_dict(self) -> Dict:
        return {
            "interaction_id": self.interaction_id,
            "agent_id": self.agent_id,
            "channel": self.channel.value,
            "interaction_type": self.interaction_type.value,
            "created_at": self.created_at.isoformat(),
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "content": self.content,
            "agent_response": self.agent_response,
            "sentiment": self.sentiment.value if self.sentiment else None,
            "keywords": self.keywords,
            "is_resolved": self.is_resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "customer_rating": self.customer_rating
        }


class ARSHandler:
    """ARS 전화 주문 처리"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
    
    def handle_call(
        self,
        caller_phone: str,
        content: str
    ) -> CustomerInteraction:
        """
        전화 주문 처리
        
        Args:
            caller_phone: 전화번호
            content: 주문 내용
        
        Returns:
            생성된 상호작용
        """
        interaction_id = f"ARS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        interaction = CustomerInteraction(
            interaction_id=interaction_id,
            agent_id=self.agent_id,
            channel=ChannelType.ARS,
            interaction_type=InteractionType.ORDER
        )
        
        interaction.customer_phone = caller_phone
        interaction.content = content
        
        # 자동 응답 생성
        response = self._generate_response(content)
        interaction.agent_response = response
        
        print(f"📞 ARS 주문 접수: {caller_phone}")
        print(f"   내용: {content}")
        print(f"   응답: {response}")
        
        return interaction
    
    def _generate_response(self, content: str) -> str:
        """주문에 대한 자동 응답 생성"""
        # 실제로는 AI 모델 사용
        return f"주문 접수되었습니다. 감사합니다!"


class GoogleBusinessManager:
    """구글 마이 비즈니스 관리"""
    
    def __init__(self, agent_id: str, google_business_id: str):
        self.agent_id = agent_id
        self.google_business_id = google_business_id
    
    def fetch_reviews(self) -> List[Dict]:
        """
        리뷰 가져오기
        
        Returns:
            리뷰 목록
        """
        # 실제로는 Google My Business API 호출
        # 예시 데이터
        reviews = [
            {
                "review_id": "GMB-001",
                "author": "홍길동",
                "rating": 5,
                "text": "음식이 정말 맛있어요!",
                "created_at": datetime.now().isoformat()
            },
            {
                "review_id": "GMB-002",
                "author": "김철수",
                "rating": 3,
                "text": "맛은 좋은데 조금 비싸네요",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        return reviews
    
    def analyze_review(self, review: Dict) -> CustomerInteraction:
        """
        리뷰 분석
        
        Args:
            review: 리뷰 데이터
        
        Returns:
            분석된 상호작용
        """
        interaction_id = f"GMB-{review['review_id']}"
        
        interaction = CustomerInteraction(
            interaction_id=interaction_id,
            agent_id=self.agent_id,
            channel=ChannelType.GOOGLE_BUSINESS,
            interaction_type=InteractionType.REVIEW
        )
        
        interaction.customer_name = review['author']
        interaction.content = review['text']
        interaction.customer_rating = review['rating']
        
        # 감정 분석
        interaction.sentiment = self._analyze_sentiment(review['text'], review['rating'])
        
        # 키워드 추출
        interaction.keywords = self._extract_keywords(review['text'])
        
        return interaction
    
    def respond_to_review(self, review_id: str, response: str) -> bool:
        """
        리뷰에 응답
        
        Args:
            review_id: 리뷰 ID
            response: 응답 내용
        
        Returns:
            성공 여부
        """
        # 실제로는 Google My Business API 호출
        print(f"✉️ 리뷰 응답: {review_id}")
        print(f"   내용: {response}")
        
        return True
    
    def update_business_info(self, info: Dict) -> bool:
        """
        비즈니스 정보 업데이트
        
        Args:
            info: 업데이트할 정보
        
        Returns:
            성공 여부
        """
        # 실제로는 Google My Business API 호출
        print(f"📝 비즈니스 정보 업데이트")
        
        return True
    
    def _analyze_sentiment(self, text: str, rating: int) -> SentimentType:
        """감정 분석"""
        # 실제로는 AI 모델 사용
        if rating >= 4:
            return SentimentType.POSITIVE
        elif rating == 3:
            return SentimentType.NEUTRAL
        else:
            return SentimentType.NEGATIVE
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        # 실제로는 NLP 모델 사용
        common_keywords = ["맛", "서비스", "가격", "양", "분위기"]
        return [kw for kw in common_keywords if kw in text]


class ReviewResponseGenerator:
    """리뷰 자동 응답 생성"""
    
    def __init__(self, agent_id: str, store_name: str):
        self.agent_id = agent_id
        self.store_name = store_name
    
    def generate_response(
        self,
        review_text: str,
        rating: int,
        sentiment: SentimentType
    ) -> str:
        """
        리뷰 응답 자동 생성
        
        Args:
            review_text: 리뷰 내용
            rating: 평점
            sentiment: 감정
        
        Returns:
            생성된 응답
        """
        if sentiment == SentimentType.POSITIVE:
            return self._positive_response(review_text)
        elif sentiment == SentimentType.NEGATIVE:
            return self._negative_response(review_text)
        else:
            return self._neutral_response(review_text)
    
    def _positive_response(self, review_text: str) -> str:
        """긍정 리뷰 응답"""
        return (
            f"소중한 리뷰 감사합니다! 😊\n"
            f"{self.store_name}를 이용해주셔서 정말 감사드립니다. "
            f"앞으로도 더 나은 서비스로 보답하겠습니다!"
        )
    
    def _negative_response(self, review_text: str) -> str:
        """부정 리뷰 응답"""
        return (
            f"귀중한 의견 감사드립니다.\n"
            f"불편을 끼쳐드려 대단히 죄송합니다. "
            f"말씀해주신 부분은 즉시 개선하도록 하겠습니다. "
            f"다음에는 더 나은 경험을 제공할 수 있도록 최선을 다하겠습니다."
        )
    
    def _neutral_response(self, review_text: str) -> str:
        """중립 리뷰 응답"""
        return (
            f"리뷰 남겨주셔서 감사합니다.\n"
            f"말씀해주신 부분은 앞으로 개선할 수 있도록 노력하겠습니다. "
            f"다음에도 {self.store_name}를 찾아주시면 감사하겠습니다!"
        )


class BusinessOperationsManager:
    """
    비즈니스 운영 관리자
    
    에이전트의 모든 업무를 통합 관리:
    - ARS 전화 주문
    - 구글 마이 비즈니스
    - 온라인 리뷰 관리
    """
    
    def __init__(self, db_connection, agent_id: str):
        """
        Args:
            db_connection: 데이터베이스 연결
            agent_id: 에이전트 ID
        """
        self.db = db_connection
        self.agent_id = agent_id
        
        # 핸들러 초기화
        self.ars_handler = ARSHandler(agent_id)
        self.google_business_manager: Optional[GoogleBusinessManager] = None
        self.response_generator: Optional[ReviewResponseGenerator] = None
    
    def setup_google_business(
        self,
        google_business_id: str,
        store_name: str
    ):
        """
        구글 마이 비즈니스 설정
        
        Args:
            google_business_id: 구글 비즈니스 ID
            store_name: 가게 이름
        """
        self.google_business_manager = GoogleBusinessManager(
            self.agent_id,
            google_business_id
        )
        
        self.response_generator = ReviewResponseGenerator(
            self.agent_id,
            store_name
        )
        
        print(f"✅ 구글 마이 비즈니스 설정 완료")
    
    def process_ars_call(
        self,
        caller_phone: str,
        content: str
    ) -> CustomerInteraction:
        """
        ARS 전화 처리
        
        Args:
            caller_phone: 전화번호
            content: 주문 내용
        
        Returns:
            처리된 상호작용
        """
        interaction = self.ars_handler.handle_call(caller_phone, content)
        
        # 데이터베이스 저장
        self._save_interaction(interaction)
        
        return interaction
    
    def sync_google_reviews(self) -> List[CustomerInteraction]:
        """
        구글 리뷰 동기화 및 분석
        
        Returns:
            분석된 리뷰들
        """
        if not self.google_business_manager:
            raise ValueError("구글 마이 비즈니스가 설정되지 않았습니다.")
        
        # 리뷰 가져오기
        reviews = self.google_business_manager.fetch_reviews()
        
        interactions = []
        for review in reviews:
            # 리뷰 분석
            interaction = self.google_business_manager.analyze_review(review)
            
            # 자동 응답 생성
            if self.response_generator:
                response = self.response_generator.generate_response(
                    interaction.content,
                    interaction.customer_rating,
                    interaction.sentiment
                )
                
                interaction.agent_response = response
                
                # 응답 전송
                self.google_business_manager.respond_to_review(
                    review['review_id'],
                    response
                )
            
            # 저장
            self._save_interaction(interaction)
            interactions.append(interaction)
        
        print(f"✅ 리뷰 {len(reviews)}개 동기화 완료")
        
        return interactions
    
    def get_daily_interactions(self, date: Optional[datetime] = None) -> List[CustomerInteraction]:
        """
        일일 고객 상호작용 조회
        
        Args:
            date: 날짜 (None이면 오늘)
        
        Returns:
            상호작용 목록
        """
        if not date:
            date = datetime.now()
        
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT * FROM interactions 
            WHERE agent_id = ? 
            AND DATE(created_at) = DATE(?)
            ORDER BY created_at DESC
        """, (self.agent_id, date))
        
        rows = cursor.fetchall()
        return [self._row_to_interaction(row) for row in rows]
    
    def get_interaction_stats(self) -> Dict:
        """상호작용 통계"""
        cursor = self.db.cursor()
        
        stats = {}
        
        # 채널별 집계
        cursor.execute("""
            SELECT channel, COUNT(*) 
            FROM interactions 
            WHERE agent_id = ?
            GROUP BY channel
        """, (self.agent_id,))
        stats['by_channel'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 감정별 집계
        cursor.execute("""
            SELECT sentiment, COUNT(*) 
            FROM interactions 
            WHERE agent_id = ? AND sentiment IS NOT NULL
            GROUP BY sentiment
        """, (self.agent_id,))
        stats['by_sentiment'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 평균 평점
        cursor.execute("""
            SELECT AVG(customer_rating) 
            FROM interactions 
            WHERE agent_id = ? AND customer_rating IS NOT NULL
        """, (self.agent_id,))
        stats['avg_rating'] = cursor.fetchone()[0] or 0.0
        
        return stats
    
    # ============================================
    # Private Methods
    # ============================================
    
    def _save_interaction(self, interaction: CustomerInteraction):
        """상호작용 저장"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO interactions (
                interaction_id, agent_id, channel, interaction_type,
                created_at, customer_name, customer_phone, content,
                agent_response, sentiment, keywords, customer_rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            interaction.interaction_id,
            interaction.agent_id,
            interaction.channel.value,
            interaction.interaction_type.value,
            interaction.created_at,
            interaction.customer_name,
            interaction.customer_phone,
            interaction.content,
            interaction.agent_response,
            interaction.sentiment.value if interaction.sentiment else None,
            json.dumps(interaction.keywords),
            interaction.customer_rating
        ))
        self.db.commit()
    
    def _row_to_interaction(self, row) -> CustomerInteraction:
        """DB 행을 Interaction으로 변환"""
        interaction = CustomerInteraction(
            interaction_id=row['interaction_id'],
            agent_id=row['agent_id'],
            channel=ChannelType(row['channel']),
            interaction_type=InteractionType(row['interaction_type'])
        )
        # ... 기타 필드 로드
        return interaction


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # manager = BusinessOperationsManager(db_connection, "AGENT-001")
    
    # 구글 비즈니스 설정
    # manager.setup_google_business(
    #     google_business_id="ChIJxxxxx",
    #     store_name="맛있는 김밥"
    # )
    
    # ARS 주문 처리
    # interaction = manager.process_ars_call(
    #     caller_phone="010-1234-5678",
    #     content="김밥 2줄 주세요"
    # )
    
    # 구글 리뷰 동기화
    # reviews = manager.sync_google_reviews()
    
    # 통계 조회
    # stats = manager.get_interaction_stats()
    
    print("✅ Business Operations 모듈 로드 완료")

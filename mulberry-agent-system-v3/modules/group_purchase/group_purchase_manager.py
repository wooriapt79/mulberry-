"""
Mulberry Group Purchase Module
CTO Koda

Mastodon + ActivityPub 기반 공동구매 시스템
식품사막화 지역 생산품 → 도시 지역 공동구매
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from enum import Enum
import json


class GroupPurchaseStatus(str, Enum):
    """공동구매 상태"""
    PENDING = "pending"              # 대기중
    ACTIVE = "active"                # 진행중
    SUCCESS = "success"              # 목표 달성
    FAILED = "failed"                # 목표 미달
    COMPLETED = "completed"          # 완료 (배송중)
    CLOSED = "closed"                # 종료


class ProductCategory(str, Enum):
    """상품 카테고리"""
    FRESH_FOOD = "fresh_food"        # 신선식품
    AGRICULTURAL = "agricultural"     # 농산물
    SEAFOOD = "seafood"              # 수산물
    PROCESSED = "processed"          # 가공식품
    CRAFT = "craft"                  # 공예품
    SPECIAL = "special"              # 특산품


class DeliveryType(str, Enum):
    """배송 유형"""
    DIRECT = "direct"                # 직접 배송
    PICKUP = "pickup"                # 픽업
    SHARED = "shared"                # 공동 배송 (마을 단위)


class GroupPurchaseProduct:
    """
    공동구매 상품
    """
    
    def __init__(
        self,
        product_id: str,
        name: str,
        description: str,
        category: ProductCategory,
        producer_agent_id: str,
        producer_location: str  # 식품사막화 지역
    ):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.category = category
        self.producer_agent_id = producer_agent_id
        self.producer_location = producer_location
        
        # 가격 정보
        self.original_price: float = 0.0
        self.group_price: float = 0.0  # 공동구매 할인가
        self.discount_rate: float = 0.0
        
        # 목표
        self.min_quantity: int = 10  # 최소 인원
        self.max_quantity: int = 100  # 최대 인원
        
        # 기간
        self.start_at: datetime = datetime.now()
        self.end_at: datetime = datetime.now() + timedelta(days=7)
        
        # 이미지
        self.image_urls: List[str] = []
        
        # 배송
        self.delivery_type: DeliveryType = DeliveryType.DIRECT
        self.delivery_fee: float = 0.0
        
        # 생산자 정보
        self.producer_story: Optional[str] = None
        
        # ActivityPub
        self.activitypub_uri: Optional[str] = None  # 연합 공유용
        
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "producer_agent_id": self.producer_agent_id,
            "producer_location": self.producer_location,
            "original_price": self.original_price,
            "group_price": self.group_price,
            "discount_rate": self.discount_rate,
            "min_quantity": self.min_quantity,
            "max_quantity": self.max_quantity,
            "start_at": self.start_at.isoformat(),
            "end_at": self.end_at.isoformat(),
            "image_urls": self.image_urls,
            "delivery_type": self.delivery_type.value,
            "delivery_fee": self.delivery_fee,
            "producer_story": self.producer_story,
            "activitypub_uri": self.activitypub_uri,
            "created_at": self.created_at.isoformat()
        }
    
    def to_activitypub_object(self) -> Dict:
        """
        ActivityPub Object 변환
        
        연합 네트워크에서 공유 가능한 형태
        """
        return {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Article",  # 또는 "Offer"
            "id": self.activitypub_uri,
            "name": f"🔥 공동구매: {self.name}",
            "content": f"""
{self.description}

📍 생산지: {self.producer_location}
💰 가격: {self.original_price:,}원 → {self.group_price:,}원 ({self.discount_rate}% 할인)
👥 최소 인원: {self.min_quantity}명
⏰ 마감: {self.end_at.strftime('%Y-%m-%d %H:%M')}

#공동구매 #식품사막화해결 #Mulberry
            """.strip(),
            "published": self.created_at.isoformat(),
            "url": f"https://mulberry.app/group-purchase/{self.product_id}",
            "image": self.image_urls[0] if self.image_urls else None,
            "tag": [
                {"type": "Hashtag", "name": "#공동구매"},
                {"type": "Hashtag", "name": "#식품사막화해결"},
                {"type": "Hashtag", "name": f"#{self.category.value}"}
            ]
        }


class GroupPurchaseCampaign:
    """
    공동구매 캠페인
    
    하나의 상품에 대한 공동구매 진행 상황
    """
    
    def __init__(
        self,
        campaign_id: str,
        product_id: str,
        min_participants: int,
        target_quantity: int
    ):
        self.campaign_id = campaign_id
        self.product_id = product_id
        self.min_participants = min_participants
        self.target_quantity = target_quantity
        
        self.current_participants: int = 0
        self.current_quantity: int = 0
        
        self.status = GroupPurchaseStatus.PENDING
        
        self.start_at = datetime.now()
        self.end_at = datetime.now() + timedelta(days=7)
        
        # 참여자 목록
        self.participants: List[str] = []  # user_id 목록
        
        # ActivityPub 활동
        self.activity_uri: Optional[str] = None
        
        self.created_at = datetime.now()
    
    def add_participant(self, user_id: str, quantity: int) -> bool:
        """
        참여자 추가
        
        Args:
            user_id: 사용자 ID (Mastodon 계정 등)
            quantity: 구매 수량
        
        Returns:
            성공 여부
        """
        if self.status != GroupPurchaseStatus.ACTIVE:
            return False
        
        if user_id not in self.participants:
            self.participants.append(user_id)
            self.current_participants += 1
        
        self.current_quantity += quantity
        
        # 목표 달성 체크
        if self.current_participants >= self.min_participants:
            self.status = GroupPurchaseStatus.SUCCESS
        
        return True
    
    def get_progress(self) -> Dict:
        """진행률 조회"""
        return {
            "campaign_id": self.campaign_id,
            "status": self.status.value,
            "current_participants": self.current_participants,
            "target_participants": self.min_participants,
            "progress_percent": round(
                self.current_participants / self.min_participants * 100, 1
            ),
            "current_quantity": self.current_quantity,
            "target_quantity": self.target_quantity,
            "time_left": (self.end_at - datetime.now()).total_seconds(),
            "is_success": self.status == GroupPurchaseStatus.SUCCESS
        }
    
    def to_activitypub_note(self, product_name: str) -> Dict:
        """
        진행 상황을 ActivityPub Note로 변환
        
        Mastodon 타임라인에 자동 포스팅용
        """
        progress = self.get_progress()
        
        # 상태별 이모지
        status_emoji = {
            GroupPurchaseStatus.PENDING: "⏳",
            GroupPurchaseStatus.ACTIVE: "🔥",
            GroupPurchaseStatus.SUCCESS: "🎉",
            GroupPurchaseStatus.FAILED: "😢",
            GroupPurchaseStatus.COMPLETED: "✅"
        }
        
        emoji = status_emoji.get(self.status, "📦")
        
        return {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Note",
            "id": self.activity_uri,
            "content": f"""
{emoji} {product_name} 공동구매 진행중!

👥 참여: {self.current_participants}/{self.min_participants}명 ({progress['progress_percent']}%)
📦 수량: {self.current_quantity}/{self.target_quantity}개
⏰ 남은 시간: {int(progress['time_left'] / 3600)}시간

👉 지금 참여하기: https://mulberry.app/group-purchase/{self.campaign_id}

#공동구매 #Mulberry
            """.strip(),
            "published": datetime.now().isoformat(),
            "tag": [
                {"type": "Hashtag", "name": "#공동구매"}
            ]
        }


class MastodonOAuthIntegration:
    """
    Mastodon OAuth 통합
    
    Mastodon 계정으로 로그인 및 타임라인 포스팅
    """
    
    def __init__(self, instance_url: str, client_id: str, client_secret: str):
        """
        Args:
            instance_url: Mastodon 인스턴스 URL (예: https://mastodon.social)
            client_id: OAuth 클라이언트 ID
            client_secret: OAuth 클라이언트 시크릿
        """
        self.instance_url = instance_url
        self.client_id = client_id
        self.client_secret = client_secret
    
    def get_authorization_url(self, redirect_uri: str) -> str:
        """
        OAuth 인증 URL 생성
        
        Args:
            redirect_uri: 인증 후 리다이렉트 URL
        
        Returns:
            인증 URL
        """
        return f"{self.instance_url}/oauth/authorize?client_id={self.client_id}&redirect_uri={redirect_uri}&response_type=code&scope=read write follow"
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> str:
        """
        인증 코드를 액세스 토큰으로 교환
        
        실제 구현 시 HTTP 요청 필요
        """
        # TODO: 실제 HTTP 요청
        # POST /oauth/token
        return "mock_access_token"
    
    def post_to_timeline(self, access_token: str, status: str, visibility: str = "public") -> Dict:
        """
        타임라인에 포스트
        
        Args:
            access_token: 사용자 액세스 토큰
            status: 포스트 내용
            visibility: 공개 범위 (public, unlisted, private)
        
        Returns:
            포스트 정보
        """
        # TODO: 실제 Mastodon API 호출
        # POST /api/v1/statuses
        return {
            "id": "mock_status_id",
            "url": f"{self.instance_url}/@user/12345",
            "created_at": datetime.now().isoformat()
        }


class GroupPurchaseManager:
    """
    공동구매 관리자
    
    상품 등록, 캠페인 생성, 참여 처리, ActivityPub 연동
    """
    
    def __init__(self, db_connection, mastodon_oauth: Optional[MastodonOAuthIntegration] = None):
        """
        Args:
            db_connection: 데이터베이스 연결
            mastodon_oauth: Mastodon OAuth 통합 (옵션)
        """
        self.db = db_connection
        self.mastodon = mastodon_oauth
    
    def create_product(
        self,
        name: str,
        description: str,
        category: ProductCategory,
        producer_agent_id: str,
        producer_location: str,
        original_price: float,
        group_price: float,
        min_quantity: int = 10,
        **kwargs
    ) -> GroupPurchaseProduct:
        """
        공동구매 상품 등록
        
        Args:
            name: 상품명
            description: 설명
            category: 카테고리
            producer_agent_id: 생산자 에이전트 ID
            producer_location: 생산 지역 (식품사막화 지역)
            original_price: 정상가
            group_price: 공동구매가
            min_quantity: 최소 수량
        
        Returns:
            생성된 상품
        """
        product_id = f"GP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        product = GroupPurchaseProduct(
            product_id=product_id,
            name=name,
            description=description,
            category=category,
            producer_agent_id=producer_agent_id,
            producer_location=producer_location
        )
        
        product.original_price = original_price
        product.group_price = group_price
        product.discount_rate = round((1 - group_price / original_price) * 100, 1)
        product.min_quantity = min_quantity
        
        # 추가 옵션
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        # ActivityPub URI 생성
        product.activitypub_uri = f"https://mulberry.app/ap/products/{product_id}"
        
        # 데이터베이스 저장
        self._save_product(product)
        
        print(f"✅ 공동구매 상품 등록: {name}")
        print(f"   가격: {original_price:,}원 → {group_price:,}원 ({product.discount_rate}% 할인)")
        print(f"   최소 수량: {min_quantity}개")
        
        return product
    
    def create_campaign(
        self,
        product_id: str,
        duration_days: int = 7
    ) -> GroupPurchaseCampaign:
        """
        공동구매 캠페인 시작
        
        Args:
            product_id: 상품 ID
            duration_days: 진행 기간 (일)
        
        Returns:
            생성된 캠페인
        """
        # 상품 조회
        product = self._load_product(product_id)
        
        campaign_id = f"CAMP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        campaign = GroupPurchaseCampaign(
            campaign_id=campaign_id,
            product_id=product_id,
            min_participants=product.min_quantity,
            target_quantity=product.max_quantity
        )
        
        campaign.end_at = datetime.now() + timedelta(days=duration_days)
        campaign.status = GroupPurchaseStatus.ACTIVE
        campaign.activity_uri = f"https://mulberry.app/ap/campaigns/{campaign_id}"
        
        # 데이터베이스 저장
        self._save_campaign(campaign)
        
        # Mastodon 타임라인에 자동 포스팅
        if self.mastodon:
            self._post_campaign_to_mastodon(campaign, product)
        
        print(f"✅ 공동구매 캠페인 시작: {campaign_id}")
        print(f"   상품: {product.name}")
        print(f"   마감: {campaign.end_at.strftime('%Y-%m-%d %H:%M')}")
        
        return campaign
    
    def join_campaign(
        self,
        campaign_id: str,
        user_id: str,
        quantity: int = 1
    ) -> Dict:
        """
        공동구매 참여
        
        Args:
            campaign_id: 캠페인 ID
            user_id: 사용자 ID (Mastodon 계정 등)
            quantity: 구매 수량
        
        Returns:
            참여 결과
        """
        campaign = self._load_campaign(campaign_id)
        product = self._load_product(campaign.product_id)
        
        # 참여 처리
        success = campaign.add_participant(user_id, quantity)
        
        if not success:
            return {
                "success": False,
                "message": "캠페인이 종료되었거나 참여할 수 없습니다."
            }
        
        # 데이터베이스 업데이트
        self._update_campaign(campaign)
        
        # 주문 기록 생성
        order = self._create_order(campaign_id, user_id, product, quantity)
        
        # 진행 상황 업데이트 (Mastodon 타임라인)
        if self.mastodon and campaign.current_participants % 5 == 0:
            # 5명씩 참여할 때마다 업데이트
            self._update_campaign_progress(campaign, product)
        
        print(f"✅ 공동구매 참여: {user_id}")
        print(f"   상품: {product.name}")
        print(f"   수량: {quantity}개")
        print(f"   현재 참여: {campaign.current_participants}명")
        
        return {
            "success": True,
            "order_id": order["order_id"],
            "campaign": campaign.get_progress(),
            "message": "공동구매 참여가 완료되었습니다!"
        }
    
    def get_hot_deals(self, limit: int = 10) -> List[Dict]:
        """
        오늘의 핫딜 조회
        
        Args:
            limit: 개수
        
        Returns:
            핫딜 목록
        """
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT p.*, c.current_participants, c.min_participants
            FROM group_purchase_products p
            JOIN group_purchase_campaigns c ON p.product_id = c.product_id
            WHERE c.status = 'active'
            AND c.end_at > ?
            ORDER BY c.current_participants DESC, p.discount_rate DESC
            LIMIT ?
        """, (datetime.now(), limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_village_purchases(self, village_id: str) -> List[Dict]:
        """
        우리 마을 공동구매
        
        같은 마을/지역의 공동구매 목록
        
        Args:
            village_id: 마을 ID
        
        Returns:
            공동구매 목록
        """
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT p.*, c.*
            FROM group_purchase_products p
            JOIN group_purchase_campaigns c ON p.product_id = c.product_id
            WHERE p.producer_location = ?
            AND c.status = 'active'
            ORDER BY c.end_at ASC
        """, (village_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ============================================
    # ActivityPub 연동
    # ============================================
    
    def publish_to_fediverse(self, product: GroupPurchaseProduct):
        """
        연합 네트워크에 공동구매 상품 공유
        
        ActivityPub을 통해 다른 Mastodon 인스턴스에도 전파
        """
        activity = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "actor": f"https://mulberry.app/ap/actors/mulberry",
            "object": product.to_activitypub_object(),
            "to": ["https://www.w3.org/ns/activitystreams#Public"]
        }
        
        # TODO: ActivityPub 서버로 전송
        # 각 팔로워 인스턴스의 inbox로 POST
        
        print(f"📡 연합 네트워크에 공유: {product.name}")
    
    # ============================================
    # Private Methods
    # ============================================
    
    def _save_product(self, product: GroupPurchaseProduct):
        """상품 저장"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO group_purchase_products (
                product_id, name, description, category,
                producer_agent_id, producer_location,
                original_price, group_price, discount_rate,
                min_quantity, max_quantity,
                start_at, end_at,
                image_urls, delivery_type, delivery_fee,
                producer_story, activitypub_uri, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product.product_id, product.name, product.description,
            product.category.value, product.producer_agent_id,
            product.producer_location, product.original_price,
            product.group_price, product.discount_rate,
            product.min_quantity, product.max_quantity,
            product.start_at, product.end_at,
            json.dumps(product.image_urls), product.delivery_type.value,
            product.delivery_fee, product.producer_story,
            product.activitypub_uri, product.created_at
        ))
        self.db.commit()
    
    def _save_campaign(self, campaign: GroupPurchaseCampaign):
        """캠페인 저장"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO group_purchase_campaigns (
                campaign_id, product_id, min_participants, target_quantity,
                current_participants, current_quantity, status,
                start_at, end_at, participants, activity_uri, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign.campaign_id, campaign.product_id,
            campaign.min_participants, campaign.target_quantity,
            campaign.current_participants, campaign.current_quantity,
            campaign.status.value, campaign.start_at, campaign.end_at,
            json.dumps(campaign.participants), campaign.activity_uri,
            campaign.created_at
        ))
        self.db.commit()
    
    def _update_campaign(self, campaign: GroupPurchaseCampaign):
        """캠페인 업데이트"""
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE group_purchase_campaigns
            SET current_participants = ?,
                current_quantity = ?,
                status = ?,
                participants = ?
            WHERE campaign_id = ?
        """, (
            campaign.current_participants,
            campaign.current_quantity,
            campaign.status.value,
            json.dumps(campaign.participants),
            campaign.campaign_id
        ))
        self.db.commit()
    
    def _create_order(self, campaign_id: str, user_id: str, product: GroupPurchaseProduct, quantity: int) -> Dict:
        """주문 생성"""
        order_id = f"ORDER-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO group_purchase_orders (
                order_id, campaign_id, user_id, product_id,
                quantity, unit_price, total_price, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id, campaign_id, user_id, product.product_id,
            quantity, product.group_price,
            product.group_price * quantity,
            datetime.now()
        ))
        self.db.commit()
        
        return {"order_id": order_id}
    
    def _load_product(self, product_id: str) -> GroupPurchaseProduct:
        """상품 조회"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT * FROM group_purchase_products
            WHERE product_id = ?
        """, (product_id,))
        
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Product {product_id} not found")
        
        # TODO: row를 GroupPurchaseProduct로 변환
        return GroupPurchaseProduct(
            product_id=row['product_id'],
            name=row['name'],
            description=row['description'],
            category=ProductCategory(row['category']),
            producer_agent_id=row['producer_agent_id'],
            producer_location=row['producer_location']
        )
    
    def _load_campaign(self, campaign_id: str) -> GroupPurchaseCampaign:
        """캠페인 조회"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT * FROM group_purchase_campaigns
            WHERE campaign_id = ?
        """, (campaign_id,))
        
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Campaign {campaign_id} not found")
        
        # TODO: row를 GroupPurchaseCampaign로 변환
        return GroupPurchaseCampaign(
            campaign_id=row['campaign_id'],
            product_id=row['product_id'],
            min_participants=row['min_participants'],
            target_quantity=row['target_quantity']
        )
    
    def _post_campaign_to_mastodon(self, campaign: GroupPurchaseCampaign, product: GroupPurchaseProduct):
        """캠페인을 Mastodon 타임라인에 포스팅"""
        if not self.mastodon:
            return
        
        note = campaign.to_activitypub_note(product.name)
        # TODO: 실제 Mastodon API 호출
        print(f"📱 Mastodon 타임라인 포스팅: {product.name}")
    
    def _update_campaign_progress(self, campaign: GroupPurchaseCampaign, product: GroupPurchaseProduct):
        """진행 상황 업데이트 (Mastodon)"""
        if not self.mastodon:
            return
        
        note = campaign.to_activitypub_note(product.name)
        # TODO: 실제 Mastodon API 호출
        print(f"📱 진행 상황 업데이트: {campaign.current_participants}명 참여")


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # manager = GroupPurchaseManager(db_connection, mastodon_oauth)
    
    # 상품 등록
    # product = manager.create_product(
    #     name="인제 옥수수 1박스 (10개)",
    #     description="강원도 인제군에서 자란 신선한 옥수수",
    #     category=ProductCategory.AGRICULTURAL,
    #     producer_agent_id="AGENT-INJE-001",
    #     producer_location="강원도 인제군",
    #     original_price=30000,
    #     group_price=20000,
    #     min_quantity=20
    # )
    
    # 캠페인 시작
    # campaign = manager.create_campaign(product.product_id, duration_days=7)
    
    # 공동구매 참여
    # result = manager.join_campaign(campaign.campaign_id, "user@mastodon.social", quantity=2)
    
    # 핫딜 조회
    # hot_deals = manager.get_hot_deals(10)
    
    print("✅ Group Purchase Manager 로드 완료")

"""
Mulberry Agentic Commerce - 장바구니 모듈
CTO Koda

에이전트별 가상 장바구니 시스템
"""

from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal
import json
import redis


class CartItem(BaseModel):
    """장바구니 아이템"""
    product_id: str
    product_name: str
    quantity: int = Field(gt=0)
    price: Decimal
    discount: Decimal = Decimal('0')
    total: Decimal = Field(default=Decimal('0'))
    
    def __init__(self, **data):
        super().__init__(**data)
        self.calculate_total()
    
    def calculate_total(self):
        """총액 계산"""
        self.total = (self.price * self.quantity) - self.discount
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class Cart(BaseModel):
    """장바구니"""
    cart_id: str
    agent_id: str
    items: List[CartItem] = Field(default_factory=list)
    subtotal: Decimal = Decimal('0')
    discount_total: Decimal = Decimal('0')
    tax: Decimal = Decimal('0')
    total: Decimal = Decimal('0')
    currency: str = "KRW"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def calculate_totals(self):
        """총액 계산"""
        self.subtotal = sum(item.total for item in self.items)
        self.discount_total = sum(item.discount for item in self.items)
        self.tax = self.subtotal * Decimal('0.1')  # 10% 세금
        self.total = self.subtotal + self.tax
        self.updated_at = datetime.now()
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }


class CartManager:
    """
    장바구니 관리자
    Redis 기반 빠른 캐싱
    """
    
    def __init__(self, redis_client: redis.Redis, db_connection):
        """
        Args:
            redis_client: Redis 클라이언트
            db_connection: 데이터베이스 연결
        """
        self.redis = redis_client
        self.db = db_connection
        self.cache_ttl = 3600  # 1시간
    
    def create_cart(self, agent_id: str) -> Cart:
        """
        새 장바구니 생성
        
        Args:
            agent_id: 에이전트 ID
        
        Returns:
            생성된 장바구니
        """
        cart_id = f"CART-{agent_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cart = Cart(
            cart_id=cart_id,
            agent_id=agent_id
        )
        
        # Redis에 캐싱
        self._cache_cart(cart)
        
        return cart
    
    def get_cart(self, cart_id: str) -> Optional[Cart]:
        """
        장바구니 조회
        
        Args:
            cart_id: 장바구니 ID
        
        Returns:
            장바구니 또는 None
        """
        # Redis에서 먼저 조회
        cached = self._get_cached_cart(cart_id)
        if cached:
            return cached
        
        # DB에서 조회
        cart = self._load_cart_from_db(cart_id)
        if cart:
            self._cache_cart(cart)
        
        return cart
    
    def get_agent_active_cart(self, agent_id: str) -> Cart:
        """
        에이전트의 활성 장바구니 조회/생성
        
        Args:
            agent_id: 에이전트 ID
        
        Returns:
            활성 장바구니
        """
        # Redis에서 활성 카트 조회
        active_cart_key = f"active_cart:{agent_id}"
        cart_id = self.redis.get(active_cart_key)
        
        if cart_id:
            cart = self.get_cart(cart_id.decode())
            if cart:
                return cart
        
        # 없으면 새로 생성
        cart = self.create_cart(agent_id)
        self.redis.setex(active_cart_key, self.cache_ttl, cart.cart_id)
        
        return cart
    
    def add_item(
        self,
        cart_id: str,
        product_id: str,
        product_name: str,
        quantity: int,
        price: Decimal,
        discount: Decimal = Decimal('0')
    ) -> Cart:
        """
        상품 추가
        
        Args:
            cart_id: 장바구니 ID
            product_id: 상품 ID
            product_name: 상품명
            quantity: 수량
            price: 가격
            discount: 할인액
        
        Returns:
            업데이트된 장바구니
        """
        cart = self.get_cart(cart_id)
        if not cart:
            raise ValueError(f"Cart {cart_id} not found")
        
        # 이미 있는 상품인지 확인
        existing_item = next(
            (item for item in cart.items if item.product_id == product_id),
            None
        )
        
        if existing_item:
            # 수량 증가
            existing_item.quantity += quantity
            existing_item.calculate_total()
        else:
            # 새 아이템 추가
            item = CartItem(
                product_id=product_id,
                product_name=product_name,
                quantity=quantity,
                price=price,
                discount=discount
            )
            cart.items.append(item)
        
        # 총액 재계산
        cart.calculate_totals()
        
        # 저장
        self._cache_cart(cart)
        self._save_cart_to_db(cart)
        
        return cart
    
    def update_item_quantity(
        self,
        cart_id: str,
        product_id: str,
        quantity: int
    ) -> Cart:
        """
        상품 수량 변경
        
        Args:
            cart_id: 장바구니 ID
            product_id: 상품 ID
            quantity: 새 수량
        
        Returns:
            업데이트된 장바구니
        """
        cart = self.get_cart(cart_id)
        if not cart:
            raise ValueError(f"Cart {cart_id} not found")
        
        item = next(
            (item for item in cart.items if item.product_id == product_id),
            None
        )
        
        if not item:
            raise ValueError(f"Product {product_id} not in cart")
        
        if quantity <= 0:
            # 수량이 0이면 삭제
            return self.remove_item(cart_id, product_id)
        
        item.quantity = quantity
        item.calculate_total()
        
        cart.calculate_totals()
        
        # 저장
        self._cache_cart(cart)
        self._save_cart_to_db(cart)
        
        return cart
    
    def remove_item(self, cart_id: str, product_id: str) -> Cart:
        """
        상품 제거
        
        Args:
            cart_id: 장바구니 ID
            product_id: 상품 ID
        
        Returns:
            업데이트된 장바구니
        """
        cart = self.get_cart(cart_id)
        if not cart:
            raise ValueError(f"Cart {cart_id} not found")
        
        cart.items = [
            item for item in cart.items 
            if item.product_id != product_id
        ]
        
        cart.calculate_totals()
        
        # 저장
        self._cache_cart(cart)
        self._save_cart_to_db(cart)
        
        return cart
    
    def clear_cart(self, cart_id: str) -> Cart:
        """
        장바구니 비우기
        
        Args:
            cart_id: 장바구니 ID
        
        Returns:
            비워진 장바구니
        """
        cart = self.get_cart(cart_id)
        if not cart:
            raise ValueError(f"Cart {cart_id} not found")
        
        cart.items = []
        cart.calculate_totals()
        
        # 저장
        self._cache_cart(cart)
        self._save_cart_to_db(cart)
        
        return cart
    
    def apply_discount(
        self,
        cart_id: str,
        product_id: Optional[str] = None,
        discount_amount: Optional[Decimal] = None,
        discount_percent: Optional[Decimal] = None
    ) -> Cart:
        """
        할인 적용
        
        Args:
            cart_id: 장바구니 ID
            product_id: 상품 ID (None이면 전체)
            discount_amount: 할인 금액
            discount_percent: 할인 퍼센트
        
        Returns:
            업데이트된 장바구니
        """
        cart = self.get_cart(cart_id)
        if not cart:
            raise ValueError(f"Cart {cart_id} not found")
        
        if product_id:
            # 특정 상품에 할인
            item = next(
                (item for item in cart.items if item.product_id == product_id),
                None
            )
            if item:
                if discount_amount:
                    item.discount = discount_amount
                elif discount_percent:
                    item.discount = item.price * item.quantity * discount_percent / 100
                item.calculate_total()
        else:
            # 전체에 할인
            for item in cart.items:
                if discount_amount:
                    # 비례 배분
                    item_ratio = item.total / cart.subtotal
                    item.discount = discount_amount * item_ratio
                elif discount_percent:
                    item.discount = item.price * item.quantity * discount_percent / 100
                item.calculate_total()
        
        cart.calculate_totals()
        
        # 저장
        self._cache_cart(cart)
        self._save_cart_to_db(cart)
        
        return cart
    
    def sync_with_server(self, cart_id: str) -> Dict:
        """
        서버와 장바구니 동기화
        
        Args:
            cart_id: 장바구니 ID
        
        Returns:
            동기화 결과 (재고 상태 등)
        """
        cart = self.get_cart(cart_id)
        if not cart:
            raise ValueError(f"Cart {cart_id} not found")
        
        # 서버 API 호출 (실제 구현 시)
        # response = requests.post(f"{SERVER_URL}/api/v1/agent/cart/sync", json=cart.dict())
        
        # 재고 확인 결과 반환
        stock_status = []
        for item in cart.items:
            # 실제로는 서버에서 받아옴
            stock_status.append({
                "product_id": item.product_id,
                "available": True,
                "stock": 100,  # 예시
                "price_changed": False
            })
        
        return {
            "cart_id": cart_id,
            "synced_at": datetime.now().isoformat(),
            "stock_status": stock_status
        }
    
    def get_cart_summary(self, cart_id: str) -> Dict:
        """
        장바구니 요약 정보
        
        Args:
            cart_id: 장바구니 ID
        
        Returns:
            요약 정보
        """
        cart = self.get_cart(cart_id)
        if not cart:
            return {}
        
        return {
            "cart_id": cart.cart_id,
            "agent_id": cart.agent_id,
            "item_count": len(cart.items),
            "total_quantity": sum(item.quantity for item in cart.items),
            "subtotal": float(cart.subtotal),
            "discount_total": float(cart.discount_total),
            "tax": float(cart.tax),
            "total": float(cart.total),
            "currency": cart.currency,
            "updated_at": cart.updated_at.isoformat()
        }
    
    # ============================================
    # Private Methods
    # ============================================
    
    def _cache_cart(self, cart: Cart):
        """Redis에 캐싱"""
        key = f"cart:{cart.cart_id}"
        value = cart.json()
        self.redis.setex(key, self.cache_ttl, value)
    
    def _get_cached_cart(self, cart_id: str) -> Optional[Cart]:
        """Redis에서 조회"""
        key = f"cart:{cart_id}"
        cached = self.redis.get(key)
        
        if cached:
            return Cart.parse_raw(cached)
        
        return None
    
    def _save_cart_to_db(self, cart: Cart):
        """데이터베이스에 저장"""
        cursor = self.db.cursor()
        
        # 카트 저장
        cursor.execute("""
            INSERT INTO carts (
                cart_id, agent_id, subtotal, discount_total,
                tax, total, currency, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (cart_id) DO UPDATE SET
                subtotal = EXCLUDED.subtotal,
                discount_total = EXCLUDED.discount_total,
                tax = EXCLUDED.tax,
                total = EXCLUDED.total,
                updated_at = EXCLUDED.updated_at
        """, (
            cart.cart_id,
            cart.agent_id,
            float(cart.subtotal),
            float(cart.discount_total),
            float(cart.tax),
            float(cart.total),
            cart.currency,
            cart.created_at,
            cart.updated_at
        ))
        
        # 아이템 저장
        cursor.execute("DELETE FROM cart_items WHERE cart_id = %s", (cart.cart_id,))
        
        for item in cart.items:
            cursor.execute("""
                INSERT INTO cart_items (
                    cart_id, product_id, product_name,
                    quantity, price, discount, total
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                cart.cart_id,
                item.product_id,
                item.product_name,
                item.quantity,
                float(item.price),
                float(item.discount),
                float(item.total)
            ))
        
        self.db.commit()
    
    def _load_cart_from_db(self, cart_id: str) -> Optional[Cart]:
        """데이터베이스에서 조회"""
        cursor = self.db.cursor()
        
        # 카트 조회
        cursor.execute(
            "SELECT * FROM carts WHERE cart_id = %s",
            (cart_id,)
        )
        cart_row = cursor.fetchone()
        
        if not cart_row:
            return None
        
        # 아이템 조회
        cursor.execute(
            "SELECT * FROM cart_items WHERE cart_id = %s",
            (cart_id,)
        )
        item_rows = cursor.fetchall()
        
        # Cart 객체 생성 (실제 구현 시 컬럼 매핑)
        items = [
            CartItem(**dict(row))
            for row in item_rows
        ]
        
        cart_data = dict(cart_row)
        cart_data['items'] = items
        
        return Cart(**cart_data)


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # Redis 연결 (실제로는 설정에서)
    # redis_client = redis.Redis(host='localhost', port=6379, db=0)
    # cart_manager = CartManager(redis_client, db_connection)
    
    # 장바구니 생성
    # cart = cart_manager.create_cart(agent_id="agent-001")
    
    # 상품 추가
    # cart = cart_manager.add_item(
    #     cart_id=cart.cart_id,
    #     product_id="PROD-001",
    #     product_name="스마트폰 XYZ",
    #     quantity=2,
    #     price=Decimal('1200000'),
    #     discount=Decimal('100000')
    # )
    
    print("✅ 장바구니 모듈 로드 완료")

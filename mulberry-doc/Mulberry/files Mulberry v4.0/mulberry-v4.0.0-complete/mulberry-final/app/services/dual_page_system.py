"""
Mulberry Phase 4-A - Dual Page System
공동구매 vs 개별 농가 페이지 이원화 및 자동 매칭
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from loguru import logger


# ============================================
# Page Types
# ============================================

class PageType(Enum):
    """페이지 타입"""
    GROUP_PURCHASE = "group_purchase"  # 공동구매
    INDIVIDUAL_FARM = "individual_farm"  # 개별 농가


class ProductStatus(Enum):
    """상품 상태"""
    AVAILABLE = "available"  # 판매 중
    LIMITED = "limited"  # 재고 부족
    SOLD_OUT = "sold_out"  # 품절
    COMING_SOON = "coming_soon"  # 입고 예정


# ============================================
# 공동구매 페이지 스키마
# ============================================

@dataclass
class GroupPurchaseProduct:
    """
    공동구매 상품
    
    여러 농가의 상품을 통합하여 대량 구매 할인
    """
    # 상품 정보
    product_id: str
    product_name: str  # 표준 상품명 (예: "사과")
    category: str  # 카테고리 (예: "과일")
    
    # 공동구매 정보
    participating_farms: List[Dict[str, Any]]  # 참여 농가 목록
    total_quantity: int  # 총 수량
    min_order_quantity: int  # 최소 주문 수량
    
    # 가격 정보
    original_price: float  # 원가
    group_price: float  # 공동구매 가격
    discount_rate: float  # 할인율
    
    # 배송 정보
    delivery_fee: float  # 배송비
    free_shipping_threshold: float  # 무료 배송 기준
    
    # 상태
    status: ProductStatus
    start_date: str
    end_date: str
    
    # 메타데이터
    description: str = ""
    images: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class GroupPurchasePage:
    """
    공동구매 페이지
    
    여러 상품을 모아서 대량 구매 할인 제공
    """
    page_id: str
    title: str
    description: str
    
    # 상품 목록
    products: List[GroupPurchaseProduct]
    
    # 페이지 설정
    theme_color: str = "#667eea"
    banner_image: Optional[str] = None
    
    # 통계
    total_participants: int = 0
    total_orders: int = 0
    
    # 메타데이터
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True


# ============================================
# 개별 농가 페이지 스키마
# ============================================

@dataclass
class IndividualFarmProduct:
    """
    개별 농가 상품
    
    특정 농가의 상품만 판매
    """
    # 상품 정보
    product_id: str
    product_name: str
    category: str
    
    # 농가 정보 (개별 농가만의 특성)
    farm_story: str  # 농가 스토리
    farming_method: str  # 재배 방법
    certification: List[str]  # 인증 (유기농, GAP 등)
    
    # 가격 정보
    price: float
    unit: str  # kg, 개 등
    
    # 재고
    available_quantity: int
    status: ProductStatus
    
    # 메타데이터
    harvest_date: Optional[str] = None  # 수확일
    description: str = ""
    images: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class FarmerProfile:
    """농부 프로필"""
    farmer_id: str
    name: str
    farm_name: str
    location: str  # 인제군 기린면 등
    
    # 스토리
    introduction: str  # 자기소개
    philosophy: str  # 농사 철학
    experience_years: int  # 경력
    
    # 연락처
    phone: str
    email: Optional[str] = None
    
    # SNS
    mastodon_handle: Optional[str] = None
    
    # 통계
    total_products: int = 0
    total_sales: int = 0
    customer_rating: float = 0.0


@dataclass
class IndividualFarmPage:
    """
    개별 농가 페이지
    
    특정 농가의 상품과 스토리 중심
    """
    page_id: str
    farm_id: str
    
    # 농부 정보
    farmer: FarmerProfile
    
    # 상품 목록
    products: List[IndividualFarmProduct]
    
    # 페이지 디자인
    theme_color: str = "#10b981"  # 녹색 계열
    cover_image: Optional[str] = None
    farm_photos: List[str] = field(default_factory=list)
    
    # 고객 후기
    reviews: List[Dict[str, Any]] = field(default_factory=list)
    
    # 메타데이터
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True


# ============================================
# 자동 매칭 시스템
# ============================================

class DualPageMatcher:
    """
    공동구매 ↔ 개별 농가 자동 매칭 시스템
    
    사용자 행동에 따라 적절한 페이지로 연결
    """
    
    def __init__(self):
        """매처 초기화"""
        # 페이지 저장소
        self.group_pages: Dict[str, GroupPurchasePage] = {}
        self.farm_pages: Dict[str, IndividualFarmPage] = {}
        
        # 상품 인덱스 (빠른 검색)
        self.product_index: Dict[str, List[str]] = {}  # product_name -> [page_ids]
        
        logger.info("✅ Dual Page Matcher initialized")
    
    def register_group_page(self, page: GroupPurchasePage):
        """공동구매 페이지 등록"""
        self.group_pages[page.page_id] = page
        
        # 상품 인덱스 업데이트
        for product in page.products:
            if product.product_name not in self.product_index:
                self.product_index[product.product_name] = []
            
            self.product_index[product.product_name].append({
                "page_id": page.page_id,
                "page_type": PageType.GROUP_PURCHASE.value,
                "price": product.group_price,
                "discount_rate": product.discount_rate
            })
        
        logger.info(f"✅ Group page registered: {page.page_id}")
    
    def register_farm_page(self, page: IndividualFarmPage):
        """개별 농가 페이지 등록"""
        self.farm_pages[page.page_id] = page
        
        # 상품 인덱스 업데이트
        for product in page.products:
            if product.product_name not in self.product_index:
                self.product_index[product.product_name] = []
            
            self.product_index[product.product_name].append({
                "page_id": page.page_id,
                "page_type": PageType.INDIVIDUAL_FARM.value,
                "farm_name": page.farmer.farm_name,
                "price": product.price
            })
        
        logger.info(f"✅ Farm page registered: {page.page_id}")
    
    def recommend_page(
        self,
        user_intent: str,
        product_name: str,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        사용자 의도에 맞는 페이지 추천
        
        Args:
            user_intent: "bulk_buy" (대량구매), "farm_story" (농가 스토리), "best_price" (최저가)
            product_name: 상품명
            user_profile: 사용자 프로필
            
        Returns:
            dict: 추천 페이지 정보
        """
        try:
            # 1. 해당 상품이 있는 페이지 찾기
            if product_name not in self.product_index:
                return {
                    "success": False,
                    "reason": "Product not found"
                }
            
            pages = self.product_index[product_name]
            
            # 2. 의도별 추천
            if user_intent == "bulk_buy":
                # 공동구매 우선
                group_pages = [p for p in pages if p["page_type"] == PageType.GROUP_PURCHASE.value]
                
                if group_pages:
                    # 할인율 높은 순
                    best = max(group_pages, key=lambda x: x.get("discount_rate", 0))
                    
                    return {
                        "success": True,
                        "recommended_page_type": PageType.GROUP_PURCHASE.value,
                        "page_id": best["page_id"],
                        "reason": f"공동구매로 {best['discount_rate']*100:.0f}% 할인",
                        "alternative_pages": [p["page_id"] for p in pages if p != best]
                    }
            
            elif user_intent == "farm_story":
                # 개별 농가 우선
                farm_pages = [p for p in pages if p["page_type"] == PageType.INDIVIDUAL_FARM.value]
                
                if farm_pages:
                    # 첫 번째 농가 추천 (향후 평점 기반 추천)
                    best = farm_pages[0]
                    
                    return {
                        "success": True,
                        "recommended_page_type": PageType.INDIVIDUAL_FARM.value,
                        "page_id": best["page_id"],
                        "farm_name": best["farm_name"],
                        "reason": f"{best['farm_name']}의 정성스런 농산물",
                        "alternative_pages": [p["page_id"] for p in pages if p != best]
                    }
            
            elif user_intent == "best_price":
                # 최저가 찾기
                best = min(pages, key=lambda x: x["price"])
                
                return {
                    "success": True,
                    "recommended_page_type": best["page_type"],
                    "page_id": best["page_id"],
                    "price": best["price"],
                    "reason": f"최저가 ₩{best['price']:,.0f}",
                    "alternative_pages": [p["page_id"] for p in pages if p != best]
                }
            
            # 3. 기본 추천 (의도 불명확)
            else:
                # 공동구매 우선 추천
                group_pages = [p for p in pages if p["page_type"] == PageType.GROUP_PURCHASE.value]
                
                if group_pages:
                    return {
                        "success": True,
                        "recommended_page_type": PageType.GROUP_PURCHASE.value,
                        "page_id": group_pages[0]["page_id"],
                        "reason": "할인 혜택이 있는 공동구매",
                        "alternative_pages": [p["page_id"] for p in pages]
                    }
                else:
                    return {
                        "success": True,
                        "recommended_page_type": PageType.INDIVIDUAL_FARM.value,
                        "page_id": pages[0]["page_id"],
                        "reason": "신선한 농가 직송",
                        "alternative_pages": [p["page_id"] for p in pages]
                    }
            
        except Exception as e:
            logger.error(f"❌ Recommendation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cross_link_pages(self, product_name: str) -> Dict[str, Any]:
        """
        페이지 간 크로스 링크
        
        공동구매 페이지 ↔ 개별 농가 페이지 상호 연결
        
        Args:
            product_name: 상품명
            
        Returns:
            dict: 크로스 링크 정보
        """
        if product_name not in self.product_index:
            return {"links": []}
        
        pages = self.product_index[product_name]
        
        group_pages = [p for p in pages if p["page_type"] == PageType.GROUP_PURCHASE.value]
        farm_pages = [p for p in pages if p["page_type"] == PageType.INDIVIDUAL_FARM.value]
        
        links = []
        
        # 공동구매 → 개별 농가
        for gp in group_pages:
            links.append({
                "from_page_id": gp["page_id"],
                "from_type": PageType.GROUP_PURCHASE.value,
                "to_pages": [fp["page_id"] for fp in farm_pages],
                "to_type": PageType.INDIVIDUAL_FARM.value,
                "link_text": "이 상품을 재배한 농가를 만나보세요"
            })
        
        # 개별 농가 → 공동구매
        for fp in farm_pages:
            links.append({
                "from_page_id": fp["page_id"],
                "from_type": PageType.INDIVIDUAL_FARM.value,
                "to_pages": [gp["page_id"] for gp in group_pages],
                "to_type": PageType.GROUP_PURCHASE.value,
                "link_text": "공동구매로 더 저렴하게 구매하세요"
            })
        
        return {
            "product_name": product_name,
            "links": links
        }


# ============================================
# 사용 예시
# ============================================

def example_usage():
    """Dual Page System 사용 예시"""
    
    # 1. 매처 생성
    matcher = DualPageMatcher()
    
    # 2. 공동구매 페이지 생성
    group_page = GroupPurchasePage(
        page_id="GP_001",
        title="인제군 겨울 사과 공동구매",
        description="인제군 5개 농가의 사과를 함께 구매하면 20% 할인!",
        products=[
            GroupPurchaseProduct(
                product_id="GP_APPLE_001",
                product_name="사과",
                category="과일",
                participating_farms=[
                    {"farm_id": "F001", "farm_name": "푸른골농원"},
                    {"farm_id": "F002", "farm_name": "청정농장"}
                ],
                total_quantity=1000,
                min_order_quantity=10,
                original_price=5000,
                group_price=4000,
                discount_rate=0.20,
                delivery_fee=3000,
                free_shipping_threshold=50000,
                status=ProductStatus.AVAILABLE,
                start_date="2024-02-12",
                end_date="2024-02-29"
            )
        ]
    )
    
    matcher.register_group_page(group_page)
    
    # 3. 개별 농가 페이지 생성
    farm_page = IndividualFarmPage(
        page_id="FP_001",
        farm_id="F001",
        farmer=FarmerProfile(
            farmer_id="F001",
            name="김철수",
            farm_name="푸른골농원",
            location="인제군 기린면",
            introduction="30년 경력의 사과 농부입니다",
            philosophy="자연과 함께하는 농사",
            experience_years=30,
            phone="010-1234-5678"
        ),
        products=[
            IndividualFarmProduct(
                product_id="FP_APPLE_001",
                product_name="사과",
                category="과일",
                farm_story="30년간 정성껏 키운 사과입니다",
                farming_method="저농약 재배",
                certification=["GAP 인증"],
                price=4500,
                unit="kg",
                available_quantity=500,
                status=ProductStatus.AVAILABLE,
                harvest_date="2024-02-10"
            )
        ]
    )
    
    matcher.register_farm_page(farm_page)
    
    # 4. 추천 테스트
    print("\n[추천 1: 대량 구매 의도]")
    rec1 = matcher.recommend_page("bulk_buy", "사과")
    print(json.dumps(rec1, indent=2, ensure_ascii=False))
    
    print("\n[추천 2: 농가 스토리 의도]")
    rec2 = matcher.recommend_page("farm_story", "사과")
    print(json.dumps(rec2, indent=2, ensure_ascii=False))
    
    print("\n[추천 3: 최저가 의도]")
    rec3 = matcher.recommend_page("best_price", "사과")
    print(json.dumps(rec3, indent=2, ensure_ascii=False))
    
    # 5. 크로스 링크
    print("\n[크로스 링크]")
    links = matcher.cross_link_pages("사과")
    print(json.dumps(links, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    example_usage()

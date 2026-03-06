"""
Mulberry Product Suggestion System
CTO Koda

제품 제안 시스템 (공개/비공개)
사용자가 공동구매 제품을 제안할 수 있음
"""

from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
import json


class SuggestionStatus(str, Enum):
    """제안 상태"""
    PENDING = "pending"          # 검토 대기
    UNDER_REVIEW = "under_review"  # 검토 중
    APPROVED = "approved"        # 승인됨
    REJECTED = "rejected"        # 거절됨
    IMPLEMENTED = "implemented"  # 실행됨 (공동구매 시작)


class SuggestionVisibility(str, Enum):
    """공개 설정"""
    PUBLIC = "public"      # 공개 (모두 볼 수 있음)
    PRIVATE = "private"    # 비공개 (운영자만)


class ProductSuggestion:
    """제품 제안"""
    
    def __init__(
        self,
        suggestion_id: str,
        user_id: str,
        product_name: str,
        description: str,
        category: str
    ):
        self.suggestion_id = suggestion_id
        self.user_id = user_id
        self.product_name = product_name
        self.description = description
        self.category = category
        
        # 상세 정보
        self.producer_location: Optional[str] = None
        self.estimated_price: Optional[float] = None
        self.min_quantity: int = 10
        
        # 공개 설정
        self.visibility = SuggestionVisibility.PUBLIC
        
        # 상태
        self.status = SuggestionStatus.PENDING
        
        # 투표
        self.upvotes: int = 0
        self.downvotes: int = 0
        self.voters: List[str] = []  # user_id 목록
        
        # 검토
        self.review_notes: Optional[str] = None
        self.reviewed_by: Optional[str] = None
        self.reviewed_at: Optional[datetime] = None
        
        # 실행
        self.campaign_id: Optional[str] = None  # 실행된 캠페인
        
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "suggestion_id": self.suggestion_id,
            "user_id": self.user_id,
            "product_name": self.product_name,
            "description": self.description,
            "category": self.category,
            "producer_location": self.producer_location,
            "estimated_price": self.estimated_price,
            "min_quantity": self.min_quantity,
            "visibility": self.visibility.value,
            "status": self.status.value,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "vote_count": len(self.voters),
            "review_notes": self.review_notes,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "campaign_id": self.campaign_id,
            "created_at": self.created_at.isoformat()
        }


class ProductSuggestionManager:
    """
    제품 제안 관리자
    
    사용자 제안 접수, 투표, 검토, 승인, 실행
    """
    
    def __init__(self, db_connection):
        """
        Args:
            db_connection: 데이터베이스 연결
        """
        self.db = db_connection
    
    def create_suggestion(
        self,
        user_id: str,
        product_name: str,
        description: str,
        category: str,
        visibility: SuggestionVisibility = SuggestionVisibility.PUBLIC,
        **kwargs
    ) -> ProductSuggestion:
        """
        제품 제안 생성
        
        Args:
            user_id: 제안자 ID
            product_name: 제품명
            description: 설명
            category: 카테고리
            visibility: 공개 설정
        
        Returns:
            생성된 제안
        """
        suggestion_id = f"SUGG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        suggestion = ProductSuggestion(
            suggestion_id=suggestion_id,
            user_id=user_id,
            product_name=product_name,
            description=description,
            category=category
        )
        
        suggestion.visibility = visibility
        
        # 추가 옵션
        for key, value in kwargs.items():
            if hasattr(suggestion, key):
                setattr(suggestion, key, value)
        
        # 저장
        self._save_suggestion(suggestion)
        
        print(f"✅ 제품 제안 생성: {product_name}")
        print(f"   제안자: {user_id}")
        print(f"   공개 설정: {visibility.value}")
        
        return suggestion
    
    def vote(
        self,
        suggestion_id: str,
        user_id: str,
        vote_type: str  # 'up' or 'down'
    ) -> Dict:
        """
        제안에 투표
        
        Args:
            suggestion_id: 제안 ID
            user_id: 투표자 ID
            vote_type: 'up' (찬성) or 'down' (반대)
        
        Returns:
            투표 결과
        """
        suggestion = self._load_suggestion(suggestion_id)
        
        # 중복 투표 방지
        if user_id in suggestion.voters:
            return {
                "success": False,
                "message": "이미 투표하셨습니다."
            }
        
        # 투표 처리
        if vote_type == 'up':
            suggestion.upvotes += 1
        elif vote_type == 'down':
            suggestion.downvotes += 1
        else:
            return {
                "success": False,
                "message": "잘못된 투표 타입입니다."
            }
        
        suggestion.voters.append(user_id)
        
        # 저장
        self._update_suggestion(suggestion)
        
        print(f"✅ 투표 완료: {suggestion_id}")
        print(f"   찬성: {suggestion.upvotes}, 반대: {suggestion.downvotes}")
        
        return {
            "success": True,
            "upvotes": suggestion.upvotes,
            "downvotes": suggestion.downvotes
        }
    
    def review_suggestion(
        self,
        suggestion_id: str,
        reviewer_id: str,
        approved: bool,
        review_notes: Optional[str] = None
    ) -> ProductSuggestion:
        """
        제안 검토
        
        Args:
            suggestion_id: 제안 ID
            reviewer_id: 검토자 ID (관리자)
            approved: 승인 여부
            review_notes: 검토 메모
        
        Returns:
            업데이트된 제안
        """
        suggestion = self._load_suggestion(suggestion_id)
        
        suggestion.status = SuggestionStatus.APPROVED if approved else SuggestionStatus.REJECTED
        suggestion.review_notes = review_notes
        suggestion.reviewed_by = reviewer_id
        suggestion.reviewed_at = datetime.now()
        
        # 저장
        self._update_suggestion(suggestion)
        
        result = "승인" if approved else "거절"
        print(f"✅ 제안 검토: {suggestion_id}")
        print(f"   결과: {result}")
        print(f"   검토자: {reviewer_id}")
        
        return suggestion
    
    def implement_suggestion(
        self,
        suggestion_id: str,
        campaign_id: str
    ) -> ProductSuggestion:
        """
        제안 실행 (공동구매 캠페인 시작)
        
        Args:
            suggestion_id: 제안 ID
            campaign_id: 시작된 캠페인 ID
        
        Returns:
            업데이트된 제안
        """
        suggestion = self._load_suggestion(suggestion_id)
        
        suggestion.status = SuggestionStatus.IMPLEMENTED
        suggestion.campaign_id = campaign_id
        
        # 저장
        self._update_suggestion(suggestion)
        
        print(f"✅ 제안 실행: {suggestion_id}")
        print(f"   캠페인: {campaign_id}")
        
        return suggestion
    
    def get_public_suggestions(self, limit: int = 50) -> List[Dict]:
        """
        공개 제안 목록 (투표순)
        
        Args:
            limit: 개수
        
        Returns:
            제안 목록
        """
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT *,
                   (upvotes - downvotes) as score
            FROM product_suggestions
            WHERE visibility = 'public'
            AND status IN ('pending', 'under_review', 'approved')
            ORDER BY score DESC, created_at DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_top_suggestions(self, limit: int = 10) -> List[Dict]:
        """
        인기 제안 (투표 많은 순)
        
        Args:
            limit: 개수
        
        Returns:
            제안 목록
        """
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT *,
                   (upvotes - downvotes) as score
            FROM product_suggestions
            WHERE visibility = 'public'
            AND status = 'pending'
            ORDER BY upvotes DESC, created_at DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_pending_for_review(self) -> List[Dict]:
        """
        검토 대기 제안 (관리자용)
        
        Returns:
            제안 목록
        """
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT *,
                   (upvotes - downvotes) as score
            FROM product_suggestions
            WHERE status = 'pending'
            ORDER BY score DESC, created_at ASC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ============================================
    # Private Methods
    # ============================================
    
    def _save_suggestion(self, suggestion: ProductSuggestion):
        """제안 저장"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO product_suggestions (
                suggestion_id, user_id, product_name, description, category,
                producer_location, estimated_price, min_quantity,
                visibility, status, upvotes, downvotes, voters,
                review_notes, reviewed_by, reviewed_at,
                campaign_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            suggestion.suggestion_id,
            suggestion.user_id,
            suggestion.product_name,
            suggestion.description,
            suggestion.category,
            suggestion.producer_location,
            suggestion.estimated_price,
            suggestion.min_quantity,
            suggestion.visibility.value,
            suggestion.status.value,
            suggestion.upvotes,
            suggestion.downvotes,
            json.dumps(suggestion.voters),
            suggestion.review_notes,
            suggestion.reviewed_by,
            suggestion.reviewed_at,
            suggestion.campaign_id,
            suggestion.created_at
        ))
        self.db.commit()
    
    def _update_suggestion(self, suggestion: ProductSuggestion):
        """제안 업데이트"""
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE product_suggestions
            SET status = ?,
                upvotes = ?,
                downvotes = ?,
                voters = ?,
                review_notes = ?,
                reviewed_by = ?,
                reviewed_at = ?,
                campaign_id = ?
            WHERE suggestion_id = ?
        """, (
            suggestion.status.value,
            suggestion.upvotes,
            suggestion.downvotes,
            json.dumps(suggestion.voters),
            suggestion.review_notes,
            suggestion.reviewed_by,
            suggestion.reviewed_at,
            suggestion.campaign_id,
            suggestion.suggestion_id
        ))
        self.db.commit()
    
    def _load_suggestion(self, suggestion_id: str) -> ProductSuggestion:
        """제안 조회"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT * FROM product_suggestions
            WHERE suggestion_id = ?
        """, (suggestion_id,))
        
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Suggestion {suggestion_id} not found")
        
        # TODO: row를 ProductSuggestion로 변환
        suggestion = ProductSuggestion(
            suggestion_id=row['suggestion_id'],
            user_id=row['user_id'],
            product_name=row['product_name'],
            description=row['description'],
            category=row['category']
        )
        
        suggestion.status = SuggestionStatus(row['status'])
        suggestion.upvotes = row['upvotes']
        suggestion.downvotes = row['downvotes']
        suggestion.voters = json.loads(row['voters']) if row['voters'] else []
        
        return suggestion


# ============================================
# 데이터베이스 스키마
# ============================================

def init_suggestion_table(db_connection):
    """제품 제안 테이블 초기화"""
    cursor = db_connection.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_suggestions (
            suggestion_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            
            product_name TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            
            producer_location TEXT,
            estimated_price REAL,
            min_quantity INTEGER DEFAULT 10,
            
            visibility TEXT NOT NULL,
            status TEXT NOT NULL,
            
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0,
            voters TEXT,  -- JSON array
            
            review_notes TEXT,
            reviewed_by TEXT,
            reviewed_at TIMESTAMP,
            
            campaign_id TEXT,
            
            created_at TIMESTAMP NOT NULL,
            
            FOREIGN KEY (campaign_id) REFERENCES group_purchase_campaigns(campaign_id)
        )
    """)
    
    # 인덱스
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_suggestions_status 
        ON product_suggestions(status, created_at)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_suggestions_visibility 
        ON product_suggestions(visibility, status)
    """)
    
    db_connection.commit()
    
    print("✅ 제품 제안 테이블 초기화 완료")


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # manager = ProductSuggestionManager(db_connection)
    
    # 제안 생성
    # suggestion = manager.create_suggestion(
    #     user_id="user@mastodon.social",
    #     product_name="인제 산나물 세트",
    #     description="인제군에서 직접 채취한 신선한 산나물",
    #     category="agricultural",
    #     visibility=SuggestionVisibility.PUBLIC,
    #     producer_location="강원도 인제군",
    #     estimated_price=25000
    # )
    
    # 투표
    # manager.vote(suggestion.suggestion_id, "user2@mastodon.social", "up")
    
    # 검토 (관리자)
    # manager.review_suggestion(
    #     suggestion.suggestion_id,
    #     reviewer_id="admin",
    #     approved=True,
    #     review_notes="좋은 제안입니다!"
    # )
    
    # 실행 (공동구매 시작)
    # manager.implement_suggestion(suggestion.suggestion_id, "CAMP-...")
    
    print("✅ Product Suggestion Manager 로드 완료")

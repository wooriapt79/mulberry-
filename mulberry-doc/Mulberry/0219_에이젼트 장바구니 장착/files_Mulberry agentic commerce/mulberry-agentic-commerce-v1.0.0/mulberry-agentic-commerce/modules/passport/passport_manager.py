"""
Mulberry Agentic Commerce - 패스포트 발급 모듈
CTO Koda

에이전트 인증 및 신용 평가 시스템
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid
import hashlib
import json
from enum import Enum


class TrustLevel(str, Enum):
    """신용 등급"""
    BRONZE = "bronze"      # 신규 (0-599)
    SILVER = "silver"      # 일반 (600-749)
    GOLD = "gold"          # 우수 (750-899)
    PLATINUM = "platinum"  # 최우수 (900-1000)


class PassportStatus(str, Enum):
    """패스포트 상태"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"


class AgentType(str, Enum):
    """에이전트 유형"""
    SALES = "sales"              # 판매 에이전트
    DELIVERY = "delivery"        # 배송 에이전트
    SERVICE = "service"          # 서비스 에이전트
    SUPPORT = "support"          # 지원 에이전트


class Location(BaseModel):
    """위치 정보"""
    latitude: float
    longitude: float
    address: str
    city: Optional[str] = None
    country: str = "KR"


class Operator(BaseModel):
    """운영자 정보"""
    name: str
    phone: str
    email: str
    id_verified: bool = False


class Passport(BaseModel):
    """패스포트"""
    passport_id: str = Field(default_factory=lambda: f"PP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}")
    agent_id: str
    device_id: str
    device_type: str = "raspberry_pi_5"
    agent_type: AgentType
    
    # 발급 정보
    issued_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field(default_factory=lambda: datetime.now() + timedelta(days=365))
    status: PassportStatus = PassportStatus.ACTIVE
    
    # 신용 정보
    credit_score: int = Field(default=750, ge=0, le=1000)
    trust_level: TrustLevel = TrustLevel.SILVER
    
    # 운영자 및 위치
    operator: Operator
    location: Location
    
    # 권한
    permissions: List[str] = Field(default_factory=list)
    
    # 활동 통계
    total_transactions: int = 0
    total_sales: float = 0.0
    successful_deliveries: int = 0
    customer_ratings: float = 0.0
    
    # 보안
    signature: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PassportManager:
    """
    패스포트 관리자
    """
    
    def __init__(self, db_connection, secret_key: str):
        """
        Args:
            db_connection: 데이터베이스 연결
            secret_key: 서명용 비밀키
        """
        self.db = db_connection
        self.secret_key = secret_key
    
    def issue_passport(
        self,
        agent_id: str,
        device_id: str,
        agent_type: AgentType,
        operator: Operator,
        location: Location
    ) -> Passport:
        """
        패스포트 발급
        
        Args:
            agent_id: 에이전트 ID
            device_id: 디바이스 ID (라즈베리 파이 시리얼)
            agent_type: 에이전트 유형
            operator: 운영자 정보
            location: 위치 정보
        
        Returns:
            발급된 패스포트
        """
        # 기본 신용 점수 결정 (신규는 750)
        credit_score = 750
        trust_level = self._calculate_trust_level(credit_score)
        
        # 권한 부여
        permissions = self._get_default_permissions(agent_type)
        
        # 패스포트 생성
        passport = Passport(
            agent_id=agent_id,
            device_id=device_id,
            agent_type=agent_type,
            operator=operator,
            location=location,
            credit_score=credit_score,
            trust_level=trust_level,
            permissions=permissions
        )
        
        # 서명 생성
        passport.signature = self._sign_passport(passport)
        
        # 데이터베이스 저장
        self._save_passport(passport)
        
        return passport
    
    def verify_passport(self, passport_id: str) -> Optional[Passport]:
        """
        패스포트 검증
        
        Args:
            passport_id: 패스포트 ID
        
        Returns:
            유효한 패스포트 또는 None
        """
        passport = self._load_passport(passport_id)
        
        if not passport:
            return None
        
        # 만료 확인
        if passport.expires_at < datetime.now():
            passport.status = PassportStatus.EXPIRED
            self._update_passport(passport)
            return None
        
        # 상태 확인
        if passport.status != PassportStatus.ACTIVE:
            return None
        
        # 서명 검증
        if not self._verify_signature(passport):
            return None
        
        return passport
    
    def update_credit_score(
        self,
        passport_id: str,
        transaction_success: bool,
        amount: float,
        customer_rating: Optional[float] = None
    ) -> Passport:
        """
        신용 점수 업데이트
        
        Args:
            passport_id: 패스포트 ID
            transaction_success: 거래 성공 여부
            amount: 거래 금액
            customer_rating: 고객 평점 (1-5)
        
        Returns:
            업데이트된 패스포트
        """
        passport = self._load_passport(passport_id)
        
        if not passport:
            raise ValueError(f"Passport {passport_id} not found")
        
        # 통계 업데이트
        passport.total_transactions += 1
        
        if transaction_success:
            passport.total_sales += amount
            passport.successful_deliveries += 1
            
            # 신용 점수 증가 (성공)
            score_increase = min(5, amount / 100000)  # 10만원당 +1점 (최대 +5)
            passport.credit_score = min(1000, passport.credit_score + score_increase)
        else:
            # 신용 점수 감소 (실패)
            passport.credit_score = max(0, passport.credit_score - 10)
        
        # 고객 평점 반영
        if customer_rating is not None:
            if passport.customer_ratings == 0:
                passport.customer_ratings = customer_rating
            else:
                # 이동 평균
                passport.customer_ratings = (
                    passport.customer_ratings * 0.9 + customer_rating * 0.1
                )
            
            # 평점에 따른 점수 조정
            if customer_rating >= 4.5:
                passport.credit_score = min(1000, passport.credit_score + 3)
            elif customer_rating < 3.0:
                passport.credit_score = max(0, passport.credit_score - 5)
        
        # 신용 등급 재계산
        passport.trust_level = self._calculate_trust_level(passport.credit_score)
        
        # 서명 재생성
        passport.signature = self._sign_passport(passport)
        
        # 저장
        self._update_passport(passport)
        
        return passport
    
    def suspend_passport(self, passport_id: str, reason: str) -> bool:
        """
        패스포트 정지
        
        Args:
            passport_id: 패스포트 ID
            reason: 정지 사유
        
        Returns:
            성공 여부
        """
        passport = self._load_passport(passport_id)
        
        if not passport:
            return False
        
        passport.status = PassportStatus.SUSPENDED
        self._update_passport(passport)
        
        # 로그 기록
        self._log_action(passport_id, "suspended", reason)
        
        return True
    
    def revoke_passport(self, passport_id: str, reason: str) -> bool:
        """
        패스포트 취소 (영구)
        
        Args:
            passport_id: 패스포트 ID
            reason: 취소 사유
        
        Returns:
            성공 여부
        """
        passport = self._load_passport(passport_id)
        
        if not passport:
            return False
        
        passport.status = PassportStatus.REVOKED
        self._update_passport(passport)
        
        # 로그 기록
        self._log_action(passport_id, "revoked", reason)
        
        return True
    
    def renew_passport(self, passport_id: str) -> Passport:
        """
        패스포트 갱신
        
        Args:
            passport_id: 패스포트 ID
        
        Returns:
            갱신된 패스포트
        """
        passport = self._load_passport(passport_id)
        
        if not passport:
            raise ValueError(f"Passport {passport_id} not found")
        
        # 만료일 연장
        passport.expires_at = datetime.now() + timedelta(days=365)
        passport.status = PassportStatus.ACTIVE
        
        # 서명 재생성
        passport.signature = self._sign_passport(passport)
        
        # 저장
        self._update_passport(passport)
        
        return passport
    
    # ============================================
    # Private Methods
    # ============================================
    
    def _calculate_trust_level(self, credit_score: int) -> TrustLevel:
        """신용 점수로부터 등급 계산"""
        if credit_score >= 900:
            return TrustLevel.PLATINUM
        elif credit_score >= 750:
            return TrustLevel.GOLD
        elif credit_score >= 600:
            return TrustLevel.SILVER
        else:
            return TrustLevel.BRONZE
    
    def _get_default_permissions(self, agent_type: AgentType) -> List[str]:
        """에이전트 유형별 기본 권한"""
        base_permissions = [
            "product.read",
            "profile.read"
        ]
        
        if agent_type == AgentType.SALES:
            return base_permissions + [
                "product.sell",
                "order.create",
                "payment.process",
                "cart.manage"
            ]
        elif agent_type == AgentType.DELIVERY:
            return base_permissions + [
                "order.read",
                "order.update_status",
                "location.track"
            ]
        elif agent_type == AgentType.SERVICE:
            return base_permissions + [
                "customer.support",
                "ticket.create"
            ]
        else:
            return base_permissions
    
    def _sign_passport(self, passport: Passport) -> str:
        """패스포트 서명 생성"""
        # 서명할 데이터 (signature 필드 제외)
        data = passport.dict(exclude={'signature'})
        message = json.dumps(data, sort_keys=True, default=str)
        
        # HMAC-SHA256
        signature = hashlib.sha256(
            (message + self.secret_key).encode()
        ).hexdigest()
        
        return signature
    
    def _verify_signature(self, passport: Passport) -> bool:
        """패스포트 서명 검증"""
        expected_signature = self._sign_passport(passport)
        return passport.signature == expected_signature
    
    def _save_passport(self, passport: Passport):
        """패스포트 저장 (데이터베이스)"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO passports (
                passport_id, agent_id, device_id, agent_type,
                issued_at, expires_at, status,
                credit_score, trust_level,
                operator, location, permissions,
                signature
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            passport.passport_id,
            passport.agent_id,
            passport.device_id,
            passport.agent_type.value,
            passport.issued_at,
            passport.expires_at,
            passport.status.value,
            passport.credit_score,
            passport.trust_level.value,
            passport.operator.json(),
            passport.location.json(),
            json.dumps(passport.permissions),
            passport.signature
        ))
        self.db.commit()
    
    def _load_passport(self, passport_id: str) -> Optional[Passport]:
        """패스포트 조회"""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM passports WHERE passport_id = %s",
            (passport_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Passport 객체로 변환 (실제 구현 시 컬럼 매핑 필요)
        # 여기서는 예시만 제공
        return Passport(**dict(row))
    
    def _update_passport(self, passport: Passport):
        """패스포트 업데이트"""
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE passports SET
                status = %s,
                credit_score = %s,
                trust_level = %s,
                total_transactions = %s,
                total_sales = %s,
                successful_deliveries = %s,
                customer_ratings = %s,
                signature = %s
            WHERE passport_id = %s
        """, (
            passport.status.value,
            passport.credit_score,
            passport.trust_level.value,
            passport.total_transactions,
            passport.total_sales,
            passport.successful_deliveries,
            passport.customer_ratings,
            passport.signature,
            passport.passport_id
        ))
        self.db.commit()
    
    def _log_action(self, passport_id: str, action: str, reason: str):
        """액션 로그 기록"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO passport_logs (
                passport_id, action, reason, created_at
            ) VALUES (%s, %s, %s, %s)
        """, (passport_id, action, reason, datetime.now()))
        self.db.commit()


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # 예시 데이터
    operator = Operator(
        name="홍길동",
        phone="010-1234-5678",
        email="hong@example.com",
        id_verified=True
    )
    
    location = Location(
        latitude=37.5665,
        longitude=126.9780,
        address="서울시 중구 세종대로 110",
        city="서울",
        country="KR"
    )
    
    # 패스포트 매니저 초기화 (실제로는 DB 연결 필요)
    # manager = PassportManager(db_connection, secret_key="your_secret")
    
    # 패스포트 발급
    # passport = manager.issue_passport(
    #     agent_id="agent-001",
    #     device_id="raspberry-pi-serial-123",
    #     agent_type=AgentType.SALES,
    #     operator=operator,
    #     location=location
    # )
    
    print("✅ 패스포트 모듈 로드 완료")
    print(f"   AgentType: {list(AgentType)}")
    print(f"   TrustLevel: {list(TrustLevel)}")

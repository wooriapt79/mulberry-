"""
Mulberry AP2 Mandate Integration
CTO Koda

AP2 위임장 시스템을 에이전트 의사결정에 통합
"""

from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
import json
import hashlib


class MandateType(str, Enum):
    """위임장 종류"""
    INTENT = "intent"          # 의도 위임장
    CART = "cart"              # 장바구니 위임장
    PAYMENT = "payment"        # 결제 위임장


class MandateStatus(str, Enum):
    """위임장 상태"""
    CREATED = "created"        # 생성됨
    ACTIVE = "active"          # 활성
    EXECUTED = "executed"      # 실행됨
    EXPIRED = "expired"        # 만료됨
    REVOKED = "revoked"        # 취소됨


class IntentMandate:
    """
    의도 위임장 (Intent Mandate)
    
    사용자가 에이전트에게 특정 작업을 수행할 권한 부여
    """
    
    def __init__(
        self,
        mandate_id: str,
        user_id: str,
        agent_id: str,
        intent: str,
        constraints: Dict
    ):
        self.mandate_id = mandate_id
        self.user_id = user_id
        self.agent_id = agent_id
        self.intent = intent  # "식료품 구매", "예약", "주문" 등
        self.constraints = constraints  # 예산, 시간, 조건 등
        
        self.created_at = datetime.now()
        self.expires_at: Optional[datetime] = None
        self.status = MandateStatus.CREATED
        
        # 서명 (암호화)
        self.signature = self._generate_signature()
    
    def _generate_signature(self) -> str:
        """위임장 서명 생성"""
        data = f"{self.mandate_id}{self.user_id}{self.agent_id}{self.intent}{json.dumps(self.constraints)}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_signature(self) -> bool:
        """서명 검증"""
        expected = self._generate_signature()
        return self.signature == expected
    
    def is_valid(self) -> bool:
        """위임장 유효성 확인"""
        if self.status not in [MandateStatus.ACTIVE, MandateStatus.CREATED]:
            return False
        
        if self.expires_at and datetime.now() > self.expires_at:
            self.status = MandateStatus.EXPIRED
            return False
        
        return self.verify_signature()
    
    def to_dict(self) -> Dict:
        return {
            "mandate_id": self.mandate_id,
            "mandate_type": MandateType.INTENT.value,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "intent": self.intent,
            "constraints": self.constraints,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status.value,
            "signature": self.signature
        }


class CartMandate:
    """
    장바구니 위임장 (Cart Mandate)
    
    사용자가 특정 장바구니 내용을 승인
    """
    
    def __init__(
        self,
        mandate_id: str,
        user_id: str,
        agent_id: str,
        cart_items: List[Dict],
        total_amount: float,
        intent_mandate_id: str
    ):
        self.mandate_id = mandate_id
        self.user_id = user_id
        self.agent_id = agent_id
        self.cart_items = cart_items
        self.total_amount = total_amount
        self.intent_mandate_id = intent_mandate_id  # 연결된 Intent Mandate
        
        self.created_at = datetime.now()
        self.status = MandateStatus.CREATED
        
        # 서명
        self.signature = self._generate_signature()
    
    def _generate_signature(self) -> str:
        """위임장 서명 생성"""
        data = f"{self.mandate_id}{self.user_id}{self.agent_id}{json.dumps(self.cart_items)}{self.total_amount}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_signature(self) -> bool:
        """서명 검증"""
        expected = self._generate_signature()
        return self.signature == expected
    
    def is_valid(self) -> bool:
        """위임장 유효성 확인"""
        if self.status != MandateStatus.ACTIVE:
            return False
        
        return self.verify_signature()
    
    def to_dict(self) -> Dict:
        return {
            "mandate_id": self.mandate_id,
            "mandate_type": MandateType.CART.value,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "cart_items": self.cart_items,
            "total_amount": self.total_amount,
            "intent_mandate_id": self.intent_mandate_id,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "signature": self.signature
        }


class PaymentMandate:
    """
    결제 위임장 (Payment Mandate)
    
    결제 시스템에 전달되는 최종 승인
    """
    
    def __init__(
        self,
        mandate_id: str,
        user_id: str,
        agent_id: str,
        cart_mandate_id: str,
        payment_method: str,
        amount: float
    ):
        self.mandate_id = mandate_id
        self.user_id = user_id
        self.agent_id = agent_id
        self.cart_mandate_id = cart_mandate_id
        self.payment_method = payment_method
        self.amount = amount
        
        self.created_at = datetime.now()
        self.status = MandateStatus.CREATED
        
        # 서명
        self.signature = self._generate_signature()
    
    def _generate_signature(self) -> str:
        """위임장 서명 생성"""
        data = f"{self.mandate_id}{self.user_id}{self.agent_id}{self.cart_mandate_id}{self.payment_method}{self.amount}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_signature(self) -> bool:
        """서명 검증"""
        expected = self._generate_signature()
        return self.signature == expected
    
    def is_valid(self) -> bool:
        """위임장 유효성 확인"""
        if self.status != MandateStatus.ACTIVE:
            return False
        
        return self.verify_signature()
    
    def to_dict(self) -> Dict:
        return {
            "mandate_id": self.mandate_id,
            "mandate_type": MandateType.PAYMENT.value,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "cart_mandate_id": self.cart_mandate_id,
            "payment_method": self.payment_method,
            "amount": self.amount,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "signature": self.signature
        }


class AP2MandateManager:
    """
    AP2 위임장 관리자
    
    에이전트가 의사결정할 때 위임장 기반으로 권한 확인
    """
    
    def __init__(self, db_connection):
        """
        Args:
            db_connection: 데이터베이스 연결
        """
        self.db = db_connection
    
    def create_intent_mandate(
        self,
        user_id: str,
        agent_id: str,
        intent: str,
        constraints: Dict,
        expires_at: Optional[datetime] = None
    ) -> IntentMandate:
        """
        Intent Mandate 생성
        
        Args:
            user_id: 사용자 ID
            agent_id: 에이전트 ID
            intent: 의도 ("식료품 구매", "예약" 등)
            constraints: 제약 조건 (예산, 시간 등)
            expires_at: 만료 시간
        
        Returns:
            생성된 위임장
        """
        mandate_id = f"INTENT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        mandate = IntentMandate(
            mandate_id=mandate_id,
            user_id=user_id,
            agent_id=agent_id,
            intent=intent,
            constraints=constraints
        )
        
        if expires_at:
            mandate.expires_at = expires_at
        
        mandate.status = MandateStatus.ACTIVE
        
        # 저장
        self._save_mandate(mandate)
        
        print(f"✅ Intent Mandate 생성: {mandate_id}")
        print(f"   의도: {intent}")
        print(f"   제약: {constraints}")
        
        return mandate
    
    def create_cart_mandate(
        self,
        user_id: str,
        agent_id: str,
        cart_items: List[Dict],
        total_amount: float,
        intent_mandate_id: str
    ) -> CartMandate:
        """
        Cart Mandate 생성
        
        Args:
            user_id: 사용자 ID
            agent_id: 에이전트 ID
            cart_items: 장바구니 항목
            total_amount: 총액
            intent_mandate_id: 연결된 Intent Mandate
        
        Returns:
            생성된 위임장
        """
        # Intent Mandate 유효성 확인
        intent_mandate = self._load_mandate(intent_mandate_id, MandateType.INTENT)
        if not intent_mandate.is_valid():
            raise ValueError(f"Intent Mandate {intent_mandate_id}가 유효하지 않습니다.")
        
        # 제약 조건 확인 (예산 등)
        if 'max_budget' in intent_mandate.constraints:
            if total_amount > intent_mandate.constraints['max_budget']:
                raise ValueError(f"예산 초과: {total_amount} > {intent_mandate.constraints['max_budget']}")
        
        mandate_id = f"CART-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        mandate = CartMandate(
            mandate_id=mandate_id,
            user_id=user_id,
            agent_id=agent_id,
            cart_items=cart_items,
            total_amount=total_amount,
            intent_mandate_id=intent_mandate_id
        )
        
        mandate.status = MandateStatus.ACTIVE
        
        # 저장
        self._save_mandate(mandate)
        
        print(f"✅ Cart Mandate 생성: {mandate_id}")
        print(f"   항목 수: {len(cart_items)}")
        print(f"   총액: {total_amount}원")
        
        return mandate
    
    def create_payment_mandate(
        self,
        user_id: str,
        agent_id: str,
        cart_mandate_id: str,
        payment_method: str,
        amount: float
    ) -> PaymentMandate:
        """
        Payment Mandate 생성
        
        Args:
            user_id: 사용자 ID
            agent_id: 에이전트 ID
            cart_mandate_id: 연결된 Cart Mandate
            payment_method: 결제 방법
            amount: 금액
        
        Returns:
            생성된 위임장
        """
        # Cart Mandate 유효성 확인
        cart_mandate = self._load_mandate(cart_mandate_id, MandateType.CART)
        if not cart_mandate.is_valid():
            raise ValueError(f"Cart Mandate {cart_mandate_id}가 유효하지 않습니다.")
        
        # 금액 확인
        if amount != cart_mandate.total_amount:
            raise ValueError(f"금액 불일치: {amount} != {cart_mandate.total_amount}")
        
        mandate_id = f"PAYMENT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        mandate = PaymentMandate(
            mandate_id=mandate_id,
            user_id=user_id,
            agent_id=agent_id,
            cart_mandate_id=cart_mandate_id,
            payment_method=payment_method,
            amount=amount
        )
        
        mandate.status = MandateStatus.ACTIVE
        
        # 저장
        self._save_mandate(mandate)
        
        print(f"✅ Payment Mandate 생성: {mandate_id}")
        print(f"   결제 방법: {payment_method}")
        print(f"   금액: {amount}원")
        
        return mandate
    
    def verify_agent_authority(
        self,
        agent_id: str,
        action: str,
        context: Dict
    ) -> bool:
        """
        에이전트 권한 검증
        
        Args:
            agent_id: 에이전트 ID
            action: 수행하려는 액션
            context: 컨텍스트 (금액, 항목 등)
        
        Returns:
            권한 여부
        """
        # 활성 Intent Mandate 조회
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT * FROM mandates
            WHERE agent_id = ?
            AND mandate_type = 'intent'
            AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
        """, (agent_id,))
        
        row = cursor.fetchone()
        if not row:
            print(f"❌ 활성 Intent Mandate 없음: {agent_id}")
            return False
        
        # Intent Mandate 로드 및 검증
        intent_mandate = self._row_to_intent_mandate(row)
        
        if not intent_mandate.is_valid():
            print(f"❌ Intent Mandate 유효하지 않음: {intent_mandate.mandate_id}")
            return False
        
        # 제약 조건 확인
        constraints = intent_mandate.constraints
        
        if 'max_budget' in constraints and 'amount' in context:
            if context['amount'] > constraints['max_budget']:
                print(f"❌ 예산 초과: {context['amount']} > {constraints['max_budget']}")
                return False
        
        print(f"✅ 에이전트 권한 확인: {agent_id} - {action}")
        return True
    
    def execute_mandate(self, mandate_id: str, mandate_type: MandateType):
        """위임장 실행 표시"""
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE mandates
            SET status = 'executed'
            WHERE mandate_id = ?
            AND mandate_type = ?
        """, (mandate_id, mandate_type.value))
        self.db.commit()
    
    # ============================================
    # Private Methods
    # ============================================
    
    def _save_mandate(self, mandate):
        """위임장 저장"""
        cursor = self.db.cursor()
        
        mandate_dict = mandate.to_dict()
        
        cursor.execute("""
            INSERT INTO mandates (
                mandate_id, mandate_type, user_id, agent_id,
                content, created_at, status, signature
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mandate.mandate_id,
            mandate_dict['mandate_type'],
            mandate.user_id,
            mandate.agent_id,
            json.dumps(mandate_dict),
            mandate.created_at,
            mandate.status.value,
            mandate.signature
        ))
        self.db.commit()
    
    def _load_mandate(self, mandate_id: str, mandate_type: MandateType):
        """위임장 조회"""
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT * FROM mandates
            WHERE mandate_id = ?
            AND mandate_type = ?
        """, (mandate_id, mandate_type.value))
        
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Mandate {mandate_id} not found")
        
        if mandate_type == MandateType.INTENT:
            return self._row_to_intent_mandate(row)
        elif mandate_type == MandateType.CART:
            return self._row_to_cart_mandate(row)
        elif mandate_type == MandateType.PAYMENT:
            return self._row_to_payment_mandate(row)
    
    def _row_to_intent_mandate(self, row) -> IntentMandate:
        """DB 행을 IntentMandate로 변환"""
        content = json.loads(row['content'])
        mandate = IntentMandate(
            mandate_id=content['mandate_id'],
            user_id=content['user_id'],
            agent_id=content['agent_id'],
            intent=content['intent'],
            constraints=content['constraints']
        )
        mandate.status = MandateStatus(content['status'])
        return mandate
    
    def _row_to_cart_mandate(self, row) -> CartMandate:
        """DB 행을 CartMandate로 변환"""
        content = json.loads(row['content'])
        mandate = CartMandate(
            mandate_id=content['mandate_id'],
            user_id=content['user_id'],
            agent_id=content['agent_id'],
            cart_items=content['cart_items'],
            total_amount=content['total_amount'],
            intent_mandate_id=content['intent_mandate_id']
        )
        mandate.status = MandateStatus(content['status'])
        return mandate
    
    def _row_to_payment_mandate(self, row) -> PaymentMandate:
        """DB 행을 PaymentMandate로 변환"""
        content = json.loads(row['content'])
        mandate = PaymentMandate(
            mandate_id=content['mandate_id'],
            user_id=content['user_id'],
            agent_id=content['agent_id'],
            cart_mandate_id=content['cart_mandate_id'],
            payment_method=content['payment_method'],
            amount=content['amount']
        )
        mandate.status = MandateStatus(content['status'])
        return mandate


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # manager = AP2MandateManager(db_connection)
    
    # 1. Intent Mandate 생성
    # intent = manager.create_intent_mandate(
    #     user_id="USER-001",
    #     agent_id="AGENT-001",
    #     intent="식료품 구매",
    #     constraints={"max_budget": 50000, "items": ["김밥", "음료"]}
    # )
    
    # 2. 에이전트가 권한 확인
    # can_proceed = manager.verify_agent_authority(
    #     agent_id="AGENT-001",
    #     action="add_to_cart",
    #     context={"amount": 30000}
    # )
    
    # 3. Cart Mandate 생성
    # cart = manager.create_cart_mandate(
    #     user_id="USER-001",
    #     agent_id="AGENT-001",
    #     cart_items=[{"item": "김밥", "qty": 2, "price": 3000}],
    #     total_amount=6000,
    #     intent_mandate_id=intent.mandate_id
    # )
    
    # 4. Payment Mandate 생성
    # payment = manager.create_payment_mandate(
    #     user_id="USER-001",
    #     agent_id="AGENT-001",
    #     cart_mandate_id=cart.mandate_id,
    #     payment_method="AP2",
    #     amount=6000
    # )
    
    print("✅ AP2 Mandate Manager 로드 완료")

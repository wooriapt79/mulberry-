"""
Mulberry AP2 (ActivityPub 2.0) Demonstration
세계 최초 AP2 기반 위임장(Mandate) 시스템

This code demonstrates:
1. Mandate creation (위임장 생성)
2. Mandate verification (위임장 검증)
3. Agent autonomous action (에이전트 자율 실행)
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


# ============================================
# AP2 Core Types
# ============================================

class MandateScope(Enum):
    """위임 권한 범위"""
    ORDER_FOOD = "order_food"  # 식품 주문
    PAY_BILLS = "pay_bills"  # 청구서 지불
    MANAGE_DELIVERY = "manage_delivery"  # 배송 관리
    COMMUNICATE = "communicate"  # 소통 (SNS 등)
    FULL_ACCESS = "full_access"  # 전체 권한


@dataclass
class Mandate:
    """
    AP2 위임장 (Mandate)
    
    법적 효력을 가진 권한 위임 문서
    """
    mandate_id: str
    
    # 당사자
    grantor: str  # 위임자 (예: 김철수 어르신)
    grantor_id: str  # 위임자 ActivityPub ID
    grantee: str  # 수임자 (예: Mulberry_Agent_001)
    grantee_id: str  # 수임자 ActivityPub ID
    
    # 권한
    scope: List[MandateScope]  # 위임 범위
    limitations: Optional[Dict[str, Any]] = None  # 제한사항
    
    # 기간
    issued_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: str = ""
    duration_days: int = 30
    
    # 검증
    signature: str = ""  # 디지털 서명
    is_verified: bool = False
    
    def __post_init__(self):
        """초기화 후 처리"""
        if not self.expires_at:
            expiry = datetime.now() + timedelta(days=self.duration_days)
            self.expires_at = expiry.isoformat()
        
        if not self.signature:
            self.signature = self._generate_signature()
    
    def _generate_signature(self) -> str:
        """
        디지털 서명 생성
        
        실제로는 Ed25519 같은 암호화 알고리즘 사용
        여기서는 SHA-256 해시로 시뮬레이션
        """
        data = f"{self.grantor_id}:{self.grantee_id}:{self.issued_at}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def verify(self) -> bool:
        """
        위임장 검증
        
        Returns:
            bool: 검증 성공 여부
        """
        # 1. 서명 확인
        expected_sig = self._generate_signature()
        if self.signature != expected_sig:
            return False
        
        # 2. 만료 확인
        now = datetime.now()
        expiry = datetime.fromisoformat(self.expires_at)
        if now > expiry:
            return False
        
        # 3. 검증 완료
        self.is_verified = True
        return True
    
    def to_activitypub(self) -> Dict[str, Any]:
        """
        ActivityPub 형식으로 변환
        
        Returns:
            dict: ActivityPub JSON-LD
        """
        return {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://mulberry.ai/ns/mandate"
            ],
            "type": "Mandate",
            "id": f"https://mulberry.ai/mandates/{self.mandate_id}",
            "actor": self.grantor_id,
            "object": {
                "type": "Authorization",
                "to": self.grantee_id,
                "scope": [s.value for s in self.scope],
                "limitations": self.limitations or {}
            },
            "published": self.issued_at,
            "expires": self.expires_at,
            "signature": {
                "type": "RsaSignature2017",
                "created": self.issued_at,
                "signatureValue": self.signature
            }
        }


# ============================================
# AP2 Agent
# ============================================

class Agent:
    """
    AP2 에이전트
    
    위임장을 기반으로 자율적으로 행동하는 AI
    """
    
    def __init__(self, mandate: Mandate):
        """
        에이전트 초기화
        
        Args:
            mandate: 위임장
        """
        self.mandate = mandate
        self.agent_id = mandate.grantee_id
        self.agent_name = mandate.grantee
        
        # 위임장 검증
        if not self.mandate.verify():
            raise ValueError("Invalid or expired mandate")
        
        # 활동 로그
        self.activity_log: List[Dict[str, Any]] = []
    
    def can_perform(self, action: MandateScope) -> bool:
        """
        행동 가능 여부 확인
        
        Args:
            action: 행동 타입
            
        Returns:
            bool: 가능 여부
        """
        return action in self.mandate.scope or MandateScope.FULL_ACCESS in self.mandate.scope
    
    def order_food(self, items: str, auto_pay: bool = False) -> Dict[str, Any]:
        """
        식품 주문
        
        Args:
            items: 주문 항목
            auto_pay: 자동 결제 여부
            
        Returns:
            dict: 주문 결과
        """
        # 권한 확인
        if not self.can_perform(MandateScope.ORDER_FOOD):
            return {
                "success": False,
                "error": "Insufficient mandate scope"
            }
        
        # 주문 실행
        order_id = f"ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        result = {
            "success": True,
            "order_id": order_id,
            "items": items,
            "ordered_by": self.agent_name,
            "on_behalf_of": self.mandate.grantor,
            "auto_pay": auto_pay,
            "timestamp": datetime.now().isoformat()
        }
        
        # 자동 결제
        if auto_pay and self.can_perform(MandateScope.PAY_BILLS):
            result["payment_status"] = "completed"
            result["payment_method"] = "Agent Passport Auto-pay"
        
        # 활동 로그
        self.activity_log.append({
            "action": "order_food",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def to_activitypub_actor(self) -> Dict[str, Any]:
        """
        ActivityPub Actor 형식으로 변환
        
        Returns:
            dict: ActivityPub Actor JSON-LD
        """
        return {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Service",
            "id": self.agent_id,
            "name": self.agent_name,
            "preferredUsername": self.agent_name.lower(),
            "summary": f"AI Agent acting on behalf of {self.mandate.grantor}",
            "inbox": f"{self.agent_id}/inbox",
            "outbox": f"{self.agent_id}/outbox",
            "following": f"{self.agent_id}/following",
            "followers": f"{self.agent_id}/followers",
            "publicKey": {
                "id": f"{self.agent_id}#main-key",
                "owner": self.agent_id,
                "publicKeyPem": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
            }
        }


# ============================================
# Demo Functions
# ============================================

def demo_basic_mandate():
    """기본 위임장 데모"""
    print("\n" + "=" * 80)
    print("🤖 AP2 Mandate Demo: Basic Example")
    print("=" * 80)
    
    # 1. 위임장 생성
    print("\n[1] Creating Mandate...")
    mandate = Mandate(
        mandate_id="MANDATE_001",
        grantor="김철수 어르신",
        grantor_id="https://mulberry.ai/users/senior_kim",
        grantee="Mulberry_Agent_001",
        grantee_id="https://mulberry.ai/agents/001",
        scope=[
            MandateScope.ORDER_FOOD,
            MandateScope.PAY_BILLS
        ],
        duration_days=30
    )
    
    print(f"✅ Mandate created: {mandate.mandate_id}")
    print(f"   From: {mandate.grantor}")
    print(f"   To: {mandate.grantee}")
    print(f"   Scope: {[s.value for s in mandate.scope]}")
    print(f"   Valid until: {mandate.expires_at[:10]}")
    print(f"   Signature: {mandate.signature}")
    
    # 2. 위임장 검증
    print("\n[2] Verifying Mandate...")
    is_valid = mandate.verify()
    print(f"{'✅' if is_valid else '❌'} Verification result: {is_valid}")
    
    # 3. ActivityPub 형식 변환
    print("\n[3] Converting to ActivityPub format...")
    ap_json = mandate.to_activitypub()
    print(f"✅ ActivityPub JSON-LD:")
    print(json.dumps(ap_json, indent=2, ensure_ascii=False))
    
    return mandate


def demo_agent_action(mandate: Mandate):
    """에이전트 행동 데모"""
    print("\n" + "=" * 80)
    print("🤖 AP2 Agent Demo: Autonomous Action")
    print("=" * 80)
    
    # 1. 에이전트 생성
    print("\n[1] Creating Agent...")
    try:
        agent = Agent(mandate)
        print(f"✅ Agent created: {agent.agent_name}")
        print(f"   Mandate verified: {mandate.is_verified}")
    except ValueError as e:
        print(f"❌ Failed to create agent: {str(e)}")
        return
    
    # 2. 권한 확인
    print("\n[2] Checking Permissions...")
    can_order = agent.can_perform(MandateScope.ORDER_FOOD)
    can_pay = agent.can_perform(MandateScope.PAY_BILLS)
    can_manage = agent.can_perform(MandateScope.MANAGE_DELIVERY)
    
    print(f"{'✅' if can_order else '❌'} Can order food: {can_order}")
    print(f"{'✅' if can_pay else '❌'} Can pay bills: {can_pay}")
    print(f"{'✅' if can_manage else '❌'} Can manage delivery: {can_manage}")
    
    # 3. 식품 주문 (자율 실행)
    print("\n[3] Ordering Food (Autonomous)...")
    result = agent.order_food("사과 3kg, 배 2kg", auto_pay=True)
    
    if result["success"]:
        print(f"✅ Order successful!")
        print(f"   Order ID: {result['order_id']}")
        print(f"   Items: {result['items']}")
        print(f"   Ordered by: {result['ordered_by']}")
        print(f"   On behalf of: {result['on_behalf_of']}")
        print(f"   Payment: {result['payment_status']}")
    else:
        print(f"❌ Order failed: {result['error']}")
    
    # 4. 활동 로그
    print("\n[4] Activity Log...")
    for i, activity in enumerate(agent.activity_log, 1):
        print(f"\n   Activity #{i}:")
        print(f"   Action: {activity['action']}")
        print(f"   Timestamp: {activity['timestamp']}")
        print(f"   Result: {activity['result']['success']}")
    
    return agent


def demo_activitypub_federation():
    """ActivityPub Federation 데모"""
    print("\n" + "=" * 80)
    print("🌐 AP2 Federation Demo: Distributed Network")
    print("=" * 80)
    
    # 1. 여러 인스턴스
    instances = [
        "https://inje.mulberry.ai",
        "https://chuncheon.mulberry.ai",
        "https://buyeo.mulberry.ai"
    ]
    
    print("\n[1] Mulberry Federation Network...")
    for i, instance in enumerate(instances, 1):
        print(f"   {i}. {instance}")
    
    # 2. 에이전트 간 통신
    print("\n[2] Agent-to-Agent Communication (via ActivityPub)...")
    
    message = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "type": "Create",
        "actor": "https://inje.mulberry.ai/agents/001",
        "object": {
            "type": "Note",
            "content": "인제군 사과 재고 부족. 춘천에서 지원 가능?",
            "to": ["https://chuncheon.mulberry.ai/agents/001"]
        },
        "published": datetime.now().isoformat()
    }
    
    print("   Message sent:")
    print(json.dumps(message, indent=4, ensure_ascii=False))
    
    # 3. 탈중앙화의 장점
    print("\n[3] Benefits of Decentralization...")
    print("   ✅ 중앙 서버 장애 시에도 지역 운영 가능")
    print("   ✅ 지역별 독립적 정책 설정")
    print("   ✅ 데이터 주권 보장")
    print("   ✅ 확장성 (새 지역 추가 용이)")


# ============================================
# Main Demo
# ============================================

def main():
    """전체 데모 실행"""
    print("\n" + "=" * 80)
    print("🌾 Mulberry AP2 Demonstration")
    print("=" * 80)
    print("\n세계 최초의 AP2 기반 AI 협동조합")
    print("World's First AP2-Based AI Digital Cooperative")
    print("\n이 데모는 다음을 보여줍니다:")
    print("1. Mandate (위임장) 생성 및 검증")
    print("2. AI Agent의 자율적 행동")
    print("3. ActivityPub Federation 네트워크")
    
    # Demo 1: 기본 위임장
    mandate = demo_basic_mandate()
    
    # Demo 2: 에이전트 행동
    agent = demo_agent_action(mandate)
    
    # Demo 3: Federation
    demo_activitypub_federation()
    
    # 종료
    print("\n" + "=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)
    print("\n이 코드는 Mulberry의 핵심 기술을 보여줍니다:")
    print("- AP2 위임장으로 AI에게 법적 권한 부여")
    print("- 블록체인 없이 신뢰 구축 (ActivityPub)")
    print("- 탈중앙화 Federation 네트워크")
    print("\n더 자세한 정보:")
    print("- README.md: 프로젝트 개요")
    print("- docs/INFRASTRUCTURE_DESIGN.md: 아키텍처 설계")
    print("- docs/setup_raspberry_pi.md: 실전 배포 가이드")


if __name__ == "__main__":
    main()

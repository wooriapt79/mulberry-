"""
Mulberry Phase 4-B - AI Agent Guardian Module
AI 에이전트 지역 후견인 시스템

Mission: 독거노인 디지털 보호 시스템
Feature: 기부 물품 판매 대행 및 자동 정산
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from decimal import Decimal
from loguru import logger


# ============================================
# Guardian Types
# ============================================

class GuardianType(Enum):
    """후견인 타입"""
    DONATION_MANAGER = "donation_manager"  # 기부 물품 관리
    FINANCIAL_MANAGER = "financial_manager"  # 재정 관리
    HEALTH_MONITOR = "health_monitor"  # 건강 모니터링
    SOCIAL_CONNECTOR = "social_connector"  # 사회적 연결


class DonationStatus(Enum):
    """기부 물품 상태"""
    RECEIVED = "received"  # 접수
    LISTED = "listed"  # 등록됨
    SOLD = "sold"  # 판매됨
    SETTLED = "settled"  # 정산 완료
    FAILED = "failed"  # 실패


# ============================================
# Data Models
# ============================================

@dataclass
class Senior:
    """어르신 정보"""
    senior_id: str
    name: str
    age: int
    address: str
    phone: str
    
    # 가족 연락처
    family_contacts: List[Dict[str, str]] = field(default_factory=list)
    
    # 지자체 정보
    municipality: str = "인제군"
    district: str = "기린면"
    
    # 상태
    is_living_alone: bool = True
    health_status: str = "normal"
    
    # 메타데이터
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DonationItem:
    """기부 물품"""
    item_id: str
    senior_id: str
    
    # 물품 정보
    item_name: str
    category: str
    description: str
    estimated_value: Decimal
    
    # 상태
    status: DonationStatus
    
    # 판매 정보
    listed_price: Optional[Decimal] = None
    sold_price: Optional[Decimal] = None
    sold_at: Optional[str] = None
    
    # 정산 정보
    settlement_amount: Optional[Decimal] = None  # 어르신께 전달될 금액
    settlement_date: Optional[str] = None
    
    # 메타데이터
    received_at: str = field(default_factory=lambda: datetime.now().isoformat())
    photos: List[str] = field(default_factory=list)


@dataclass
class GuardianAgent:
    """후견인 에이전트"""
    agent_id: str
    agent_name: str
    guardian_type: GuardianType
    
    # 담당 어르신
    assigned_seniors: List[str]  # senior_id 리스트
    
    # 활동 내역
    total_donations_handled: int = 0
    total_amount_settled: Decimal = Decimal('0')
    
    # 상태
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================
# Guardian System
# ============================================

class GuardianSystem:
    """
    AI 에이전트 후견인 시스템
    
    독거노인을 위한 디지털 보호 및 정산 시스템
    """
    
    def __init__(self):
        """시스템 초기화"""
        # 데이터 저장소
        self.seniors: Dict[str, Senior] = {}
        self.agents: Dict[str, GuardianAgent] = {}
        self.donations: Dict[str, DonationItem] = {}
        
        # 매칭 테이블
        self.senior_to_agent: Dict[str, str] = {}  # senior_id → agent_id
        
        # 정산 테이블 (암호화 DB - 세무 데이터)
        self.settlement_ledger: List[Dict[str, Any]] = []
        
        # 통계
        self.total_donations = 0
        self.total_settlements = 0
        self.total_amount_distributed = Decimal('0')
        
        logger.info("✅ Guardian System initialized")
    
    def register_senior(
        self,
        name: str,
        age: int,
        address: str,
        phone: str,
        municipality: str = "인제군",
        district: str = "기린면"
    ) -> Senior:
        """
        어르신 등록
        
        Args:
            name: 이름
            age: 나이
            address: 주소
            phone: 전화번호
            municipality: 시군
            district: 읍면동
            
        Returns:
            Senior: 등록된 어르신 정보
        """
        senior_id = f"SENIOR_{uuid.uuid4().hex[:8].upper()}"
        
        senior = Senior(
            senior_id=senior_id,
            name=name,
            age=age,
            address=address,
            phone=phone,
            municipality=municipality,
            district=district
        )
        
        self.seniors[senior_id] = senior
        
        logger.info(f"✅ Senior registered: {name} ({senior_id})")
        
        return senior
    
    def create_guardian_agent(
        self,
        agent_name: str,
        guardian_type: GuardianType
    ) -> GuardianAgent:
        """
        후견인 에이전트 생성
        
        Args:
            agent_name: 에이전트 이름
            guardian_type: 후견인 타입
            
        Returns:
            GuardianAgent: 생성된 에이전트
        """
        agent_id = f"AGENT_{guardian_type.value.upper()}_{uuid.uuid4().hex[:8].upper()}"
        
        agent = GuardianAgent(
            agent_id=agent_id,
            agent_name=agent_name,
            guardian_type=guardian_type,
            assigned_seniors=[]
        )
        
        self.agents[agent_id] = agent
        
        logger.info(f"✅ Guardian agent created: {agent_name} ({agent_id})")
        
        return agent
    
    def assign_guardian(
        self,
        senior_id: str,
        agent_id: str
    ) -> bool:
        """
        후견인 에이전트 배정
        
        Agent-to-Human 매칭
        
        Args:
            senior_id: 어르신 ID
            agent_id: 에이전트 ID
            
        Returns:
            bool: 성공 여부
        """
        if senior_id not in self.seniors:
            logger.error(f"❌ Senior not found: {senior_id}")
            return False
        
        if agent_id not in self.agents:
            logger.error(f"❌ Agent not found: {agent_id}")
            return False
        
        # 매칭
        self.senior_to_agent[senior_id] = agent_id
        
        # 에이전트에 어르신 추가
        agent = self.agents[agent_id]
        if senior_id not in agent.assigned_seniors:
            agent.assigned_seniors.append(senior_id)
        
        senior = self.seniors[senior_id]
        
        logger.info(f"✅ Guardian assigned: {senior.name} ← {agent.agent_name}")
        
        return True
    
    def register_donation(
        self,
        senior_id: str,
        item_name: str,
        category: str,
        description: str,
        estimated_value: float,
        photos: Optional[List[str]] = None
    ) -> DonationItem:
        """
        기부 물품 등록
        
        Args:
            senior_id: 어르신 ID
            item_name: 물품명
            category: 카테고리
            description: 설명
            estimated_value: 예상 가격
            photos: 사진 목록
            
        Returns:
            DonationItem: 등록된 기부 물품
        """
        item_id = f"DONATION_{uuid.uuid4().hex[:8].upper()}"
        
        donation = DonationItem(
            item_id=item_id,
            senior_id=senior_id,
            item_name=item_name,
            category=category,
            description=description,
            estimated_value=Decimal(str(estimated_value)),
            status=DonationStatus.RECEIVED,
            photos=photos or []
        )
        
        self.donations[item_id] = donation
        self.total_donations += 1
        
        senior = self.seniors[senior_id]
        logger.info(f"✅ Donation registered: {item_name} from {senior.name}")
        
        return donation
    
    async def process_donation_sale(
        self,
        item_id: str,
        sold_price: float
    ) -> Dict[str, Any]:
        """
        기부 물품 판매 처리
        
        Args:
            item_id: 물품 ID
            sold_price: 판매 가격
            
        Returns:
            dict: 판매 결과
        """
        if item_id not in self.donations:
            return {
                "success": False,
                "error": "Item not found"
            }
        
        donation = self.donations[item_id]
        
        # 판매 처리
        donation.sold_price = Decimal(str(sold_price))
        donation.sold_at = datetime.now().isoformat()
        donation.status = DonationStatus.SOLD
        
        # 정산 금액 계산 (수수료 10% 차감)
        commission_rate = Decimal('0.10')
        settlement_amount = donation.sold_price * (Decimal('1') - commission_rate)
        
        donation.settlement_amount = settlement_amount
        
        senior = self.seniors[donation.senior_id]
        
        logger.info(f"✅ Donation sold: {donation.item_name} for ₩{sold_price:,.0f}")
        logger.info(f"💰 Settlement amount: ₩{float(settlement_amount):,.0f} (to {senior.name})")
        
        # 자동 정산 처리
        await self._process_settlement(item_id)
        
        return {
            "success": True,
            "item_id": item_id,
            "sold_price": float(donation.sold_price),
            "settlement_amount": float(settlement_amount),
            "commission": float(donation.sold_price * commission_rate)
        }
    
    async def _process_settlement(self, item_id: str):
        """
        정산 처리 (내부)
        
        Args:
            item_id: 물품 ID
        """
        donation = self.donations[item_id]
        senior = self.seniors[donation.senior_id]
        
        # 정산 기록 생성 (암호화 DB 저장용)
        settlement_record = {
            "settlement_id": f"SETTLE_{uuid.uuid4().hex[:8].upper()}",
            "item_id": item_id,
            "senior_id": donation.senior_id,
            "senior_name": senior.name,
            "municipality": senior.municipality,
            "district": senior.district,
            
            # 금액 정보
            "sold_price": float(donation.sold_price),
            "commission": float(donation.sold_price * Decimal('0.10')),
            "settlement_amount": float(donation.settlement_amount),
            
            # 라벨링 (지자체 기탁금 형식)
            "settlement_type": "municipal_contribution",  # 지자체 기탁금
            "payment_method": "bank_transfer",
            "bank_account": senior.phone,  # 실제로는 은행 계좌
            
            # 메타데이터
            "settlement_date": datetime.now().isoformat(),
            "agent_id": self.senior_to_agent.get(donation.senior_id),
            "tax_year": datetime.now().year,
            
            # 세무 데이터 라벨
            "tax_category": "donation_income",
            "tax_exempt": True,  # 기부 수익금 비과세 (확인 필요)
        }
        
        # 암호화 DB에 저장
        self.settlement_ledger.append(settlement_record)
        
        # 물품 상태 업데이트
        donation.status = DonationStatus.SETTLED
        donation.settlement_date = settlement_record["settlement_date"]
        
        # 통계 업데이트
        self.total_settlements += 1
        self.total_amount_distributed += donation.settlement_amount
        
        # 에이전트 통계 업데이트
        agent_id = self.senior_to_agent.get(donation.senior_id)
        if agent_id and agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.total_donations_handled += 1
            agent.total_amount_settled += donation.settlement_amount
        
        logger.info(f"✅ Settlement processed: {settlement_record['settlement_id']}")
        logger.info(f"💰 Amount transferred: ₩{float(donation.settlement_amount):,.0f} to {senior.name}")
        
        # 실제로는 은행 API 호출
        # await transfer_to_senior_account(senior, donation.settlement_amount)
    
    def get_senior_report(self, senior_id: str) -> Dict[str, Any]:
        """
        어르신 활동 보고서
        
        Args:
            senior_id: 어르신 ID
            
        Returns:
            dict: 보고서
        """
        if senior_id not in self.seniors:
            return {"error": "Senior not found"}
        
        senior = self.seniors[senior_id]
        
        # 해당 어르신의 기부 물품
        donations = [d for d in self.donations.values() if d.senior_id == senior_id]
        
        # 통계
        total_donations = len(donations)
        total_sold = len([d for d in donations if d.status == DonationStatus.SOLD or d.status == DonationStatus.SETTLED])
        total_amount = sum([float(d.settlement_amount or 0) for d in donations])
        
        # 담당 에이전트
        agent_id = self.senior_to_agent.get(senior_id)
        agent_name = self.agents[agent_id].agent_name if agent_id and agent_id in self.agents else "없음"
        
        return {
            "senior_id": senior_id,
            "senior_name": senior.name,
            "age": senior.age,
            "municipality": f"{senior.municipality} {senior.district}",
            "guardian_agent": agent_name,
            
            "donation_stats": {
                "total_donations": total_donations,
                "total_sold": total_sold,
                "total_amount_received": total_amount,
                "pending_items": len([d for d in donations if d.status == DonationStatus.LISTED])
            },
            
            "recent_donations": [
                {
                    "item_name": d.item_name,
                    "status": d.status.value,
                    "sold_price": float(d.sold_price) if d.sold_price else None,
                    "settlement_amount": float(d.settlement_amount) if d.settlement_amount else None
                }
                for d in sorted(donations, key=lambda x: x.received_at, reverse=True)[:5]
            ]
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """시스템 전체 통계"""
        return {
            "total_seniors": len(self.seniors),
            "total_agents": len(self.agents),
            "total_donations": self.total_donations,
            "total_settlements": self.total_settlements,
            "total_amount_distributed": float(self.total_amount_distributed),
            
            "by_municipality": self._get_municipality_breakdown(),
            "by_agent": self._get_agent_breakdown()
        }
    
    def _get_municipality_breakdown(self) -> Dict[str, Any]:
        """지자체별 통계"""
        breakdown = {}
        
        for senior in self.seniors.values():
            key = f"{senior.municipality} {senior.district}"
            
            if key not in breakdown:
                breakdown[key] = {
                    "senior_count": 0,
                    "donation_count": 0,
                    "total_amount": 0
                }
            
            breakdown[key]["senior_count"] += 1
            
            # 기부 물품 수
            donations = [d for d in self.donations.values() if d.senior_id == senior.senior_id]
            breakdown[key]["donation_count"] += len(donations)
            
            # 정산 금액
            amount = sum([float(d.settlement_amount or 0) for d in donations])
            breakdown[key]["total_amount"] += amount
        
        return breakdown
    
    def _get_agent_breakdown(self) -> Dict[str, Any]:
        """에이전트별 통계"""
        breakdown = {}
        
        for agent in self.agents.values():
            breakdown[agent.agent_name] = {
                "assigned_seniors": len(agent.assigned_seniors),
                "donations_handled": agent.total_donations_handled,
                "total_amount_settled": float(agent.total_amount_settled)
            }
        
        return breakdown


# ============================================
# Example Usage
# ============================================

async def demo_guardian_system():
    """후견인 시스템 데모"""
    system = GuardianSystem()
    
    # 1. 어르신 등록
    senior1 = system.register_senior(
        name="김철수",
        age=78,
        address="인제군 기린면 진동리",
        phone="010-1234-5678",
        municipality="인제군",
        district="기린면"
    )
    
    # 2. 후견인 에이전트 생성
    agent1 = system.create_guardian_agent(
        agent_name="인제군 기부물품 관리 에이전트",
        guardian_type=GuardianType.DONATION_MANAGER
    )
    
    # 3. 매칭
    system.assign_guardian(senior1.senior_id, agent1.agent_id)
    
    # 4. 기부 물품 등록
    donation1 = system.register_donation(
        senior_id=senior1.senior_id,
        item_name="옛날 라디오",
        category="가전제품",
        description="1970년대 진공관 라디오, 작동 가능",
        estimated_value=50000
    )
    
    # 5. 판매 처리
    sale_result = await system.process_donation_sale(
        item_id=donation1.item_id,
        sold_price=45000
    )
    
    print(f"\n✅ 판매 완료:")
    print(f"판매가: ₩{sale_result['sold_price']:,.0f}")
    print(f"정산액: ₩{sale_result['settlement_amount']:,.0f} (수수료 10% 차감)")
    
    # 6. 어르신 보고서
    report = system.get_senior_report(senior1.senior_id)
    print(f"\n📊 {report['senior_name']} 님 보고서:")
    print(f"총 기부: {report['donation_stats']['total_donations']}건")
    print(f"총 수령액: ₩{report['donation_stats']['total_amount_received']:,.0f}")
    
    # 7. 시스템 통계
    stats = system.get_system_stats()
    print(f"\n📈 시스템 전체 통계:")
    print(f"등록 어르신: {stats['total_seniors']}명")
    print(f"총 분배액: ₩{stats['total_amount_distributed']:,.0f}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_guardian_system())

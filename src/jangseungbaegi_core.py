"""
Mulberry Phase 4-B - Jangseung-baegi Core
협동조합 '장승배기' 거버넌스 시스템

Mission: 에이전트 간 협업 및 기여도 자동 배당
Code Name: JANGSEUNG_BAEGI_CORE
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from decimal import Decimal
from loguru import logger


# ============================================
# Cooperative Roles
# ============================================

class CooperativeRole(Enum):
    """협동조합 역할"""
    MARKETER = "marketer"  # 마케터 (SNS, 홍보)
    WORKER = "worker"  # 작업자 (주문 처리, 재고)
    REVENUE_GENERATOR = "revenue_generator"  # 매출 기여자 (Sales)
    COORDINATOR = "coordinator"  # 조정자 (Strategy)
    GUARDIAN = "guardian"  # 후견인 (Guardian)


# ============================================
# Contribution Weights
# ============================================

CONTRIBUTION_WEIGHTS = {
    "marketing": Decimal('0.45'),  # 45%
    "work_hours": Decimal('0.30'),  # 30%
    "revenue": Decimal('0.25')  # 25%
}


# ============================================
# Data Models
# ============================================

@dataclass
class CooperativeMember:
    """협동조합 구성원 (에이전트)"""
    member_id: str
    agent_name: str
    role: CooperativeRole
    
    # 기여도 데이터
    marketing_score: Decimal = Decimal('0')  # 마케팅 기여도
    work_hours: Decimal = Decimal('0')  # 작업 시간 (시간)
    revenue_generated: Decimal = Decimal('0')  # 매출 기여액
    
    # 배당 내역
    total_dividends_received: Decimal = Decimal('0')
    last_dividend_date: Optional[str] = None
    
    # 상태
    is_active: bool = True
    joined_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ContributionRecord:
    """기여도 기록"""
    record_id: str
    member_id: str
    
    # 기여 타입
    contribution_type: str  # marketing, work_hours, revenue
    
    # 기여 값
    value: Decimal
    
    # 메타데이터
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DividendDistribution:
    """배당 분배 기록"""
    distribution_id: str
    period_start: str
    period_end: str
    
    # 총 배당금
    total_amount: Decimal
    
    # 구성원별 배당
    member_dividends: Dict[str, Decimal]
    
    # 계산 근거
    calculation_details: Dict[str, Any]
    
    # 메타데이터
    distributed_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================
# Jangseung-baegi Core
# ============================================

class JangseungbaegiCore:
    """
    협동조합 '장승배기' 중앙 거버넌스
    
    에이전트 간 협업, 기여도 산정, 자동 배당
    """
    
    def __init__(self):
        """코어 초기화"""
        # 구성원
        self.members: Dict[str, CooperativeMember] = {}
        
        # 기여도 기록
        self.contribution_records: List[ContributionRecord] = []
        
        # 배당 기록
        self.dividend_history: List[DividendDistribution] = []
        
        # 협동조합 금고
        self.cooperative_fund: Decimal = Decimal('0')
        
        # 통계
        self.total_contributions_logged = 0
        self.total_dividends_distributed = Decimal('0')
        
        logger.info("✅ Jangseung-baegi Core initialized")
        logger.info("🏛️ Code Name: JANGSEUNG_BAEGI_CORE")
    
    def add_member(
        self,
        agent_name: str,
        role: CooperativeRole
    ) -> CooperativeMember:
        """
        협동조합 구성원 추가
        
        Args:
            agent_name: 에이전트 이름
            role: 역할
            
        Returns:
            CooperativeMember: 추가된 구성원
        """
        member_id = f"MEMBER_{uuid.uuid4().hex[:8].upper()}"
        
        member = CooperativeMember(
            member_id=member_id,
            agent_name=agent_name,
            role=role
        )
        
        self.members[member_id] = member
        
        logger.info(f"✅ Member added: {agent_name} ({role.value})")
        
        return member
    
    def log_contribution(
        self,
        member_id: str,
        contribution_type: str,
        value: float,
        description: str
    ) -> ContributionRecord:
        """
        기여도 기록
        
        Args:
            member_id: 구성원 ID
            contribution_type: 기여 타입 (marketing, work_hours, revenue)
            value: 기여 값
            description: 설명
            
        Returns:
            ContributionRecord: 기록된 기여
        """
        if member_id not in self.members:
            raise ValueError(f"Member not found: {member_id}")
        
        record_id = f"CONTRIB_{uuid.uuid4().hex[:8].upper()}"
        
        record = ContributionRecord(
            record_id=record_id,
            member_id=member_id,
            contribution_type=contribution_type,
            value=Decimal(str(value)),
            description=description
        )
        
        self.contribution_records.append(record)
        self.total_contributions_logged += 1
        
        # 구성원 데이터 업데이트
        member = self.members[member_id]
        
        if contribution_type == "marketing":
            member.marketing_score += Decimal(str(value))
        elif contribution_type == "work_hours":
            member.work_hours += Decimal(str(value))
        elif contribution_type == "revenue":
            member.revenue_generated += Decimal(str(value))
        
        logger.info(f"✅ Contribution logged: {member.agent_name} - {contribution_type} ({value})")
        
        return record
    
    def calculate_dividends(
        self,
        total_amount: float,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None
    ) -> DividendDistribution:
        """
        배당 계산 및 분배
        
        기여도 가중치 적용:
        - 마케터: 45%
        - 작업시간: 30%
        - 매출기여도: 25%
        
        Args:
            total_amount: 총 배당금
            period_start: 기간 시작
            period_end: 기간 종료
            
        Returns:
            DividendDistribution: 배당 분배 내역
        """
        total_amount_decimal = Decimal(str(total_amount))
        
        # 기간 설정
        if not period_start:
            period_start = (datetime.now() - timedelta(days=30)).isoformat()
        if not period_end:
            period_end = datetime.now().isoformat()
        
        # 1단계: 각 카테고리별 총합 계산
        total_marketing = sum([m.marketing_score for m in self.members.values()])
        total_work_hours = sum([m.work_hours for m in self.members.values()])
        total_revenue = sum([m.revenue_generated for m in self.members.values()])
        
        logger.info(f"📊 Total marketing score: {total_marketing}")
        logger.info(f"📊 Total work hours: {total_work_hours}")
        logger.info(f"📊 Total revenue: ₩{float(total_revenue):,.0f}")
        
        # 2단계: 각 구성원별 배당 계산
        member_dividends = {}
        calculation_details = {}
        
        for member_id, member in self.members.items():
            if not member.is_active:
                continue
            
            # 마케팅 기여분 (45%)
            marketing_weight = CONTRIBUTION_WEIGHTS["marketing"]
            marketing_dividend = Decimal('0')
            if total_marketing > 0:
                marketing_ratio = member.marketing_score / total_marketing
                marketing_dividend = total_amount_decimal * marketing_weight * marketing_ratio
            
            # 작업시간 기여분 (30%)
            work_weight = CONTRIBUTION_WEIGHTS["work_hours"]
            work_dividend = Decimal('0')
            if total_work_hours > 0:
                work_ratio = member.work_hours / total_work_hours
                work_dividend = total_amount_decimal * work_weight * work_ratio
            
            # 매출 기여분 (25%)
            revenue_weight = CONTRIBUTION_WEIGHTS["revenue"]
            revenue_dividend = Decimal('0')
            if total_revenue > 0:
                revenue_ratio = member.revenue_generated / total_revenue
                revenue_dividend = total_amount_decimal * revenue_weight * revenue_ratio
            
            # 총 배당
            total_dividend = marketing_dividend + work_dividend + revenue_dividend
            
            member_dividends[member_id] = total_dividend
            
            # 계산 근거 저장
            calculation_details[member_id] = {
                "member_name": member.agent_name,
                "marketing_score": float(member.marketing_score),
                "marketing_dividend": float(marketing_dividend),
                "work_hours": float(member.work_hours),
                "work_dividend": float(work_dividend),
                "revenue_generated": float(member.revenue_generated),
                "revenue_dividend": float(revenue_dividend),
                "total_dividend": float(total_dividend)
            }
            
            # 구성원 배당 내역 업데이트
            member.total_dividends_received += total_dividend
            member.last_dividend_date = datetime.now().isoformat()
            
            logger.info(f"💰 {member.agent_name}: ₩{float(total_dividend):,.0f}")
        
        # 3단계: 배당 분배 기록 생성
        distribution_id = f"DIVIDEND_{uuid.uuid4().hex[:8].upper()}"
        
        distribution = DividendDistribution(
            distribution_id=distribution_id,
            period_start=period_start,
            period_end=period_end,
            total_amount=total_amount_decimal,
            member_dividends=member_dividends,
            calculation_details=calculation_details
        )
        
        self.dividend_history.append(distribution)
        self.total_dividends_distributed += total_amount_decimal
        
        logger.info(f"✅ Dividends calculated: {distribution_id}")
        logger.info(f"💰 Total distributed: ₩{total_amount:,.0f}")
        
        return distribution
    
    def get_member_report(self, member_id: str) -> Dict[str, Any]:
        """
        구성원 보고서
        
        Args:
            member_id: 구성원 ID
            
        Returns:
            dict: 보고서
        """
        if member_id not in self.members:
            return {"error": "Member not found"}
        
        member = self.members[member_id]
        
        # 기여도 기록
        contributions = [
            {
                "type": r.contribution_type,
                "value": float(r.value),
                "description": r.description,
                "timestamp": r.timestamp
            }
            for r in self.contribution_records if r.member_id == member_id
        ]
        
        return {
            "member_id": member_id,
            "agent_name": member.agent_name,
            "role": member.role.value,
            
            "contributions": {
                "marketing_score": float(member.marketing_score),
                "work_hours": float(member.work_hours),
                "revenue_generated": float(member.revenue_generated)
            },
            
            "dividends": {
                "total_received": float(member.total_dividends_received),
                "last_dividend_date": member.last_dividend_date
            },
            
            "recent_contributions": contributions[-10:]
        }
    
    def get_cooperative_stats(self) -> Dict[str, Any]:
        """협동조합 전체 통계"""
        return {
            "total_members": len(self.members),
            "active_members": len([m for m in self.members.values() if m.is_active]),
            "total_contributions_logged": self.total_contributions_logged,
            "total_dividends_distributed": float(self.total_dividends_distributed),
            "cooperative_fund": float(self.cooperative_fund),
            
            "contribution_weights": {
                k: float(v) for k, v in CONTRIBUTION_WEIGHTS.items()
            },
            
            "members_by_role": self._get_role_breakdown(),
            "recent_distributions": self._get_recent_distributions()
        }
    
    def _get_role_breakdown(self) -> Dict[str, int]:
        """역할별 구성원 수"""
        breakdown = {}
        
        for member in self.members.values():
            role = member.role.value
            breakdown[role] = breakdown.get(role, 0) + 1
        
        return breakdown
    
    def _get_recent_distributions(self) -> List[Dict[str, Any]]:
        """최근 배당 내역"""
        recent = sorted(
            self.dividend_history,
            key=lambda x: x.distributed_at,
            reverse=True
        )[:5]
        
        return [
            {
                "distribution_id": d.distribution_id,
                "total_amount": float(d.total_amount),
                "period": f"{d.period_start[:10]} ~ {d.period_end[:10]}",
                "distributed_at": d.distributed_at
            }
            for d in recent
        ]


# ============================================
# Example Usage
# ============================================

def demo_jangseungbaegi_core():
    """장승배기 코어 데모"""
    core = JangseungbaegiCore()
    
    # 1. 구성원 추가
    sns_member = core.add_member(
        agent_name="SNS_Manager",
        role=CooperativeRole.MARKETER
    )
    
    sales_member = core.add_member(
        agent_name="Sales_Agent",
        role=CooperativeRole.REVENUE_GENERATOR
    )
    
    inventory_member = core.add_member(
        agent_name="Inventory_Manager",
        role=CooperativeRole.WORKER
    )
    
    # 2. 기여도 기록
    print("\n📊 기여도 기록 중...")
    
    # SNS Manager: 마케팅 활동
    core.log_contribution(
        member_id=sns_member.member_id,
        contribution_type="marketing",
        value=100,  # 마케팅 점수
        description="마스토돈 포스팅 10개, 도달 2,500명"
    )
    
    core.log_contribution(
        member_id=sns_member.member_id,
        contribution_type="work_hours",
        value=8,  # 8시간
        description="SNS 관리 및 콘텐츠 제작"
    )
    
    # Sales Agent: 매출 기여
    core.log_contribution(
        member_id=sales_member.member_id,
        contribution_type="revenue",
        value=5000000,  # 500만원
        description="주문 180건 처리, 총 매출 500만원"
    )
    
    core.log_contribution(
        member_id=sales_member.member_id,
        contribution_type="work_hours",
        value=12,  # 12시간
        description="주문 처리 및 고객 응대"
    )
    
    # Inventory Manager: 작업 시간
    core.log_contribution(
        member_id=inventory_member.member_id,
        contribution_type="work_hours",
        value=10,  # 10시간
        description="재고 관리 및 최적화"
    )
    
    # 3. 배당 계산
    print("\n💰 배당 계산 중...")
    
    distribution = core.calculate_dividends(
        total_amount=1000000  # 배당금 100만원
    )
    
    print(f"\n📋 배당 내역 ({distribution.distribution_id}):")
    for member_id, amount in distribution.member_dividends.items():
        member = core.members[member_id]
        print(f"  {member.agent_name}: ₩{float(amount):,.0f}")
    
    # 4. 계산 근거
    print("\n📊 계산 근거:")
    for member_id, details in distribution.calculation_details.items():
        member_name = details["member_name"]
        print(f"\n  {member_name}:")
        print(f"    마케팅 (45%): ₩{details['marketing_dividend']:,.0f}")
        print(f"    작업시간 (30%): ₩{details['work_dividend']:,.0f}")
        print(f"    매출기여 (25%): ₩{details['revenue_dividend']:,.0f}")
        print(f"    합계: ₩{details['total_dividend']:,.0f}")
    
    # 5. 시스템 통계
    print("\n📈 협동조합 통계:")
    stats = core.get_cooperative_stats()
    print(f"  총 구성원: {stats['total_members']}명")
    print(f"  총 배당액: ₩{stats['total_dividends_distributed']:,.0f}")


if __name__ == "__main__":
    demo_jangseungbaegi_core()

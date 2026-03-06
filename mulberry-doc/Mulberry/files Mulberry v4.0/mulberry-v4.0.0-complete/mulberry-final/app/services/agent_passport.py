"""
Mulberry Phase 4-A - Agent Passport
에이전트 신원증명 및 자율 결제 시스템

에이전트가 직접 결제하고 지출할 수 있는 권한 관리
"""

import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from loguru import logger


# ============================================
# Agent Permission Levels
# ============================================

class PermissionLevel(Enum):
    """에이전트 권한 수준"""
    RESTRICTED = 1  # 제한됨: 읽기만 가능
    BASIC = 2  # 기본: 소액 결제 가능
    STANDARD = 3  # 표준: 일반 결제 가능
    ELEVATED = 4  # 상승: 고액 결제 가능
    ADMIN = 5  # 관리자: 무제한


class PaymentCategory(Enum):
    """결제 카테고리"""
    INVENTORY_PURCHASE = "inventory_purchase"  # 재고 구매
    PROMOTION_AD = "promotion_ad"  # 프로모션 광고
    DELIVERY_FEE = "delivery_fee"  # 배송비
    SERVICE_FEE = "service_fee"  # 서비스 수수료
    EMERGENCY = "emergency"  # 긴급 지출
    MAINTENANCE = "maintenance"  # 유지보수


# ============================================
# Agent Passport
# ============================================

@dataclass
class AgentPassport:
    """
    에이전트 신원증명서
    
    에이전트의 신원, 권한, 예산을 관리
    """
    # 신원 정보
    agent_id: str  # 고유 ID
    agent_name: str  # 에이전트 이름
    agent_type: str  # 에이전트 타입 (SNS_Manager, Sales_Agent 등)
    
    # 권한
    permission_level: PermissionLevel  # 권한 수준
    allowed_categories: List[PaymentCategory]  # 허용된 결제 카테고리
    
    # 예산
    daily_budget: float  # 일일 예산
    monthly_budget: float  # 월간 예산
    remaining_daily: float  # 남은 일일 예산
    remaining_monthly: float  # 남은 월간 예산
    
    # 결제 한도
    single_transaction_limit: float  # 1회 결제 한도
    auto_approve_threshold: float  # 자동 승인 금액 (이하는 자동, 이상은 승인 필요)
    
    # 메타데이터
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True
    
    # 지출 기록
    transaction_history: List[Dict[str, Any]] = field(default_factory=list)


# ============================================
# Agent Wallet
# ============================================

class AgentWallet:
    """
    에이전트 지갑
    
    실제 결제 처리 및 예산 관리
    """
    
    def __init__(self, passport: AgentPassport):
        """
        지갑 초기화
        
        Args:
            passport: 에이전트 신원증명서
        """
        self.passport = passport
        
        # 승인 대기 거래
        self.pending_approvals: List[Dict[str, Any]] = []
        
        logger.info(f"✅ Agent Wallet initialized for {passport.agent_name}")
    
    def can_spend(
        self,
        amount: float,
        category: PaymentCategory
    ) -> Dict[str, Any]:
        """
        지출 가능 여부 확인
        
        Args:
            amount: 금액
            category: 카테고리
            
        Returns:
            dict: {
                "allowed": bool,
                "reason": str,
                "requires_approval": bool
            }
        """
        # 1. 활성 상태 확인
        if not self.passport.is_active:
            return {
                "allowed": False,
                "reason": "Agent passport is inactive",
                "requires_approval": False
            }
        
        # 2. 카테고리 권한 확인
        if category not in self.passport.allowed_categories:
            return {
                "allowed": False,
                "reason": f"Category {category.value} not allowed",
                "requires_approval": False
            }
        
        # 3. 1회 결제 한도 확인
        if amount > self.passport.single_transaction_limit:
            return {
                "allowed": False,
                "reason": f"Exceeds single transaction limit (₩{self.passport.single_transaction_limit:,.0f})",
                "requires_approval": False
            }
        
        # 4. 예산 확인
        if amount > self.passport.remaining_daily:
            return {
                "allowed": False,
                "reason": f"Exceeds daily budget (remaining: ₩{self.passport.remaining_daily:,.0f})",
                "requires_approval": False
            }
        
        if amount > self.passport.remaining_monthly:
            return {
                "allowed": False,
                "reason": f"Exceeds monthly budget (remaining: ₩{self.passport.remaining_monthly:,.0f})",
                "requires_approval": False
            }
        
        # 5. 자동 승인 여부 확인
        requires_approval = amount > self.passport.auto_approve_threshold
        
        return {
            "allowed": True,
            "reason": "OK",
            "requires_approval": requires_approval
        }
    
    async def spend(
        self,
        amount: float,
        category: PaymentCategory,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        지출 실행
        
        Args:
            amount: 금액
            category: 카테고리
            description: 설명
            metadata: 추가 정보
            
        Returns:
            dict: 거래 결과
        """
        try:
            # 지출 가능 여부 확인
            check = self.can_spend(amount, category)
            
            if not check["allowed"]:
                logger.warning(f"❌ Spending denied: {check['reason']}")
                return {
                    "success": False,
                    "reason": check["reason"]
                }
            
            # 거래 ID 생성
            transaction_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
            
            # 거래 데이터
            transaction = {
                "transaction_id": transaction_id,
                "agent_id": self.passport.agent_id,
                "agent_name": self.passport.agent_name,
                "amount": amount,
                "category": category.value,
                "description": description,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "status": "pending" if check["requires_approval"] else "completed"
            }
            
            # 승인 필요 시
            if check["requires_approval"]:
                logger.info(f"⏳ Transaction requires approval: {transaction_id} (₩{amount:,.0f})")
                
                self.pending_approvals.append(transaction)
                
                # Sentinel에게 승인 요청 (향후 구현)
                # await self._request_approval(transaction)
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "status": "pending_approval",
                    "message": f"Transaction pending approval (₩{amount:,.0f})"
                }
            
            # 자동 승인
            else:
                # 예산 차감
                self.passport.remaining_daily -= amount
                self.passport.remaining_monthly -= amount
                self.passport.last_updated = datetime.now().isoformat()
                
                # 거래 기록
                self.passport.transaction_history.append(transaction)
                
                logger.info(f"✅ Transaction completed: {transaction_id} (₩{amount:,.0f})")
                logger.info(f"💰 Remaining daily: ₩{self.passport.remaining_daily:,.0f}")
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "status": "completed",
                    "amount": amount,
                    "remaining_daily": self.passport.remaining_daily,
                    "remaining_monthly": self.passport.remaining_monthly
                }
            
        except Exception as e:
            logger.error(f"❌ Spending error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def approve_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        거래 승인 (Sentinel/관리자)
        
        Args:
            transaction_id: 거래 ID
            
        Returns:
            dict: 승인 결과
        """
        try:
            # 대기 중인 거래 찾기
            transaction = None
            for txn in self.pending_approvals:
                if txn["transaction_id"] == transaction_id:
                    transaction = txn
                    break
            
            if not transaction:
                return {
                    "success": False,
                    "reason": "Transaction not found"
                }
            
            # 승인 처리
            amount = transaction["amount"]
            
            # 예산 차감
            self.passport.remaining_daily -= amount
            self.passport.remaining_monthly -= amount
            self.passport.last_updated = datetime.now().isoformat()
            
            # 상태 변경
            transaction["status"] = "completed"
            transaction["approved_at"] = datetime.now().isoformat()
            
            # 거래 기록
            self.passport.transaction_history.append(transaction)
            
            # 대기 목록에서 제거
            self.pending_approvals.remove(transaction)
            
            logger.info(f"✅ Transaction approved: {transaction_id} (₩{amount:,.0f})")
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": "completed",
                "amount": amount
            }
            
        except Exception as e:
            logger.error(f"❌ Approval error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_spending_summary(self) -> Dict[str, Any]:
        """지출 요약"""
        total_spent_today = self.passport.daily_budget - self.passport.remaining_daily
        total_spent_month = self.passport.monthly_budget - self.passport.remaining_monthly
        
        # 카테고리별 지출
        category_breakdown = {}
        for txn in self.passport.transaction_history:
            if txn["status"] == "completed":
                category = txn["category"]
                category_breakdown[category] = category_breakdown.get(category, 0) + txn["amount"]
        
        return {
            "agent_name": self.passport.agent_name,
            "daily_budget": self.passport.daily_budget,
            "spent_today": total_spent_today,
            "remaining_today": self.passport.remaining_daily,
            "monthly_budget": self.passport.monthly_budget,
            "spent_month": total_spent_month,
            "remaining_month": self.passport.remaining_monthly,
            "total_transactions": len(self.passport.transaction_history),
            "pending_approvals": len(self.pending_approvals),
            "category_breakdown": category_breakdown
        }


# ============================================
# Agent Passport Manager
# ============================================

class AgentPassportManager:
    """
    에이전트 신원증명 관리자
    
    모든 에이전트의 Passport 발급 및 관리
    """
    
    def __init__(self):
        """관리자 초기화"""
        self.passports: Dict[str, AgentPassport] = {}
        self.wallets: Dict[str, AgentWallet] = {}
        
        logger.info("✅ Agent Passport Manager initialized")
    
    def issue_passport(
        self,
        agent_name: str,
        agent_type: str,
        permission_level: PermissionLevel,
        daily_budget: float,
        monthly_budget: float,
        allowed_categories: List[PaymentCategory]
    ) -> AgentPassport:
        """
        신원증명서 발급
        
        Args:
            agent_name: 에이전트 이름
            agent_type: 에이전트 타입
            permission_level: 권한 수준
            daily_budget: 일일 예산
            monthly_budget: 월간 예산
            allowed_categories: 허용 카테고리
            
        Returns:
            AgentPassport: 발급된 신원증명서
        """
        agent_id = f"AGENT_{uuid.uuid4().hex[:8].upper()}"
        
        # 권한별 한도 설정
        limits = {
            PermissionLevel.BASIC: {
                "single": 50000,  # 5만원
                "auto_approve": 10000  # 1만원
            },
            PermissionLevel.STANDARD: {
                "single": 200000,  # 20만원
                "auto_approve": 50000  # 5만원
            },
            PermissionLevel.ELEVATED: {
                "single": 1000000,  # 100만원
                "auto_approve": 200000  # 20만원
            },
            PermissionLevel.ADMIN: {
                "single": float('inf'),
                "auto_approve": 1000000  # 100만원
            }
        }
        
        limit = limits.get(permission_level, limits[PermissionLevel.BASIC])
        
        passport = AgentPassport(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type,
            permission_level=permission_level,
            allowed_categories=allowed_categories,
            daily_budget=daily_budget,
            monthly_budget=monthly_budget,
            remaining_daily=daily_budget,
            remaining_monthly=monthly_budget,
            single_transaction_limit=limit["single"],
            auto_approve_threshold=limit["auto_approve"]
        )
        
        # 저장
        self.passports[agent_id] = passport
        
        # 지갑 생성
        self.wallets[agent_id] = AgentWallet(passport)
        
        logger.info(f"✅ Passport issued: {agent_name} ({agent_id})")
        logger.info(f"💰 Daily budget: ₩{daily_budget:,.0f}")
        logger.info(f"💰 Monthly budget: ₩{monthly_budget:,.0f}")
        
        return passport
    
    def get_wallet(self, agent_id: str) -> Optional[AgentWallet]:
        """에이전트 지갑 조회"""
        return self.wallets.get(agent_id)
    
    def get_all_spending_summary(self) -> Dict[str, Any]:
        """전체 에이전트 지출 요약"""
        summaries = {}
        
        total_spent_today = 0
        total_spent_month = 0
        
        for agent_id, wallet in self.wallets.items():
            summary = wallet.get_spending_summary()
            summaries[wallet.passport.agent_name] = summary
            
            total_spent_today += summary["spent_today"]
            total_spent_month += summary["spent_month"]
        
        return {
            "total_agents": len(self.wallets),
            "total_spent_today": total_spent_today,
            "total_spent_month": total_spent_month,
            "agent_summaries": summaries
        }


# ============================================
# 사용 예시
# ============================================

async def example_usage():
    """Agent Passport 사용 예시"""
    
    # 1. Passport Manager 생성
    manager = AgentPassportManager()
    
    # 2. SNS Manager에게 Passport 발급
    sns_passport = manager.issue_passport(
        agent_name="SNS_Manager",
        agent_type="sns_manager",
        permission_level=PermissionLevel.STANDARD,
        daily_budget=100000,  # 일일 10만원
        monthly_budget=3000000,  # 월간 300만원
        allowed_categories=[
            PaymentCategory.PROMOTION_AD,
            PaymentCategory.SERVICE_FEE
        ]
    )
    
    # 3. 지갑 가져오기
    sns_wallet = manager.get_wallet(sns_passport.agent_id)
    
    # 4. 광고 결제 (자동 승인)
    result1 = await sns_wallet.spend(
        amount=30000,
        category=PaymentCategory.PROMOTION_AD,
        description="마스토돈 프로모션 광고",
        metadata={"platform": "mastodon", "duration_days": 7}
    )
    
    print(f"결제 1: {result1}")
    
    # 5. 고액 결제 (승인 필요)
    result2 = await sns_wallet.spend(
        amount=150000,
        category=PaymentCategory.PROMOTION_AD,
        description="대규모 SNS 캠페인",
        metadata={"platform": "multiple", "duration_days": 30}
    )
    
    print(f"결제 2: {result2}")
    
    # 6. 지출 요약
    summary = sns_wallet.get_spending_summary()
    print(f"지출 요약: {json.dumps(summary, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    asyncio.run(example_usage())

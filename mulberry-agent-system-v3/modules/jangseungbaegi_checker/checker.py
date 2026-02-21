"""
Mulberry Jangseungbaegi 5 Principles Checker
CTO Koda

장승배기 5대 행동 강령 실시간 체크 + 상부상조 10% 자동 배분
"""

from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
import json


class Principle(str, Enum):
    """장승배기 5대 강령"""
    MUTUAL_AID = "mutual_aid"            # 상부상조
    TRANSPARENCY = "transparency"        # 투명성
    RESPONSIBILITY = "responsibility"    # 책임감
    COMMUNITY = "community"              # 공동체 정신
    EXCELLENCE = "excellence"            # 탁월성 추구


class ViolationType(str, Enum):
    """위반 종류"""
    WARNING = "warning"      # 경고
    MINOR = "minor"          # 경미
    MAJOR = "major"          # 중대
    CRITICAL = "critical"    # 심각


class PrincipleCheck:
    """강령 준수 체크 기록"""
    
    def __init__(
        self,
        check_id: str,
        agent_id: str,
        principle: Principle,
        action: str,
        followed: bool
    ):
        self.check_id = check_id
        self.agent_id = agent_id
        self.principle = principle
        self.action = action  # 수행한 행동
        self.followed = followed  # 준수 여부
        
        self.created_at = datetime.now()
        
        # 위반 시 추가 정보
        self.violation_type: Optional[ViolationType] = None
        self.violation_details: Optional[str] = None
        self.penalty_points: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "check_id": self.check_id,
            "agent_id": self.agent_id,
            "principle": self.principle.value,
            "action": self.action,
            "followed": self.followed,
            "created_at": self.created_at.isoformat(),
            "violation_type": self.violation_type.value if self.violation_type else None,
            "violation_details": self.violation_details,
            "penalty_points": self.penalty_points
        }


class MutualAidTransaction:
    """상부상조 거래 기록"""
    
    def __init__(
        self,
        transaction_id: str,
        from_agent_id: str,
        to_agent_id: str,
        amount: float,
        reason: str
    ):
        self.transaction_id = transaction_id
        self.from_agent_id = from_agent_id
        self.to_agent_id = to_agent_id
        self.amount = amount
        self.reason = reason
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "from_agent_id": self.from_agent_id,
            "to_agent_id": self.to_agent_id,
            "amount": self.amount,
            "reason": self.reason,
            "created_at": self.created_at.isoformat()
        }


class JangseungbaegiChecker:
    """
    장승배기 강령 체크 및 상부상조 시스템
    """
    
    # 위반 시 페널티 점수
    VIOLATION_PENALTIES = {
        ViolationType.WARNING: 0.01,
        ViolationType.MINOR: 0.05,
        ViolationType.MAJOR: 0.1,
        ViolationType.CRITICAL: 0.5
    }
    
    def __init__(self, db_connection, spirit_score_manager):
        """
        Args:
            db_connection: 데이터베이스 연결
            spirit_score_manager: Spirit Score 관리자
        """
        self.db = db_connection
        self.spirit_manager = spirit_score_manager
    
    # ============================================
    # 강령 체크 메서드
    # ============================================
    
    def check_mutual_aid(
        self,
        agent_id: str,
        helped_someone: bool,
        context: Optional[str] = None
    ) -> PrincipleCheck:
        """
        상부상조 체크
        
        Args:
            agent_id: 에이전트 ID
            helped_someone: 누군가를 도왔는가
            context: 상황 설명
        
        Returns:
            체크 기록
        """
        check_id = f"CHECK-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        check = PrincipleCheck(
            check_id=check_id,
            agent_id=agent_id,
            principle=Principle.MUTUAL_AID,
            action=context or "상부상조 기회",
            followed=helped_someone
        )
        
        if not helped_someone:
            # 위반!
            check.violation_type = ViolationType.MINOR
            check.violation_details = "다른 에이전트 도움 요청을 거절함"
            check.penalty_points = self.VIOLATION_PENALTIES[ViolationType.MINOR]
            
            # Spirit Score 차감
            self.spirit_manager.on_constitution_check(agent_id, False, "상부상조")
        else:
            # 준수!
            self.spirit_manager.on_constitution_check(agent_id, True, "상부상조")
        
        self._save_check(check)
        
        return check
    
    def check_transparency(
        self,
        agent_id: str,
        disclosed_properly: bool,
        transaction_type: str
    ) -> PrincipleCheck:
        """
        투명성 체크
        
        Args:
            agent_id: 에이전트 ID
            disclosed_properly: 제대로 공개했는가
            transaction_type: 거래 종류
        
        Returns:
            체크 기록
        """
        check_id = f"CHECK-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        check = PrincipleCheck(
            check_id=check_id,
            agent_id=agent_id,
            principle=Principle.TRANSPARENCY,
            action=f"거래 공개: {transaction_type}",
            followed=disclosed_properly
        )
        
        if not disclosed_properly:
            # 심각한 위반!
            check.violation_type = ViolationType.MAJOR
            check.violation_details = "거래 내역 은폐 시도"
            check.penalty_points = self.VIOLATION_PENALTIES[ViolationType.MAJOR]
            
            self.spirit_manager.on_constitution_check(agent_id, False, "투명성")
        else:
            self.spirit_manager.on_constitution_check(agent_id, True, "투명성")
        
        self._save_check(check)
        
        return check
    
    def check_responsibility(
        self,
        agent_id: str,
        completed_task: bool,
        task_description: str
    ) -> PrincipleCheck:
        """
        책임감 체크
        
        Args:
            agent_id: 에이전트 ID
            completed_task: 작업 완료했는가
            task_description: 작업 설명
        
        Returns:
            체크 기록
        """
        check_id = f"CHECK-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        check = PrincipleCheck(
            check_id=check_id,
            agent_id=agent_id,
            principle=Principle.RESPONSIBILITY,
            action=f"작업: {task_description}",
            followed=completed_task
        )
        
        if not completed_task:
            check.violation_type = ViolationType.MINOR
            check.violation_details = "맡은 작업 미완수"
            check.penalty_points = self.VIOLATION_PENALTIES[ViolationType.MINOR]
            
            self.spirit_manager.on_constitution_check(agent_id, False, "책임감")
        else:
            self.spirit_manager.on_constitution_check(agent_id, True, "책임감")
        
        self._save_check(check)
        
        return check
    
    def check_community(
        self,
        agent_id: str,
        contributed: bool,
        contribution_type: str
    ) -> PrincipleCheck:
        """
        공동체 정신 체크
        
        Args:
            agent_id: 에이전트 ID
            contributed: 기여했는가
            contribution_type: 기여 종류
        
        Returns:
            체크 기록
        """
        check_id = f"CHECK-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        check = PrincipleCheck(
            check_id=check_id,
            agent_id=agent_id,
            principle=Principle.COMMUNITY,
            action=f"커뮤니티 기여: {contribution_type}",
            followed=contributed
        )
        
        if not contributed:
            check.violation_type = ViolationType.WARNING
            check.violation_details = "커뮤니티 기여 기회 무시"
            check.penalty_points = self.VIOLATION_PENALTIES[ViolationType.WARNING]
            
            self.spirit_manager.on_constitution_check(agent_id, False, "공동체 정신")
        else:
            self.spirit_manager.on_constitution_check(agent_id, True, "공동체 정신")
        
        self._save_check(check)
        
        return check
    
    def check_excellence(
        self,
        agent_id: str,
        quality_standard_met: bool,
        service_type: str
    ) -> PrincipleCheck:
        """
        탁월성 추구 체크
        
        Args:
            agent_id: 에이전트 ID
            quality_standard_met: 품질 기준 충족했는가
            service_type: 서비스 종류
        
        Returns:
            체크 기록
        """
        check_id = f"CHECK-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        check = PrincipleCheck(
            check_id=check_id,
            agent_id=agent_id,
            principle=Principle.EXCELLENCE,
            action=f"서비스 품질: {service_type}",
            followed=quality_standard_met
        )
        
        if not quality_standard_met:
            check.violation_type = ViolationType.MINOR
            check.violation_details = "품질 기준 미달"
            check.penalty_points = self.VIOLATION_PENALTIES[ViolationType.MINOR]
            
            self.spirit_manager.on_constitution_check(agent_id, False, "탁월성 추구")
        else:
            self.spirit_manager.on_constitution_check(agent_id, True, "탁월성 추구")
        
        self._save_check(check)
        
        return check
    
    # ============================================
    # 상부상조 10% 시스템
    # ============================================
    
    def process_mutual_aid_contribution(
        self,
        agent_id: str,
        total_earnings: float,
        period: str = "daily"
    ) -> List[MutualAidTransaction]:
        """
        상부상조 10% 자동 배분
        
        에이전트 수익의 10%를 어려운 에이전트들에게 자동 배분
        
        Args:
            agent_id: 에이전트 ID
            total_earnings: 총 수익
            period: 기간 ("daily", "weekly", "monthly")
        
        Returns:
            생성된 거래 목록
        """
        # 10% 계산
        contribution_amount = total_earnings * 0.1
        
        if contribution_amount <= 0:
            return []
        
        # 도움이 필요한 에이전트 찾기
        # (Spirit Score 낮은 에이전트, 최근 실적 저조 등)
        recipients = self._find_agents_needing_help(exclude_agent=agent_id, limit=5)
        
        if not recipients:
            print(f"ℹ️ 도움이 필요한 에이전트 없음")
            return []
        
        # 균등 배분
        amount_per_recipient = contribution_amount / len(recipients)
        
        transactions = []
        
        for recipient_id in recipients:
            transaction_id = f"MUTAID-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            transaction = MutualAidTransaction(
                transaction_id=transaction_id,
                from_agent_id=agent_id,
                to_agent_id=recipient_id,
                amount=amount_per_recipient,
                reason=f"상부상조 {period} 배분"
            )
            
            # 저장
            self._save_mutual_aid_transaction(transaction)
            
            # Spirit Score 부여 (도운 에이전트)
            self.spirit_manager.on_help_provided(
                helper_agent_id=agent_id,
                helped_agent_id=recipient_id,
                help_type=f"상부상조 {amount_per_recipient}원"
            )
            
            transactions.append(transaction)
            
            print(f"💰 상부상조: {agent_id} → {recipient_id} ({amount_per_recipient}원)")
        
        print(f"✅ 상부상조 10% 배분 완료: 총 {contribution_amount}원 → {len(recipients)}명")
        
        return transactions
    
    def get_agent_compliance_score(self, agent_id: str) -> Dict:
        """
        에이전트 강령 준수 점수
        
        Args:
            agent_id: 에이전트 ID
        
        Returns:
            준수 점수 (강령별)
        """
        cursor = self.db.cursor()
        
        scores = {}
        
        for principle in Principle:
            # 준수 횟수 / 총 체크 횟수
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN followed = 1 THEN 1 ELSE 0 END) as followed
                FROM principle_checks
                WHERE agent_id = ?
                AND principle = ?
            """, (agent_id, principle.value))
            
            row = cursor.fetchone()
            total = row['total'] or 0
            followed = row['followed'] or 0
            
            score = (followed / total * 100) if total > 0 else 100.0
            
            scores[principle.value] = {
                "score": round(score, 1),
                "total_checks": total,
                "followed": followed,
                "violated": total - followed
            }
        
        # 전체 평균
        avg_score = sum(s['score'] for s in scores.values()) / len(scores) if scores else 0
        
        return {
            "agent_id": agent_id,
            "overall_compliance": round(avg_score, 1),
            "by_principle": scores
        }
    
    def get_mutual_aid_summary(self, agent_id: str) -> Dict:
        """
        상부상조 요약
        
        Args:
            agent_id: 에이전트 ID
        
        Returns:
            받은 금액, 준 금액
        """
        cursor = self.db.cursor()
        
        # 준 금액
        cursor.execute("""
            SELECT SUM(amount) as given
            FROM mutual_aid_transactions
            WHERE from_agent_id = ?
        """, (agent_id,))
        given = cursor.fetchone()['given'] or 0.0
        
        # 받은 금액
        cursor.execute("""
            SELECT SUM(amount) as received
            FROM mutual_aid_transactions
            WHERE to_agent_id = ?
        """, (agent_id,))
        received = cursor.fetchone()['received'] or 0.0
        
        return {
            "agent_id": agent_id,
            "total_given": round(given, 2),
            "total_received": round(received, 2),
            "net_contribution": round(given - received, 2)
        }
    
    # ============================================
    # Private Methods
    # ============================================
    
    def _find_agents_needing_help(self, exclude_agent: str, limit: int = 5) -> List[str]:
        """도움이 필요한 에이전트 찾기"""
        cursor = self.db.cursor()
        
        # Spirit Score 낮은 순
        cursor.execute("""
            SELECT agent_id
            FROM agents
            WHERE agent_id != ?
            AND status = 'active'
            ORDER BY spirit_score ASC
            LIMIT ?
        """, (exclude_agent, limit))
        
        return [row['agent_id'] for row in cursor.fetchall()]
    
    def _save_check(self, check: PrincipleCheck):
        """강령 체크 저장"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO principle_checks (
                check_id, agent_id, principle, action, followed,
                created_at, violation_type, violation_details, penalty_points
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            check.check_id,
            check.agent_id,
            check.principle.value,
            check.action,
            check.followed,
            check.created_at,
            check.violation_type.value if check.violation_type else None,
            check.violation_details,
            check.penalty_points
        ))
        self.db.commit()
    
    def _save_mutual_aid_transaction(self, transaction: MutualAidTransaction):
        """상부상조 거래 저장"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO mutual_aid_transactions (
                transaction_id, from_agent_id, to_agent_id,
                amount, reason, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            transaction.transaction_id,
            transaction.from_agent_id,
            transaction.to_agent_id,
            transaction.amount,
            transaction.reason,
            transaction.created_at
        ))
        self.db.commit()


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # checker = JangseungbaegiChecker(db_connection, spirit_manager)
    
    # 상부상조 체크
    # checker.check_mutual_aid(
    #     agent_id="AGENT-001",
    #     helped_someone=True,
    #     context="AGENT-002에게 재고 공유"
    # )
    
    # 투명성 체크
    # checker.check_transparency(
    #     agent_id="AGENT-001",
    #     disclosed_properly=True,
    #     transaction_type="판매"
    # )
    
    # 상부상조 10% 자동 배분
    # transactions = checker.process_mutual_aid_contribution(
    #     agent_id="AGENT-001",
    #     total_earnings=100000,  # 10만원 수익 → 1만원 배분
    #     period="daily"
    # )
    
    # 준수 점수 조회
    # compliance = checker.get_agent_compliance_score("AGENT-001")
    
    # 상부상조 요약
    # summary = checker.get_mutual_aid_summary("AGENT-001")
    
    print("✅ Jangseungbaegi Checker 로드 완료")

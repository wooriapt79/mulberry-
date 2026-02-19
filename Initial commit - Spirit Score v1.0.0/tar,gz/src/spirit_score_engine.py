"""
Spirit Score Engine - 핵심 로직
CTO Koda

장승배기 정신을 코드로 구현
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
import uuid


class SpiritScoreEngine:
    """
    Spirit Score 계산 및 관리 엔진
    """
    
    # 활동별 점수 규칙
    SCORE_RULES = {
        'daily_login': Decimal('0.01'),
        'mention_response': Decimal('0.02'),
        'code_commit': Decimal('0.03'),
        'pr_review': Decimal('0.02'),
        'bug_report': Decimal('0.03'),
        'important_decision': Decimal('0.05'),
        'meeting_absence': Decimal('-0.01'),
        'mention_no_response_3x': Decimal('-0.02'),
        'documentation': Decimal('0.03'),
    }
    
    # 자동 승인 여부
    AUTO_APPROVE = {
        'daily_login': True,
        'mention_response': True,
        'code_commit': True,
        'pr_review': True,
        'bug_report': False,  # 수동 승인 필요
        'important_decision': False,  # 수동 승인 필요
        'meeting_absence': True,
        'mention_no_response_3x': True,
        'documentation': False,  # 수동 승인 필요
    }
    
    # 상부상조 10% 기금 비율
    MUTUAL_AID_RATE = Decimal('0.10')
    
    # 상부상조 기여 점수 (₩1000당 +0.001)
    MUTUAL_AID_SCORE_PER_1K = Decimal('0.001')
    
    def __init__(self, db_connection):
        """
        Args:
            db_connection: PostgreSQL 연결 객체
        """
        self.db = db_connection
    
    def calculate_score_change(
        self, 
        activity_type: str, 
        context: Optional[Dict] = None
    ) -> Decimal:
        """
        활동 유형에 따른 점수 변화 계산
        
        Args:
            activity_type: 활동 유형
            context: 추가 컨텍스트 (예: 기여 금액)
        
        Returns:
            점수 변화량
        """
        if activity_type == 'mutual_aid_contribution':
            # 상부상조 기여: ₩1000당 +0.001
            amount = Decimal(str(context.get('amount', 0)))
            return (amount / Decimal('1000')) * self.MUTUAL_AID_SCORE_PER_1K
        
        return self.SCORE_RULES.get(activity_type, Decimal('0'))
    
    def record_activity(
        self,
        user_id: str,
        activity_type: str,
        activity_data: Optional[Dict] = None,
        auto_approve: Optional[bool] = None
    ) -> Dict:
        """
        활동 기록 및 점수 업데이트
        
        Args:
            user_id: 사용자 ID
            activity_type: 활동 유형
            activity_data: 활동 상세 정보
            auto_approve: 자동 승인 여부 (None이면 규칙에 따름)
        
        Returns:
            활동 기록 결과
        """
        # 점수 변화 계산
        score_change = self.calculate_score_change(activity_type, activity_data)
        
        # 자동 승인 여부 결정
        if auto_approve is None:
            auto_approve = self.AUTO_APPROVE.get(activity_type, False)
        
        # Activity 기록
        activity_id = str(uuid.uuid4())
        
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO activities (
                activity_id, user_id, activity_type, 
                activity_data, score_change, auto_approved
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING activity_id, created_at
        """, (
            activity_id,
            user_id,
            activity_type,
            json.dumps(activity_data) if activity_data else None,
            float(score_change),
            auto_approve
        ))
        
        result = cursor.fetchone()
        
        # 자동 승인이면 즉시 점수 업데이트
        if auto_approve:
            self._update_user_score(user_id, score_change, activity_id)
        
        self.db.commit()
        
        return {
            'activity_id': result[0],
            'score_change': float(score_change),
            'auto_approved': auto_approve,
            'created_at': result[1]
        }
    
    def _update_user_score(
        self, 
        user_id: str, 
        score_change: Decimal,
        activity_id: Optional[str] = None
    ):
        """
        사용자 Spirit Score 업데이트 (내부 함수)
        
        Args:
            user_id: 사용자 ID
            score_change: 점수 변화량
            activity_id: 관련 활동 ID
        """
        cursor = self.db.cursor()
        
        # 현재 점수 조회
        cursor.execute(
            "SELECT spirit_score FROM users WHERE user_id = %s",
            (user_id,)
        )
        current_score = Decimal(str(cursor.fetchone()[0]))
        
        # 새 점수 계산
        new_score = current_score + score_change
        
        # 점수 업데이트
        cursor.execute("""
            UPDATE users 
            SET spirit_score = %s
            WHERE user_id = %s
        """, (float(new_score), user_id))
        
        # 히스토리 기록 (Trigger가 자동으로 처리하지만 activity_id 연결 위해)
        if activity_id:
            cursor.execute("""
                UPDATE spirit_score_history
                SET activity_id = %s
                WHERE user_id = %s
                  AND created_at = (
                      SELECT MAX(created_at) 
                      FROM spirit_score_history 
                      WHERE user_id = %s
                  )
            """, (activity_id, user_id, user_id))
    
    def approve_manual_activity(
        self, 
        activity_id: str, 
        approved_by: str
    ) -> Dict:
        """
        수동 승인이 필요한 활동 승인
        
        Args:
            activity_id: 활동 ID
            approved_by: 승인자 ID
        
        Returns:
            승인 결과
        """
        cursor = self.db.cursor()
        
        # 활동 정보 조회
        cursor.execute("""
            SELECT user_id, activity_type, score_change, auto_approved
            FROM activities
            WHERE activity_id = %s
        """, (activity_id,))
        
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Activity {activity_id} not found")
        
        user_id, activity_type, score_change, auto_approved = row
        
        if auto_approved:
            return {'message': 'Already approved', 'score_applied': True}
        
        # 승인 처리
        cursor.execute("""
            UPDATE activities
            SET auto_approved = true, approved_by = %s
            WHERE activity_id = %s
        """, (approved_by, activity_id))
        
        # 점수 업데이트
        self._update_user_score(user_id, Decimal(str(score_change)), activity_id)
        
        self.db.commit()
        
        return {
            'message': 'Approved',
            'score_change': float(score_change),
            'score_applied': True
        }
    
    def get_user_score(self, user_id: str) -> Dict:
        """
        사용자 Spirit Score 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            사용자 점수 정보
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT 
                u.username,
                u.display_name,
                u.spirit_score,
                COUNT(a.activity_id) as total_activities,
                SUM(CASE WHEN a.score_change > 0 THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN a.score_change < 0 THEN 1 ELSE 0 END) as negative_count
            FROM users u
            LEFT JOIN activities a ON u.user_id = a.user_id
            WHERE u.user_id = %s
            GROUP BY u.user_id, u.username, u.display_name, u.spirit_score
        """, (user_id,))
        
        row = cursor.fetchone()
        
        return {
            'username': row[0],
            'display_name': row[1],
            'spirit_score': float(row[2]),
            'total_activities': row[3] or 0,
            'positive_activities': row[4] or 0,
            'negative_activities': row[5] or 0
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """
        Spirit Score 리더보드 조회
        
        Args:
            limit: 조회할 인원 수
        
        Returns:
            리더보드 순위 리스트
        """
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT 
                username,
                display_name,
                role,
                spirit_score,
                RANK() OVER (ORDER BY spirit_score DESC) as rank
            FROM users
            ORDER BY spirit_score DESC
            LIMIT %s
        """, (limit,))
        
        return [
            {
                'rank': row[4],
                'username': row[0],
                'display_name': row[1],
                'role': row[2],
                'spirit_score': float(row[3])
            }
            for row in cursor.fetchall()
        ]
    
    def record_mutual_aid(
        self, 
        user_id: str, 
        amount: Decimal,
        contribution_type: str = '10_percent_auto'
    ) -> Dict:
        """
        상부상조 기여 기록
        
        Args:
            user_id: 사용자 ID
            amount: 기여 금액
            contribution_type: 기여 유형
        
        Returns:
            기여 기록 결과
        """
        # Spirit Score 보너스 계산
        score_bonus = (amount / Decimal('1000')) * self.MUTUAL_AID_SCORE_PER_1K
        
        cursor = self.db.cursor()
        
        # 기금 기록
        fund_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO mutual_aid_fund (
                fund_id, user_id, contribution_amount,
                contribution_type, spirit_score_bonus
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING fund_id, created_at
        """, (
            fund_id,
            user_id,
            float(amount),
            contribution_type,
            float(score_bonus)
        ))
        
        result = cursor.fetchone()
        
        # 활동 기록 (자동으로 점수 업데이트됨)
        self.record_activity(
            user_id=user_id,
            activity_type='mutual_aid_contribution',
            activity_data={'amount': float(amount), 'fund_id': fund_id},
            auto_approve=True
        )
        
        self.db.commit()
        
        return {
            'fund_id': result[0],
            'amount': float(amount),
            'score_bonus': float(score_bonus),
            'created_at': result[1]
        }
    
    def check_mention_response_timeout(self, user_id: str) -> bool:
        """
        @호출 무응답 3회 체크
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            패널티 발생 여부
        """
        # 최근 24시간 내 무응답 횟수 확인
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM activities
            WHERE user_id = %s
              AND activity_type = 'mention_no_response'
              AND created_at > NOW() - INTERVAL '24 hours'
        """, (user_id,))
        
        no_response_count = cursor.fetchone()[0]
        
        # 3회 이상이면 패널티
        if no_response_count >= 3:
            self.record_activity(
                user_id=user_id,
                activity_type='mention_no_response_3x',
                activity_data={'count': no_response_count},
                auto_approve=True
            )
            return True
        
        return False


# ============================================
# 사용 예시
# ============================================

import json

if __name__ == "__main__":
    # DB 연결 (예시)
    # import psycopg2
    # conn = psycopg2.connect(...)
    # engine = SpiritScoreEngine(conn)
    
    # 예시 사용법
    print("Spirit Score Engine 초기화 완료")
    print("사용 예시:")
    print("  engine.record_activity(user_id, 'daily_login')")
    print("  engine.get_user_score(user_id)")
    print("  engine.get_leaderboard()")

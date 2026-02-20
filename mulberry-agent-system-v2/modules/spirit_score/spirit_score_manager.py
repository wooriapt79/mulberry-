"""
Mulberry Spirit Score System
CTO Koda

에이전트 모든 활동을 Spirit Score로 자동 변환
"""

from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
import json


class SpiritScoreEvent(str, Enum):
    """Spirit Score 이벤트 종류"""
    # 긍정적 활동
    TASK_COMPLETED = "task_completed"                  # 업무 완료 +0.01
    CUSTOMER_SERVED = "customer_served"                # 고객 응대 +0.005
    POSITIVE_REVIEW = "positive_review"                # 긍정 리뷰 +0.02
    HELP_OTHER_AGENT = "help_other_agent"              # 다른 에이전트 도움 +0.03
    MEETING_ATTENDED = "meeting_attended"              # 회의 참석 +0.01
    TRAINING_COMPLETED = "training_completed"          # 교육 이수 +0.05
    CONSTITUTION_FOLLOWED = "constitution_followed"    # 헌법 준수 +0.01
    MUTUAL_AID_GIVEN = "mutual_aid_given"             # 상부상조 제공 +0.05
    
    # 부정적 활동
    TASK_FAILED = "task_failed"                       # 업무 실패 -0.02
    NEGATIVE_REVIEW = "negative_review"               # 부정 리뷰 -0.03
    CONSTITUTION_VIOLATED = "constitution_violated"    # 헌법 위반 -0.1
    MEETING_ABSENT = "meeting_absent"                 # 회의 불참 -0.02
    HELP_REFUSED = "help_refused"                     # 도움 거부 -0.05


class SpiritLevel(str, Enum):
    """Spirit 레벨"""
    NOVICE = "novice"           # 0-20
    APPRENTICE = "apprentice"   # 21-40
    SKILLED = "skilled"         # 41-60
    EXPERT = "expert"           # 61-80
    MASTER = "master"           # 81-100


class SpiritScoreRecord:
    """Spirit Score 기록"""
    
    def __init__(
        self,
        record_id: str,
        agent_id: str,
        event_type: SpiritScoreEvent,
        points: float,
        reason: str
    ):
        self.record_id = record_id
        self.agent_id = agent_id
        self.event_type = event_type
        self.points = points
        self.reason = reason
        self.created_at = datetime.now()
        
        # 추가 정보
        self.related_entity: Optional[str] = None  # 관련 고객, 에이전트 등
        self.metadata: Dict = {}
    
    def to_dict(self) -> Dict:
        return {
            "record_id": self.record_id,
            "agent_id": self.agent_id,
            "event_type": self.event_type.value,
            "points": self.points,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
            "related_entity": self.related_entity,
            "metadata": self.metadata
        }


class SpiritScoreManager:
    """
    Spirit Score 관리자
    
    에이전트의 모든 활동을 Spirit Score로 변환하고 관리
    """
    
    # 이벤트별 점수 매핑
    EVENT_POINTS = {
        SpiritScoreEvent.TASK_COMPLETED: 0.01,
        SpiritScoreEvent.CUSTOMER_SERVED: 0.005,
        SpiritScoreEvent.POSITIVE_REVIEW: 0.02,
        SpiritScoreEvent.HELP_OTHER_AGENT: 0.03,
        SpiritScoreEvent.MEETING_ATTENDED: 0.01,
        SpiritScoreEvent.TRAINING_COMPLETED: 0.05,
        SpiritScoreEvent.CONSTITUTION_FOLLOWED: 0.01,
        SpiritScoreEvent.MUTUAL_AID_GIVEN: 0.05,
        
        SpiritScoreEvent.TASK_FAILED: -0.02,
        SpiritScoreEvent.NEGATIVE_REVIEW: -0.03,
        SpiritScoreEvent.CONSTITUTION_VIOLATED: -0.1,
        SpiritScoreEvent.MEETING_ABSENT: -0.02,
        SpiritScoreEvent.HELP_REFUSED: -0.05,
    }
    
    def __init__(self, db_connection):
        """
        Args:
            db_connection: 데이터베이스 연결
        """
        self.db = db_connection
    
    def record_event(
        self,
        agent_id: str,
        event_type: SpiritScoreEvent,
        reason: str,
        related_entity: Optional[str] = None,
        metadata: Optional[Dict] = None,
        points_override: Optional[float] = None
    ) -> SpiritScoreRecord:
        """
        이벤트 기록 및 점수 부여
        
        Args:
            agent_id: 에이전트 ID
            event_type: 이벤트 종류
            reason: 사유
            related_entity: 관련 엔티티 (고객, 다른 에이전트 등)
            metadata: 추가 메타데이터
            points_override: 점수 오버라이드 (특수한 경우)
        
        Returns:
            생성된 기록
        """
        # 점수 계산
        points = points_override if points_override is not None else self.EVENT_POINTS[event_type]
        
        # 기록 ID 생성
        record_id = f"SPIRIT-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # 기록 생성
        record = SpiritScoreRecord(
            record_id=record_id,
            agent_id=agent_id,
            event_type=event_type,
            points=points,
            reason=reason
        )
        
        if related_entity:
            record.related_entity = related_entity
        if metadata:
            record.metadata = metadata
        
        # 데이터베이스 저장
        self._save_record(record)
        
        # 에이전트 총점 업데이트
        self._update_agent_score(agent_id, points)
        
        print(f"✅ Spirit Score 기록: {agent_id}")
        print(f"   이벤트: {event_type.value}")
        print(f"   점수: {points:+.3f}")
        print(f"   사유: {reason}")
        
        return record
    
    def get_agent_score(self, agent_id: str) -> Dict:
        """
        에이전트 현재 점수 조회
        
        Args:
            agent_id: 에이전트 ID
        
        Returns:
            점수 정보
        """
        cursor = self.db.cursor()
        
        # 총점 조회
        cursor.execute("""
            SELECT SUM(points) as total_score,
                   COUNT(*) as total_events
            FROM spirit_scores
            WHERE agent_id = ?
        """, (agent_id,))
        
        row = cursor.fetchone()
        total_score = row['total_score'] or 0.0
        total_events = row['total_events'] or 0
        
        # 레벨 계산
        level = self._calculate_level(total_score)
        
        # 다음 레벨까지 필요한 점수
        next_level_score = self._get_next_level_threshold(level)
        
        return {
            "agent_id": agent_id,
            "total_score": round(total_score, 3),
            "total_events": total_events,
            "level": level.value,
            "next_level_score": next_level_score,
            "progress_to_next": self._calculate_progress(total_score, level)
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """
        Spirit Score 리더보드
        
        Args:
            limit: 상위 N명
        
        Returns:
            리더보드
        """
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT 
                agent_id,
                SUM(points) as total_score,
                COUNT(*) as total_events
            FROM spirit_scores
            GROUP BY agent_id
            ORDER BY total_score DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        
        leaderboard = []
        for rank, row in enumerate(rows, start=1):
            score = row['total_score']
            level = self._calculate_level(score)
            
            leaderboard.append({
                "rank": rank,
                "agent_id": row['agent_id'],
                "total_score": round(score, 3),
                "total_events": row['total_events'],
                "level": level.value
            })
        
        return leaderboard
    
    def get_recent_activities(self, agent_id: str, limit: int = 20) -> List[Dict]:
        """
        최근 활동 내역
        
        Args:
            agent_id: 에이전트 ID
            limit: 개수
        
        Returns:
            활동 내역
        """
        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT *
            FROM spirit_scores
            WHERE agent_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (agent_id, limit))
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    # ============================================
    # 자동 통합 헬퍼 메서드
    # ============================================
    
    def on_task_completed(self, agent_id: str, task_description: str):
        """업무 완료 시 자동 호출"""
        self.record_event(
            agent_id=agent_id,
            event_type=SpiritScoreEvent.TASK_COMPLETED,
            reason=f"업무 완료: {task_description}"
        )
    
    def on_customer_served(self, agent_id: str, customer_id: str):
        """고객 응대 시 자동 호출"""
        self.record_event(
            agent_id=agent_id,
            event_type=SpiritScoreEvent.CUSTOMER_SERVED,
            reason=f"고객 응대 완료",
            related_entity=customer_id
        )
    
    def on_review_received(self, agent_id: str, rating: int, review_text: str):
        """리뷰 수신 시 자동 호출"""
        if rating >= 4:
            event_type = SpiritScoreEvent.POSITIVE_REVIEW
            reason = f"긍정 리뷰 ({rating}★): {review_text[:50]}"
        else:
            event_type = SpiritScoreEvent.NEGATIVE_REVIEW
            reason = f"부정 리뷰 ({rating}★): {review_text[:50]}"
        
        self.record_event(
            agent_id=agent_id,
            event_type=event_type,
            reason=reason,
            metadata={"rating": rating, "review": review_text}
        )
    
    def on_help_provided(self, helper_agent_id: str, helped_agent_id: str, help_type: str):
        """다른 에이전트 도움 시 자동 호출"""
        self.record_event(
            agent_id=helper_agent_id,
            event_type=SpiritScoreEvent.HELP_OTHER_AGENT,
            reason=f"에이전트 {helped_agent_id} 도움: {help_type}",
            related_entity=helped_agent_id
        )
    
    def on_meeting_attended(self, agent_id: str, meeting_id: str):
        """회의 참석 시 자동 호출"""
        self.record_event(
            agent_id=agent_id,
            event_type=SpiritScoreEvent.MEETING_ATTENDED,
            reason=f"회의 참석: {meeting_id}",
            related_entity=meeting_id
        )
    
    def on_constitution_check(self, agent_id: str, followed: bool, principle: str):
        """헌법 준수 체크 시 자동 호출"""
        if followed:
            event_type = SpiritScoreEvent.CONSTITUTION_FOLLOWED
            reason = f"장승배기 헌법 준수: {principle}"
        else:
            event_type = SpiritScoreEvent.CONSTITUTION_VIOLATED
            reason = f"장승배기 헌법 위반: {principle}"
        
        self.record_event(
            agent_id=agent_id,
            event_type=event_type,
            reason=reason,
            metadata={"principle": principle}
        )
    
    # ============================================
    # Private Methods
    # ============================================
    
    def _calculate_level(self, score: float) -> SpiritLevel:
        """점수로 레벨 계산"""
        if score < 21:
            return SpiritLevel.NOVICE
        elif score < 41:
            return SpiritLevel.APPRENTICE
        elif score < 61:
            return SpiritLevel.SKILLED
        elif score < 81:
            return SpiritLevel.EXPERT
        else:
            return SpiritLevel.MASTER
    
    def _get_next_level_threshold(self, current_level: SpiritLevel) -> Optional[float]:
        """다음 레벨 문턱값"""
        thresholds = {
            SpiritLevel.NOVICE: 21.0,
            SpiritLevel.APPRENTICE: 41.0,
            SpiritLevel.SKILLED: 61.0,
            SpiritLevel.EXPERT: 81.0,
            SpiritLevel.MASTER: None  # 최고 레벨
        }
        return thresholds[current_level]
    
    def _calculate_progress(self, score: float, level: SpiritLevel) -> float:
        """다음 레벨까지 진행도 (0.0 ~ 1.0)"""
        ranges = {
            SpiritLevel.NOVICE: (0, 20),
            SpiritLevel.APPRENTICE: (21, 40),
            SpiritLevel.SKILLED: (41, 60),
            SpiritLevel.EXPERT: (61, 80),
            SpiritLevel.MASTER: (81, 100)
        }
        
        min_score, max_score = ranges[level]
        
        if level == SpiritLevel.MASTER:
            return 1.0 if score >= 100 else (score - min_score) / (max_score - min_score)
        
        return (score - min_score) / (max_score - min_score)
    
    def _save_record(self, record: SpiritScoreRecord):
        """기록 저장"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO spirit_scores (
                record_id, agent_id, event_type, points, reason,
                created_at, related_entity, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.record_id,
            record.agent_id,
            record.event_type.value,
            record.points,
            record.reason,
            record.created_at,
            record.related_entity,
            json.dumps(record.metadata) if record.metadata else None
        ))
        self.db.commit()
    
    def _update_agent_score(self, agent_id: str, points: float):
        """에이전트 총점 업데이트 (캐시)"""
        # agents 테이블의 spirit_score 컬럼 업데이트
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE agents
            SET spirit_score = COALESCE(spirit_score, 0) + ?
            WHERE agent_id = ?
        """, (points, agent_id))
        self.db.commit()


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # manager = SpiritScoreManager(db_connection)
    
    # 업무 완료
    # manager.on_task_completed("AGENT-001", "김밥 10줄 판매")
    
    # 고객 응대
    # manager.on_customer_served("AGENT-001", "CUSTOMER-123")
    
    # 리뷰 수신
    # manager.on_review_received("AGENT-001", 5, "정말 맛있어요!")
    
    # 다른 에이전트 도움
    # manager.on_help_provided("AGENT-001", "AGENT-002", "재고 공유")
    
    # 현재 점수 조회
    # score_info = manager.get_agent_score("AGENT-001")
    # print(f"총점: {score_info['total_score']}")
    # print(f"레벨: {score_info['level']}")
    
    # 리더보드
    # leaderboard = manager.get_leaderboard(10)
    
    print("✅ Spirit Score Manager 로드 완료")

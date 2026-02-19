"""
Activity Tracker - 활동 감지 시스템
CTO Koda

다양한 소스에서 팀원 활동을 자동 감지하고 기록
"""

from typing import Dict, Optional, Callable
from datetime import datetime, timedelta
import asyncio
import hashlib


class ActivityTracker:
    """
    팀원 활동 자동 감지 및 추적
    """
    
    def __init__(self, spirit_engine):
        """
        Args:
            spirit_engine: SpiritScoreEngine 인스턴스
        """
        self.engine = spirit_engine
        self.activity_cache = {}  # 중복 방지용 캐시
        self.mention_tracking = {}  # @호출 추적
    
    def _generate_activity_hash(
        self, 
        user_id: str, 
        activity_type: str, 
        timestamp: datetime
    ) -> str:
        """
        활동 중복 체크용 해시 생성
        """
        content = f"{user_id}_{activity_type}_{timestamp.strftime('%Y%m%d%H')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_duplicate(self, activity_hash: str) -> bool:
        """
        중복 활동인지 체크
        """
        if activity_hash in self.activity_cache:
            return True
        
        self.activity_cache[activity_hash] = datetime.now()
        return False
    
    def _cleanup_cache(self):
        """
        오래된 캐시 정리 (24시간 이상)
        """
        cutoff = datetime.now() - timedelta(hours=24)
        self.activity_cache = {
            k: v for k, v in self.activity_cache.items()
            if v > cutoff
        }
    
    # ============================================
    # 로그인 활동 추적
    # ============================================
    
    def track_login(self, user_id: str) -> Optional[Dict]:
        """
        일일 로그인 추적
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            활동 기록 결과 (중복이면 None)
        """
        activity_hash = self._generate_activity_hash(
            user_id, 'daily_login', datetime.now()
        )
        
        if self._is_duplicate(activity_hash):
            return None  # 오늘 이미 로그인 기록됨
        
        return self.engine.record_activity(
            user_id=user_id,
            activity_type='daily_login',
            activity_data={'timestamp': datetime.now().isoformat()}
        )
    
    # ============================================
    # @호출 응답 추적
    # ============================================
    
    def track_mention(
        self, 
        mentioned_user_id: str, 
        mention_id: str,
        mentioned_by: str,
        channel: str
    ):
        """
        @호출 기록
        
        Args:
            mentioned_user_id: 호출된 사용자
            mention_id: 호출 ID (메시지 ID 등)
            mentioned_by: 호출한 사람
            channel: 채널
        """
        self.mention_tracking[mention_id] = {
            'mentioned_user': mentioned_user_id,
            'mentioned_by': mentioned_by,
            'channel': channel,
            'timestamp': datetime.now(),
            'responded': False
        }
    
    def track_mention_response(
        self, 
        user_id: str, 
        mention_id: str
    ) -> Optional[Dict]:
        """
        @호출 응답 추적
        
        Args:
            user_id: 응답한 사용자
            mention_id: 호출 ID
        
        Returns:
            활동 기록 결과
        """
        if mention_id not in self.mention_tracking:
            return None
        
        mention = self.mention_tracking[mention_id]
        
        if mention['mentioned_user'] != user_id:
            return None  # 다른 사람의 호출
        
        if mention['responded']:
            return None  # 이미 응답함
        
        # 응답 기록
        mention['responded'] = True
        mention['response_time'] = datetime.now()
        
        # 응답 시간 계산 (분)
        response_duration = (
            mention['response_time'] - mention['timestamp']
        ).total_seconds() / 60
        
        return self.engine.record_activity(
            user_id=user_id,
            activity_type='mention_response',
            activity_data={
                'mention_id': mention_id,
                'response_time_minutes': response_duration,
                'mentioned_by': mention['mentioned_by']
            }
        )
    
    def check_mention_timeouts(self):
        """
        @호출 무응답 체크 (30분 타임아웃)
        """
        timeout_threshold = datetime.now() - timedelta(minutes=30)
        
        for mention_id, mention in list(self.mention_tracking.items()):
            if not mention['responded'] and mention['timestamp'] < timeout_threshold:
                # 무응답 기록
                self.engine.record_activity(
                    user_id=mention['mentioned_user'],
                    activity_type='mention_no_response',
                    activity_data={
                        'mention_id': mention_id,
                        'mentioned_by': mention['mentioned_by']
                    }
                )
                
                # 3회 무응답 체크
                self.engine.check_mention_response_timeout(
                    mention['mentioned_user']
                )
                
                # 추적 제거
                del self.mention_tracking[mention_id]
    
    # ============================================
    # GitHub 활동 추적
    # ============================================
    
    def track_github_commit(
        self, 
        user_id: str, 
        commit_sha: str,
        repo: str,
        approved: bool = False
    ) -> Optional[Dict]:
        """
        GitHub 커밋 추적
        
        Args:
            user_id: 사용자 ID
            commit_sha: 커밋 해시
            repo: 저장소
            approved: PR 승인 여부
        
        Returns:
            활동 기록 결과
        """
        activity_hash = f"{user_id}_{commit_sha}"
        
        if self._is_duplicate(activity_hash):
            return None
        
        # 승인된 커밋만 점수 부여
        if not approved:
            return None
        
        return self.engine.record_activity(
            user_id=user_id,
            activity_type='code_commit',
            activity_data={
                'commit_sha': commit_sha,
                'repo': repo,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def track_pr_review(
        self, 
        reviewer_id: str, 
        pr_number: int,
        repo: str,
        review_state: str
    ) -> Optional[Dict]:
        """
        PR 리뷰 추적
        
        Args:
            reviewer_id: 리뷰어 ID
            pr_number: PR 번호
            repo: 저장소
            review_state: 리뷰 상태 (approved, changes_requested, commented)
        
        Returns:
            활동 기록 결과
        """
        activity_hash = f"{reviewer_id}_pr_{pr_number}"
        
        if self._is_duplicate(activity_hash):
            return None
        
        # approved나 changes_requested만 점수 부여
        if review_state not in ['approved', 'changes_requested']:
            return None
        
        return self.engine.record_activity(
            user_id=reviewer_id,
            activity_type='pr_review',
            activity_data={
                'pr_number': pr_number,
                'repo': repo,
                'review_state': review_state,
                'timestamp': datetime.now().isoformat()
            }
        )
    
    # ============================================
    # 회의 참석 추적
    # ============================================
    
    def track_meeting_attendance(
        self, 
        meeting_id: str,
        meeting_name: str,
        attendees: list,
        all_members: list
    ):
        """
        회의 참석 추적
        
        Args:
            meeting_id: 회의 ID
            meeting_name: 회의 이름
            attendees: 참석자 리스트
            all_members: 전체 팀원 리스트
        """
        cursor = self.engine.db.cursor()
        
        # 참석자 기록
        for user_id in attendees:
            cursor.execute("""
                INSERT INTO meeting_attendance (
                    meeting_id, meeting_name, user_id, attended
                ) VALUES (%s, %s, %s, true)
            """, (meeting_id, meeting_name, user_id))
        
        # 불참자 기록 및 점수 차감
        absent_members = set(all_members) - set(attendees)
        for user_id in absent_members:
            cursor.execute("""
                INSERT INTO meeting_attendance (
                    meeting_id, meeting_name, user_id, attended
                ) VALUES (%s, %s, %s, false)
            """, (meeting_id, meeting_name, user_id))
            
            # 불참 점수 차감
            self.engine.record_activity(
                user_id=user_id,
                activity_type='meeting_absence',
                activity_data={
                    'meeting_id': meeting_id,
                    'meeting_name': meeting_name
                }
            )
        
        self.engine.db.commit()
    
    # ============================================
    # 상부상조 자동 추적
    # ============================================
    
    def track_revenue_contribution(
        self, 
        user_id: str, 
        revenue: float
    ) -> Dict:
        """
        수익 발생 시 자동 10% 상부상조 기금 기록
        
        Args:
            user_id: 사용자 ID
            revenue: 수익 금액
        
        Returns:
            기여 기록 결과
        """
        from decimal import Decimal
        
        contribution_amount = Decimal(str(revenue)) * Decimal('0.10')
        
        return self.engine.record_mutual_aid(
            user_id=user_id,
            amount=contribution_amount,
            contribution_type='10_percent_auto'
        )
    
    # ============================================
    # 주기적 작업
    # ============================================
    
    async def periodic_tasks(self):
        """
        주기적으로 실행할 작업들
        """
        while True:
            # 30분마다 실행
            await asyncio.sleep(1800)
            
            # @호출 타임아웃 체크
            self.check_mention_timeouts()
            
            # 캐시 정리
            self._cleanup_cache()


# ============================================
# GitHub Webhook 연동 예시
# ============================================

class GitHubWebhookHandler:
    """
    GitHub Webhook 이벤트 처리
    """
    
    def __init__(self, activity_tracker: ActivityTracker):
        self.tracker = activity_tracker
        self.user_github_mapping = {}  # GitHub username → user_id 매핑
    
    def handle_push_event(self, payload: Dict):
        """
        Push 이벤트 처리
        """
        commits = payload.get('commits', [])
        repo = payload['repository']['name']
        
        for commit in commits:
            github_user = commit['author']['username']
            user_id = self.user_github_mapping.get(github_user)
            
            if user_id:
                self.tracker.track_github_commit(
                    user_id=user_id,
                    commit_sha=commit['id'],
                    repo=repo,
                    approved=True  # Push는 이미 승인된 것으로 간주
                )
    
    def handle_pull_request_review(self, payload: Dict):
        """
        PR 리뷰 이벤트 처리
        """
        review = payload.get('review', {})
        pr = payload.get('pull_request', {})
        
        github_user = review['user']['login']
        user_id = self.user_github_mapping.get(github_user)
        
        if user_id:
            self.tracker.track_pr_review(
                reviewer_id=user_id,
                pr_number=pr['number'],
                repo=payload['repository']['name'],
                review_state=review['state']
            )


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    print("Activity Tracker 초기화 완료")
    print("지원 활동:")
    print("  - 일일 로그인")
    print("  - @호출 응답/무응답")
    print("  - GitHub 커밋")
    print("  - PR 리뷰")
    print("  - 회의 참석/불참")
    print("  - 상부상조 자동 기여")

"""
Mulberry Mastodon 통합 - 시작 코드
CTO Koda

ActivityPub 기반 협업 시스템
"""

from mastodon import Mastodon
import os
from datetime import datetime


class MulberryMastodon:
    """
    Mastodon 기반 Mulberry 협업 시스템
    """
    
    def __init__(self, 
                 client_id: str,
                 client_secret: str,
                 access_token: str,
                 api_base_url: str = 'https://mastodon.social'):
        """
        Args:
            client_id: Mastodon 클라이언트 ID
            client_secret: Mastodon 클라이언트 비밀키
            access_token: 액세스 토큰
            api_base_url: Mastodon 인스턴스 URL
        """
        self.mastodon = Mastodon(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            api_base_url=api_base_url
        )
    
    def post_toot(self, message: str, visibility: str = 'public'):
        """
        Toot 작성
        
        Args:
            message: 메시지 내용
            visibility: 'public', 'unlisted', 'private', 'direct'
        
        Returns:
            Toot 정보
        """
        return self.mastodon.toot(message, visibility=visibility)
    
    def reply_to_mention(self, notification_id: str, message: str):
        """
        Mention에 답장
        
        Args:
            notification_id: 알림 ID
            message: 답장 내용
        """
        notification = self.mastodon.notifications(id=notification_id)
        status_id = notification['status']['id']
        
        return self.mastodon.status_reply(
            to_status=status_id,
            status=message
        )
    
    def get_mentions(self, limit: int = 20):
        """
        최근 Mention 조회
        
        Args:
            limit: 조회할 개수
        
        Returns:
            Mention 리스트
        """
        notifications = self.mastodon.notifications(limit=limit)
        
        mentions = [
            notif for notif in notifications
            if notif['type'] == 'mention'
        ]
        
        return mentions
    
    def boost_status(self, status_id: str):
        """
        Status Boost (리트윗)
        
        Args:
            status_id: Status ID
        """
        return self.mastodon.status_reblog(status_id)
    
    def follow_user(self, account_id: str):
        """
        사용자 팔로우
        
        Args:
            account_id: 계정 ID
        """
        return self.mastodon.account_follow(account_id)


# ============================================
# Spirit Score Bot
# ============================================

class SpiritScoreBot(MulberryMastodon):
    """
    Spirit Score 알림 Bot
    """
    
    def post_daily_leaderboard(self, leaderboard: list):
        """
        일일 리더보드 공유
        
        Args:
            leaderboard: 리더보드 데이터
        """
        message = "🌾 오늘의 Spirit Score 리더보드!\n\n"
        
        for i, user in enumerate(leaderboard[:10], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            message += f"{emoji} {i}위. @{user['username']}: {user['score']:.2f}\n"
        
        message += "\n#MulberryTeam #SpiritScore #장승배기"
        
        return self.post_toot(message)
    
    def notify_score_change(self, username: str, old_score: float, 
                           new_score: float, activity: str):
        """
        점수 변경 알림
        
        Args:
            username: 사용자 이름
            old_score: 이전 점수
            new_score: 새 점수
            activity: 활동 유형
        """
        change = new_score - old_score
        emoji = "📈" if change > 0 else "📉"
        
        message = (
            f"{emoji} @{username}님의 Spirit Score가 변경되었습니다!\n\n"
            f"활동: {activity}\n"
            f"변화: {change:+.2f}\n"
            f"현재 점수: {new_score:.2f}\n\n"
            f"#SpiritScore"
        )
        
        return self.post_toot(message, visibility='unlisted')
    
    def notify_mutual_aid(self, username: str, amount: float, bonus: float):
        """
        상부상조 기여 알림
        
        Args:
            username: 사용자 이름
            amount: 기여 금액
            bonus: 점수 보너스
        """
        message = (
            f"💙 @{username}님이 상부상조 기금에 기여하셨습니다!\n\n"
            f"기여 금액: ₩{amount:,.0f}\n"
            f"Spirit Score 보너스: +{bonus:.3f}\n\n"
            f"감사합니다! 🌾\n\n"
            f"#상부상조 #MulberryTeam"
        )
        
        return self.post_toot(message)


# ============================================
# CTO Koda Bot
# ============================================

class CTOKodaBot(MulberryMastodon):
    """
    CTO Koda AI 에이전트
    """
    
    def announce_completion(self, project: str, details: str):
        """
        작업 완료 공지
        
        Args:
            project: 프로젝트 이름
            details: 상세 내용
        """
        message = (
            f"✅ {project} 완료!\n\n"
            f"{details}\n\n"
            f"- CTO Koda 🌾\n\n"
            f"#개발완료 #MulberryTeam"
        )
        
        return self.post_toot(message)
    
    def share_tech_update(self, title: str, content: str, tags: list = None):
        """
        기술 업데이트 공유
        
        Args:
            title: 제목
            content: 내용
            tags: 해시태그 리스트
        """
        message = f"🔧 {title}\n\n{content}\n\n- CTO Koda"
        
        if tags:
            message += "\n\n" + " ".join(f"#{tag}" for tag in tags)
        
        return self.post_toot(message)


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # 환경 변수에서 읽기
    CLIENT_ID = os.getenv('MASTODON_CLIENT_ID')
    CLIENT_SECRET = os.getenv('MASTODON_CLIENT_SECRET')
    ACCESS_TOKEN = os.getenv('MASTODON_ACCESS_TOKEN')
    
    # Spirit Score Bot 초기화
    spirit_bot = SpiritScoreBot(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        access_token=ACCESS_TOKEN
    )
    
    # 예시: 리더보드 공유
    leaderboard = [
        {'username': 're_eul', 'score': 0.85},
        {'username': 'pm_mulberry', 'score': 0.78},
        {'username': 'koda_mulberry', 'score': 0.75},
    ]
    
    # spirit_bot.post_daily_leaderboard(leaderboard)
    
    # CTO Koda Bot 초기화
    koda_bot = CTOKodaBot(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        access_token=ACCESS_TOKEN
    )
    
    # 예시: 작업 완료 공지
    # koda_bot.announce_completion(
    #     project="Spirit Score 자동화 시스템",
    #     details="장승배기 정신을 코드로 구현한 완전 자동화 시스템 구축 완료!"
    # )
    
    print("✅ Mastodon 통합 준비 완료!")
    print("환경 변수 설정 후 주석을 해제하고 실행하세요.")

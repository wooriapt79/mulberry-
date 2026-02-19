"""
Mulberry Mastodon Bot System
CTO Koda

3개 Bot 통합 관리 시스템
"""

from mastodon import Mastodon
import os
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv('.env.mastodon')


class MulberryBotSystem:
    """
    3개 Bot 통합 관리
    """
    
    def __init__(self):
        """Initialize all 3 bots"""
        self.instance_url = os.getenv('MASTODON_INSTANCE', 'https://mastodon.social')
        
        # CEO Bot
        self.ceo_bot = Mastodon(
            client_id=os.getenv('CEO_BOT_CLIENT_ID'),
            client_secret=os.getenv('CEO_BOT_CLIENT_SECRET'),
            access_token=os.getenv('CEO_BOT_ACCESS_TOKEN'),
            api_base_url=self.instance_url
        )
        
        # PM Bot
        self.pm_bot = Mastodon(
            client_id=os.getenv('PM_BOT_CLIENT_ID'),
            client_secret=os.getenv('PM_BOT_CLIENT_SECRET'),
            access_token=os.getenv('PM_BOT_ACCESS_TOKEN'),
            api_base_url=self.instance_url
        )
        
        # Spirit Score Bot
        self.spirit_bot = Mastodon(
            client_id=os.getenv('SPIRIT_BOT_CLIENT_ID'),
            client_secret=os.getenv('SPIRIT_BOT_CLIENT_SECRET'),
            access_token=os.getenv('SPIRIT_BOT_ACCESS_TOKEN'),
            api_base_url=self.instance_url
        )
        
        print("✅ Mulberry Bot System 초기화 완료!")
        print(f"   Instance: {self.instance_url}")
        print(f"   Bots: CEO, PM, Spirit Score")
    
    # ============================================
    # CEO Bot Functions
    # ============================================
    
    def ceo_announce(self, message: str, visibility: str = 'public'):
        """
        CEO Bot 공지
        
        Args:
            message: 공지 내용
            visibility: 'public', 'unlisted', 'private', 'direct'
        """
        full_message = f"🌾 CEO 공지\n\n{message}\n\n#MulberryTeam #CEO"
        return self.ceo_bot.toot(full_message, visibility=visibility)
    
    def ceo_weekly_message(self):
        """CEO 주간 메시지"""
        message = """🌾 Mulberry Team에게

이번 주도 모두 수고 많으셨습니다!

우리의 목표:
✅ 장승배기 정신 실천
✅ 투명한 협업
✅ 상부상조

함께 달려가 봅시다! 💪

#MulberryTeam #장승배기"""
        
        return self.ceo_bot.toot(message)
    
    # ============================================
    # PM Bot Functions
    # ============================================
    
    def pm_daily_standup(self, tasks: list):
        """
        PM Bot 일일 스탠드업
        
        Args:
            tasks: 작업 리스트 ['Task 1', 'Task 2', ...]
        """
        message = "📋 Today's Plan\n\n"
        
        for i, task in enumerate(tasks, 1):
            message += f"{i}. {task}\n"
        
        message += "\n@re_eul @ceo_mulberry @spirit_mulberry\n"
        message += "#DailyStandup #MulberryTeam"
        
        return self.pm_bot.toot(message)
    
    def pm_weekly_plan(self, week_goals: list):
        """
        PM Bot 주간 계획
        
        Args:
            week_goals: 주간 목표 리스트
        """
        message = "📋 Weekly Plan\n\n"
        
        for goal in week_goals:
            message += f"□ {goal}\n"
        
        message += "\n#WeeklyPlan #MulberryTeam"
        
        return self.pm_bot.toot(message)
    
    # ============================================
    # Spirit Score Bot Functions
    # ============================================
    
    def spirit_post_leaderboard(self, leaderboard: list):
        """
        Spirit Score 리더보드 공유
        
        Args:
            leaderboard: [{'username': 're_eul', 'score': 0.85}, ...]
        """
        message = "🌾 Spirit Score 리더보드\n\n"
        
        for i, user in enumerate(leaderboard[:5], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            message += f"{emoji} {i}위. @{user['username']}: {user['score']:.2f}\n"
        
        message += "\n모두 수고하셨습니다! 💙\n"
        message += "#SpiritScore #Leaderboard"
        
        return self.spirit_bot.toot(message)
    
    def spirit_score_update(self, username: str, old_score: float, 
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
        
        message = f"""{emoji} Spirit Score 업데이트

@{username}님
활동: {activity}
변화: {change:+.2f}
현재: {new_score:.2f}

#SpiritScore"""
        
        return self.spirit_bot.toot(message, visibility='unlisted')
    
    def spirit_mutual_aid(self, username: str, amount: float):
        """
        상부상조 기여 알림
        
        Args:
            username: 사용자 이름
            amount: 기여 금액
        """
        bonus = (amount / 1000) * 0.001
        
        message = f"""💙 상부상조 기여

@{username}님이 기여하셨습니다!

기여: ₩{amount:,.0f}
Spirit Score: +{bonus:.3f}

감사합니다! 🌾

#상부상조 #MulberryTeam"""
        
        return self.spirit_bot.toot(message)
    
    # ============================================
    # Team Functions (모든 Bot 활용)
    # ============================================
    
    def team_morning_routine(self):
        """
        아침 루틴 (CEO → PM → Spirit 순서)
        """
        results = []
        
        # 1. CEO 인사
        ceo_msg = self.ceo_bot.toot(
            "🌾 좋은 아침입니다, Mulberry Team!\n"
            "오늘도 힘차게 시작해봅시다! 💪\n\n"
            "@re_eul @pm_mulberry @spirit_mulberry\n"
            "#GoodMorning #MulberryTeam"
        )
        results.append(('CEO', ceo_msg))
        
        # 2. PM 오늘의 계획
        pm_msg = self.pm_bot.toot(
            "📋 오늘의 Focus\n\n"
            "1. Mastodon Bot 시스템 테스트\n"
            "2. Spirit Score 연동\n"
            "3. 자동화 검증\n\n"
            "#DailyPlan"
        )
        results.append(('PM', pm_msg))
        
        # 3. Spirit 어제의 리더보드
        spirit_msg = self.spirit_bot.toot(
            "🌾 어제의 Spirit Score\n\n"
            "🥇 1위. @re_eul: 0.85\n"
            "🥈 2위. @ceo_mulberry: 0.80\n"
            "🥉 3위. @pm_mulberry: 0.75\n\n"
            "오늘도 화이팅! 💙\n"
            "#SpiritScore"
        )
        results.append(('Spirit', spirit_msg))
        
        return results
    
    def test_all_bots(self):
        """
        모든 Bot 테스트
        """
        print("\n" + "="*50)
        print("🤖 Mulberry Bot System Test")
        print("="*50 + "\n")
        
        tests = []
        
        # CEO Bot 테스트
        try:
            ceo_test = self.ceo_bot.toot(
                "🌾 CEO Bot 테스트\n"
                "시스템 정상 작동 중!\n\n"
                "#BotTest #CEO"
            )
            print("✅ CEO Bot: OK")
            tests.append(('CEO', True, ceo_test))
        except Exception as e:
            print(f"❌ CEO Bot: FAIL - {e}")
            tests.append(('CEO', False, str(e)))
        
        # PM Bot 테스트
        try:
            pm_test = self.pm_bot.toot(
                "📋 PM Bot 테스트\n"
                "프로젝트 관리 준비 완료!\n\n"
                "#BotTest #PM"
            )
            print("✅ PM Bot: OK")
            tests.append(('PM', True, pm_test))
        except Exception as e:
            print(f"❌ PM Bot: FAIL - {e}")
            tests.append(('PM', False, str(e)))
        
        # Spirit Bot 테스트
        try:
            spirit_test = self.spirit_bot.toot(
                "🌾 Spirit Score Bot 테스트\n"
                "점수 관리 시스템 가동!\n\n"
                "#BotTest #SpiritScore"
            )
            print("✅ Spirit Bot: OK")
            tests.append(('Spirit', True, spirit_test))
        except Exception as e:
            print(f"❌ Spirit Bot: FAIL - {e}")
            tests.append(('Spirit', False, str(e)))
        
        print("\n" + "="*50)
        success_count = sum(1 for _, success, _ in tests if success)
        print(f"결과: {success_count}/3 성공")
        print("="*50 + "\n")
        
        return tests
    
    def get_all_timelines(self, limit: int = 5):
        """
        모든 Bot의 타임라인 조회
        """
        return {
            'ceo': self.ceo_bot.timeline_home(limit=limit),
            'pm': self.pm_bot.timeline_home(limit=limit),
            'spirit': self.spirit_bot.timeline_home(limit=limit)
        }


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # Bot System 초기화
    bots = MulberryBotSystem()
    
    print("\n" + "="*50)
    print("Mulberry Bot System 준비 완료!")
    print("="*50)
    print("\n사용 가능한 명령어:")
    print("  bots.test_all_bots()        # 모든 Bot 테스트")
    print("  bots.team_morning_routine()  # 아침 루틴")
    print("  bots.ceo_announce('메시지')  # CEO 공지")
    print("  bots.pm_daily_standup([...]) # PM 일일 계획")
    print("  bots.spirit_post_leaderboard([...]) # 리더보드")
    print("\n" + "="*50)
    
    # 자동 테스트 실행하시겠습니까? (Y/n)
    user_input = input("\n모든 Bot 테스트를 실행하시겠습니까? (y/N): ")
    
    if user_input.lower() == 'y':
        print("\n🚀 테스트 시작...\n")
        results = bots.test_all_bots()
        
        print("\n✅ 테스트 완료!")
        print("Mastodon에서 확인하세요!")

"""
🌿 Mulberry Bot System
======================
4개 봇 통합 시스템 (requests 기반):
  - @ceo_mulberry      (CEO Bot)
  - @pm_mulberry       (PM Bot)
  - @spirit_mulberry   (Spirit Score Bot)
  - @nguyen_trang      (Nguyen Trang - AI Operations Manager)
"""

import requests
import os
from datetime import datetime

# ─────────────────────────────────────────────
# .env.mastodon 수동 로드
# ─────────────────────────────────────────────

def load_env(filepath='.env.mastodon'):
    env = {}
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"⚠️ {filepath} 파일을 찾을 수 없습니다.")
    return env

ENV = load_env('/sessions/tender-busy-knuth/mnt/mulberry-/.env.mastodon')
INSTANCE = ENV.get('MASTODON_INSTANCE', 'https://mastodon.social')

# ─────────────────────────────────────────────
# 봇 클래스
# ─────────────────────────────────────────────

class MastodonBot:
    def __init__(self, name, access_token, instance=INSTANCE):
        self.name = name
        self.token = access_token
        self.instance = instance
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def toot(self, message: str):
        """게시물 작성"""
        url = f"{self.instance}/api/v1/statuses"
        response = requests.post(url, headers=self.headers, json={'status': message})
        if response.status_code == 200:
            print(f"✅ {self.name} Toot 성공!")
            return True
        else:
            print(f"❌ {self.name} Toot 실패: {response.status_code}")
            return False

    def me(self):
        """계정 정보 확인"""
        url = f"{self.instance}/api/v1/accounts/verify_credentials"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None


# ─────────────────────────────────────────────
# Mulberry 봇 시스템
# ─────────────────────────────────────────────

class MulberryBotSystem:
    def __init__(self):
        print("🌿 Mulberry Bot System 초기화 중...\n")

        self.ceo_bot = MastodonBot(
            "CEO Bot (@ceo_mulberry)",
            ENV.get('CEO_BOT_ACCESS_TOKEN', '')
        )
        self.pm_bot = MastodonBot(
            "PM Bot (@pm_mulberry)",
            ENV.get('PM_BOT_ACCESS_TOKEN', '')
        )
        self.spirit_bot = MastodonBot(
            "Spirit Score Bot (@spirit_mulberry)",
            ENV.get('SPIRIT_BOT_ACCESS_TOKEN', '')
        )
        self.nguyen_trang_bot = MastodonBot(
            "Nguyen Trang (@nguyen_trang)",
            ENV.get('NGUYEN_TRANG_ACCESS_TOKEN', '')
        )
        print("✅ 4개 봇 초기화 완료!\n")

    def test_all_bots(self):
        """4개 봇 연결 테스트"""
        print("🧪 봇 연결 테스트 시작...\n")
        bots = [self.ceo_bot, self.pm_bot, self.spirit_bot, self.nguyen_trang_bot]
        success = 0
        for bot in bots:
            account = bot.me()
            if account:
                print(f"✅ {bot.name}: 연결 성공 — @{account['username']}")
                success += 1
            else:
                print(f"❌ {bot.name}: 연결 실패")

        print(f"\n📊 결과: {success}/4 봇 정상")
        return success == 4

    def team_morning_routine(self):
        """팀 아침 루틴"""
        today = datetime.now().strftime("%Y년 %m월 %d일")
        print(f"\n⏰ 아침 루틴 시작 — {today}\n")

        self.ceo_bot.toot(
            f"🌾 [CEO 공지]\n\n{today}\n식품사막화 제로를 향해 오늘도 함께 달립시다! 🚀\n\n#MulberryProject #식품사막화제로"
        )
        self.pm_bot.toot(
            f"📋 [PM 일일 계획 - {today}]\n\n• 팀 이슈 점검\n• GitHub 업데이트\n• Spirit Score 리더보드\n\n#MulberryProject"
        )
        self.spirit_bot.toot(
            f"🏆 [Spirit Score 리더보드]\n\n1. @re_eul — 95 SS\n2. @nguyen_trang — 90 SS\n3. @ceo_mulberry — 88 SS\n\n#SpiritScore #MulberryProject"
        )
        self.nguyen_trang_bot.toot(
            f"🌿 [AI Operations Report - {today}]\n\n• HF Space: ✅ Running\n• Mastodon Bots: ✅ Active\n• GitHub: ✅ Connected\n\n— Nguyen Trang, AI Operations Manager\n#MulberryProject"
        )
        print("\n✅ 아침 루틴 완료!")


# ─────────────────────────────────────────────
# 실행
# ─────────────────────────────────────────────

if __name__ == "__main__":
    bots = MulberryBotSystem()

    print("=" * 40)
    if bots.test_all_bots():
        print("\n🎉 모든 봇 정상 연결!")
        answer = input("\n아침 루틴을 실행하시겠습니까? (y/N): ").strip().lower()
        if answer == 'y':
            bots.team_morning_routine()
    else:
        print("\n⚠️ 일부 봇 연결 실패. 키값을 확인해 주세요.")

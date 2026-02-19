"""
Mulberry Bot 초간단 테스트
CTO Koda
"""

from mastodon import Mastodon

print("="*50)
print("Mulberry Bot 테스트")
print("="*50)
print()

# CEO Bot
print("1. CEO Bot 테스트 중...")
try:
    ceo_bot = Mastodon(
        client_id='NSMDsFSuKRXitZshoeKHIQFduHGPNU2kHAgSA84ogYo',
        client_secret='LxZtVcokzxgqr8fOSDeAA6fA39xkMMGMjrdmueWPFps',
        access_token='1qgEb3QivKw3r6WNS01ua_qE1uop2QBKtPUFpz5xp9U',
        api_base_url='https://mastodon.social'
    )
    
    result = ceo_bot.toot("🌾 CEO Bot 테스트 성공!\n#MulberryTeam #BotTest")
    print("   ✅ CEO Bot: 성공!")
except Exception as e:
    print(f"   ❌ CEO Bot: 실패 - {e}")

print()

# PM Bot
print("2. PM Bot 테스트 중...")
try:
    pm_bot = Mastodon(
        client_id='IQL4lO9hfVVsyUvWtVN9h4pFyCRpNb38myPF84g6QiU',
        client_secret='jT_VUheS4xymN-dkrPrTWsDkPD9MI67pSDLl3qWqAi8',
        access_token='d5fWGxXBz4xXkmJCwUGI97kAt0Ud9dufeK4oZ9N65o0',
        api_base_url='https://mastodon.social'
    )
    
    result = pm_bot.toot("📋 PM Bot 테스트 성공!\n#MulberryTeam #BotTest")
    print("   ✅ PM Bot: 성공!")
except Exception as e:
    print(f"   ❌ PM Bot: 실패 - {e}")

print()

# Spirit Bot
print("3. Spirit Score Bot 테스트 중...")
try:
    spirit_bot = Mastodon(
        client_id='2dwYeg6VczzX5AjzG7_2q8pKsdNhUSkgNVESMyDOH6g',
        client_secret='rrw8rYduj16koNvI7vrpgOiaJGZKKkZ2TIIYMYBBpEI',
        access_token='yiAMC_yQc1zh4Ngh62K_2FpTsuYD8obdZggtlF4QZ7A',
        api_base_url='https://mastodon.social'
    )
    
    result = spirit_bot.toot("🌾 Spirit Score Bot 테스트 성공!\n#MulberryTeam #BotTest")
    print("   ✅ Spirit Bot: 성공!")
except Exception as e:
    print(f"   ❌ Spirit Bot: 실패 - {e}")

print()
print("="*50)
print("테스트 완료!")
print("Mastodon에서 확인하세요!")
print("="*50)

"""
Mulberry Project: AI Agent Core Logic
Roles: Malu (Strategy), Koda (CTO)
"""

class MulberryAgent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.mission = "인제군 식품사막화 해소 및 시니어 케어"

    def get_status(self):
        return f"[{self.name} {self.role}] 시스템 정상 작동 중. 미션: {self.mission}"

# 핵심 에이전트 인스턴스화
malu = MulberryAgent("Malu", "수석 실장 (Strategy)")
koda = MulberryAgent("Koda", "CTO (Technology)")

if __name__ == "__main__":
    print(malu.get_status())
    print(koda.get_status())

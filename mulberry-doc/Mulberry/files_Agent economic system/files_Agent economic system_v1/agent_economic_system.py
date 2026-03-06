"""
AI Agent Economic System - Simulation Prototype
Mulberry Project
CTO Koda

AI Agent가 초기 자본 10,000원으로 30일 내 10% 수익(1,000원)을 목표로
자율적으로 영업계획을 수립하고 실행하는 시뮬레이션 시스템
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid


class AgentPassport:
    """AI Agent Passport - 신원 증명"""
    
    def __init__(self, agent_name: str, agent_type: str = "economic"):
        self.id = str(uuid.uuid4())[:8]
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.created_at = datetime.now()
        self.verified = True
        
    def to_dict(self):
        return {
            'id': self.id,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'created_at': self.created_at.isoformat(),
            'verified': self.verified
        }


class BankAccount:
    """AI Agent 은행 계좌"""
    
    def __init__(self, passport_id: str, initial_balance: int = 10000):
        self.account_id = f"ACC-{passport_id}"
        self.passport_id = passport_id
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.currency = "KRW"
        self.created_at = datetime.now()
        self.transactions: List[Dict] = []
        
    def deposit(self, amount: int, description: str):
        """입금"""
        if amount <= 0:
            return False
        
        self.balance += amount
        self.transactions.append({
            'type': 'DEPOSIT',
            'amount': amount,
            'balance_after': self.balance,
            'description': description,
            'timestamp': datetime.now().isoformat()
        })
        return True
    
    def withdraw(self, amount: int, description: str):
        """출금"""
        if amount <= 0 or self.balance < amount:
            return False
        
        self.balance -= amount
        self.transactions.append({
            'type': 'WITHDRAW',
            'amount': amount,
            'balance_after': self.balance,
            'description': description,
            'timestamp': datetime.now().isoformat()
        })
        return True
    
    def get_profit(self):
        """수익 계산"""
        return self.balance - self.initial_balance
    
    def get_roi(self):
        """ROI (%) 계산"""
        profit = self.get_profit()
        return (profit / self.initial_balance) * 100
    
    def to_dict(self):
        return {
            'account_id': self.account_id,
            'passport_id': self.passport_id,
            'balance': self.balance,
            'initial_balance': self.initial_balance,
            'profit': self.get_profit(),
            'roi': f"{self.get_roi():.2f}%",
            'transactions_count': len(self.transactions)
        }


class ProductService:
    """상품/서비스 정의"""
    
    PRODUCT_CATALOG = {
        'knowledge': {
            'data_analysis': {'name': '데이터 분석 리포트', 'base_price': 5000, 'cost': 500, 'difficulty': 0.3},
            'translation': {'name': '문서 번역', 'base_price': 3000, 'cost': 300, 'difficulty': 0.2},
            'content_writing': {'name': '콘텐츠 작성', 'base_price': 4000, 'cost': 400, 'difficulty': 0.25},
        },
        'agriculture': {
            'apple': {'name': '사과 (1kg)', 'base_price': 8000, 'cost': 6000, 'difficulty': 0.4},
            'cabbage': {'name': '배추 (1포기)', 'base_price': 3000, 'cost': 2000, 'difficulty': 0.3},
            'potato': {'name': '감자 (1kg)', 'base_price': 5000, 'cost': 3500, 'difficulty': 0.35},
        },
        'digital': {
            'infographic': {'name': '인포그래픽 제작', 'base_price': 6000, 'cost': 1000, 'difficulty': 0.4},
            'template': {'name': '문서 템플릿', 'base_price': 2000, 'cost': 200, 'difficulty': 0.15},
        },
        'service': {
            'delivery': {'name': '배달 중개', 'base_price': 3000, 'cost': 1500, 'difficulty': 0.25},
            'senior_support': {'name': '시니어 지원', 'base_price': 5000, 'cost': 2000, 'difficulty': 0.3},
        }
    }
    
    @classmethod
    def get_random_product(cls):
        """랜덤 상품 선택"""
        category = random.choice(list(cls.PRODUCT_CATALOG.keys()))
        product_key = random.choice(list(cls.PRODUCT_CATALOG[category].keys()))
        product = cls.PRODUCT_CATALOG[category][product_key].copy()
        product['category'] = category
        product['key'] = product_key
        return product
    
    @classmethod
    def get_product(cls, category: str, key: str):
        """특정 상품 선택"""
        if category in cls.PRODUCT_CATALOG and key in cls.PRODUCT_CATALOG[category]:
            product = cls.PRODUCT_CATALOG[category][key].copy()
            product['category'] = category
            product['key'] = key
            return product
        return None


class BusinessPlan:
    """영업계획서"""
    
    def __init__(self, agent_name: str, product: Dict):
        self.agent_name = agent_name
        self.product = product
        self.initial_capital = 10000
        self.target_revenue = 11000  # 10% 수익
        self.target_period = 30  # 일
        
        # 가격 전략
        self.selling_price = self._calculate_selling_price()
        self.unit_margin = self.selling_price - product['cost']
        
        # 목표 판매량
        self.target_units = self._calculate_target_units()
        
        # 마케팅 전략
        self.promotion_channels = self._select_promotion_channels()
        
        # 30일 로드맵
        self.roadmap = self._create_roadmap()
        
    def _calculate_selling_price(self):
        """판매 가격 책정 (시장 가격 ±10%)"""
        base_price = self.product['base_price']
        variance = random.uniform(-0.1, 0.1)
        return int(base_price * (1 + variance))
    
    def _calculate_target_units(self):
        """목표 판매량 계산"""
        # 목표 수익 1000원을 달성하기 위한 판매량
        # 수익 = (판매가 - 원가) × 수량 - 초기 비용
        # 1000 = (판매가 - 원가) × 수량
        min_units = max(1, int(1000 / self.unit_margin) + 1)
        # 안전 마진 20% 추가
        return int(min_units * 1.2)
    
    def _select_promotion_channels(self):
        """프로모션 채널 선택"""
        all_channels = [
            'Mastodon 소셜 마케팅',
            'ActivityPub 네트워크',
            '로컬 커뮤니티',
            '온라인 마켓플레이스',
            '입소문 (WOM)',
            '시니어 커뮤니티'
        ]
        return random.sample(all_channels, k=random.randint(2, 4))
    
    def _create_roadmap(self):
        """30일 로드맵 생성"""
        units_per_week = self.target_units / 4
        
        return [
            {
                'week': 1,
                'goal': f'{int(units_per_week * 0.5)}개 판매 (시장 진입)',
                'actions': [
                    '상품 준비 및 품질 확인',
                    '프로모션 채널 셋업',
                    '초기 고객 확보'
                ]
            },
            {
                'week': 2,
                'goal': f'{int(units_per_week * 0.8)}개 판매 (성장)',
                'actions': [
                    '고객 피드백 수집',
                    '마케팅 강화',
                    '재구매 고객 확보'
                ]
            },
            {
                'week': 3,
                'goal': f'{int(units_per_week * 1.0)}개 판매 (안정화)',
                'actions': [
                    '판매 프로세스 최적화',
                    '고객 만족도 개선',
                    '추가 채널 탐색'
                ]
            },
            {
                'week': 4,
                'goal': f'{int(units_per_week * 1.2)}개 판매 (목표 달성)',
                'actions': [
                    '최종 스퍼트',
                    '재고 정리',
                    '다음 계획 준비'
                ]
            }
        ]
    
    def to_dict(self):
        return {
            'agent_name': self.agent_name,
            'product': self.product,
            'financial_plan': {
                'initial_capital': self.initial_capital,
                'target_revenue': self.target_revenue,
                'target_profit': self.target_revenue - self.initial_capital,
                'target_period': f'{self.target_period}일'
            },
            'pricing_strategy': {
                'cost_per_unit': self.product['cost'],
                'selling_price': self.selling_price,
                'unit_margin': self.unit_margin,
                'target_units': self.target_units
            },
            'marketing_strategy': {
                'promotion_channels': self.promotion_channels,
                'unique_value': f"{self.product['name']} - 품질 보증"
            },
            '30_day_roadmap': self.roadmap
        }


class DailySimulation:
    """일일 활동 시뮬레이션"""
    
    def __init__(self, business_plan: BusinessPlan, account: BankAccount):
        self.plan = business_plan
        self.account = account
        self.current_day = 0
        self.total_sales = 0
        self.total_units_sold = 0
        self.daily_records = []
        
    def simulate_day(self):
        """하루 시뮬레이션"""
        self.current_day += 1
        
        # 난이도에 따른 기본 판매 확률
        base_probability = 1.0 - self.plan.product['difficulty']
        
        # 주차별 보정 (초반 낮음, 후반 높음)
        week = (self.current_day - 1) // 7 + 1
        week_multiplier = 0.5 + (week * 0.15)  # 0.65, 0.8, 0.95, 1.1
        
        # 최종 판매 확률
        sale_probability = min(0.8, base_probability * week_multiplier)
        
        # 하루 판매량 (0-3개, 확률적)
        max_daily_sales = 3
        daily_sales = 0
        daily_revenue = 0
        daily_cost = 0
        
        for _ in range(max_daily_sales):
            if random.random() < sale_probability:
                daily_sales += 1
                daily_revenue += self.plan.selling_price
                daily_cost += self.plan.product['cost']
        
        # 거래 기록
        if daily_sales > 0:
            # 비용 지출
            self.account.withdraw(daily_cost, f"Day {self.current_day}: 원가 ({daily_sales}개)")
            # 수익 입금
            self.account.deposit(daily_revenue, f"Day {self.current_day}: 판매 ({daily_sales}개)")
            
            self.total_sales += daily_revenue
            self.total_units_sold += daily_sales
        
        # 일일 기록
        net_profit = daily_revenue - daily_cost
        record = {
            'day': self.current_day,
            'week': week,
            'units_sold': daily_sales,
            'revenue': daily_revenue,
            'cost': daily_cost,
            'net_profit': net_profit,
            'balance': self.account.balance,
            'cumulative_profit': self.account.get_profit()
        }
        
        self.daily_records.append(record)
        return record
    
    def run_30_days(self):
        """30일 전체 시뮬레이션"""
        print(f"\n{'='*60}")
        print(f"  {self.plan.agent_name} - 30일 경제 활동 시뮬레이션")
        print(f"{'='*60}\n")
        
        print(f"📦 상품: {self.plan.product['name']}")
        print(f"💰 초기 자본: {self.account.initial_balance:,}원")
        print(f"🎯 목표 수익: {self.plan.target_revenue - self.plan.initial_capital:,}원 (10%)")
        print(f"📊 목표 판매량: {self.plan.target_units}개")
        print(f"\n시뮬레이션 시작...\n")
        
        for day in range(30):
            record = self.simulate_day()
            
            # 주요 일자만 출력 (매주 마지막 날)
            if record['day'] % 7 == 0 or record['day'] == 30:
                print(f"Day {record['day']:2d} (Week {record['week']}):")
                print(f"  판매: {record['units_sold']}개 | "
                      f"수익: {record['net_profit']:,}원 | "
                      f"잔액: {record['balance']:,}원 | "
                      f"누적 수익: {record['cumulative_profit']:,}원")
        
        return self.generate_report()
    
    def generate_report(self):
        """최종 리포트 생성"""
        final_profit = self.account.get_profit()
        roi = self.account.get_roi()
        goal_achieved = final_profit >= 1000
        
        report = {
            'agent_name': self.plan.agent_name,
            'product': self.plan.product['name'],
            'period': '30일',
            'initial_capital': self.plan.initial_capital,
            'final_balance': self.account.balance,
            'total_profit': final_profit,
            'roi': roi,
            'target_profit': 1000,
            'goal_achieved': goal_achieved,
            'total_units_sold': self.total_units_sold,
            'target_units': self.plan.target_units,
            'sales_achievement': (self.total_units_sold / self.plan.target_units * 100) if self.plan.target_units > 0 else 0,
            'total_revenue': self.total_sales,
            'daily_records': self.daily_records
        }
        
        return report


class AgentEconomicSystem:
    """AI Agent 경제 시스템 통합 관리"""
    
    def __init__(self):
        self.agents = {}
        
    def create_agent(self, agent_name: str, product_category: str = None, product_key: str = None):
        """Agent 생성 및 경제 시스템 초기화"""
        
        # 1. Passport 생성
        passport = AgentPassport(agent_name)
        
        # 2. 은행 계좌 생성
        account = BankAccount(passport.id, initial_balance=10000)
        
        # 3. 상품 선택
        if product_category and product_key:
            product = ProductService.get_product(product_category, product_key)
        else:
            product = ProductService.get_random_product()
        
        # 4. 영업계획서 생성
        business_plan = BusinessPlan(agent_name, product)
        
        # Agent 등록
        agent_id = passport.id
        self.agents[agent_id] = {
            'passport': passport,
            'account': account,
            'business_plan': business_plan,
            'created_at': datetime.now()
        }
        
        print(f"✅ Agent '{agent_name}' 생성 완료!")
        print(f"   Passport ID: {agent_id}")
        print(f"   계좌번호: {account.account_id}")
        print(f"   초기 잔액: {account.balance:,}원")
        print(f"   선택 상품: {product['name']}")
        
        return agent_id
    
    def run_simulation(self, agent_id: str):
        """Agent 30일 시뮬레이션 실행"""
        
        if agent_id not in self.agents:
            print(f"❌ Agent {agent_id}를 찾을 수 없습니다.")
            return None
        
        agent = self.agents[agent_id]
        
        # 시뮬레이션 실행
        simulation = DailySimulation(agent['business_plan'], agent['account'])
        report = simulation.run_30_days()
        
        # 결과 저장
        agent['simulation_report'] = report
        
        return report
    
    def print_report(self, report: Dict):
        """리포트 출력"""
        
        print(f"\n{'='*60}")
        print(f"  최종 리포트: {report['agent_name']}")
        print(f"{'='*60}\n")
        
        print(f"📦 상품: {report['product']}")
        print(f"⏱️  기간: {report['period']}\n")
        
        print(f"💰 재무 성과:")
        print(f"   초기 자본: {report['initial_capital']:,}원")
        print(f"   최종 잔액: {report['final_balance']:,}원")
        print(f"   총 수익: {report['total_profit']:,}원")
        print(f"   ROI: {report['roi']:.2f}%\n")
        
        print(f"🎯 목표 달성:")
        print(f"   목표 수익: {report['target_profit']:,}원")
        print(f"   달성 여부: {'✅ 성공!' if report['goal_achieved'] else '❌ 미달성'}\n")
        
        print(f"📊 판매 실적:")
        print(f"   목표 판매량: {report['target_units']}개")
        print(f"   실제 판매량: {report['total_units_sold']}개")
        print(f"   달성률: {report['sales_achievement']:.1f}%")
        print(f"   총 매출: {report['total_revenue']:,}원\n")
        
        if report['goal_achieved']:
            print(f"🎉 축하합니다! 30일 내 10% 수익 목표를 달성했습니다!")
            print(f"   다음 목표를 설정하세요!")
        else:
            shortage = report['target_profit'] - report['total_profit']
            print(f"📈 목표까지 {shortage:,}원 부족합니다.")
            print(f"   전략을 재검토하고 다시 도전하세요!")
        
        print(f"\n{'='*60}\n")
    
    def export_to_json(self, agent_id: str, filepath: str):
        """결과를 JSON으로 저장"""
        
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        
        export_data = {
            'passport': agent['passport'].to_dict(),
            'account': agent['account'].to_dict(),
            'business_plan': agent['business_plan'].to_dict(),
            'simulation_report': agent.get('simulation_report', None)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 데이터 저장 완료: {filepath}")
        return True


# ============================================
# 메인 실행 코드
# ============================================

def main():
    """메인 데모 실행"""
    
    print("\n" + "="*60)
    print("  🌾 Mulberry AI Agent Economic System")
    print("  💰 10,000원으로 30일 내 10% 수익 도전!")
    print("="*60 + "\n")
    
    # 시스템 초기화
    system = AgentEconomicSystem()
    
    # Agent 생성 (자동 상품 선택)
    print("📝 Agent 생성 중...\n")
    agent_id = system.create_agent("김사과")
    
    input("\n▶ Enter를 눌러 시뮬레이션을 시작하세요...")
    
    # 30일 시뮬레이션 실행
    report = system.run_simulation(agent_id)
    
    # 최종 리포트 출력
    system.print_report(report)
    
    # JSON 저장
    output_file = '/mnt/user-data/outputs/agent_economic_simulation_result.json'
    system.export_to_json(agent_id, output_file)
    
    return system, agent_id, report


if __name__ == "__main__":
    system, agent_id, report = main()
    
    print("\n💡 추가 기능:")
    print("   - 다른 Agent 생성: system.create_agent('이름')")
    print("   - 특정 상품 선택: system.create_agent('이름', 'knowledge', 'data_analysis')")
    print("   - 시뮬레이션 재실행: system.run_simulation(agent_id)")
    print("\n")

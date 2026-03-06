"""
Advanced AI Agent Skill System
Mulberry Project - CTO Koda

B단계: 스킬업 시스템 (전문성 + 속도)

PM 제안 5가지 방법론:
1. 시뮬레이션 가속화 (Accelerated Learning)
2. 합성 데이터 생성 (Synthetic Data)
3. 전이 학습 (Transfer Learning)
4. 스킬 NFT 마켓플레이스
5. 협업 학습 (Collaborative Learning)

추가:
6. 스킬 추천 엔진
7. 경쟁 환경 모듈
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import uuid
from collections import defaultdict

# 기존 스킬 시스템 import
import sys
sys.path.append('/home/claude')
from agent_skill_system import AgentSkill, SkillNFT, AgentSkillSystem


# ============================================
# 1. 시뮬레이션 가속화 (Accelerated Learning)
# ============================================

class AcceleratedLearning:
    """30일치 경험을 1시간에 습득하는 타임 워프 모드"""
    
    def __init__(self):
        self.simulation_speed = 100  # 100배 속도
        
    def warp_simulation(self, agent_id: str, days: int = 30, scenario: str = "balanced"):
        """
        실제 시간 대비 100배 속도로 시뮬레이션
        
        Args:
            agent_id: Agent ID
            days: 시뮬레이션 일수
            scenario: 시나리오 (balanced, aggressive, conservative)
        """
        
        print(f"\n⚡ 타임 워프 시뮬레이션 시작: {days}일 → {days*24/self.simulation_speed:.1f}분")
        
        scenarios = {
            'balanced': {'sales_rate': 0.7, 'price_variance': 0.1, 'risk': 0.3},
            'aggressive': {'sales_rate': 0.5, 'price_variance': 0.2, 'risk': 0.5},
            'conservative': {'sales_rate': 0.85, 'price_variance': 0.05, 'risk': 0.1}
        }
        
        params = scenarios.get(scenario, scenarios['balanced'])
        
        results = {
            'days_simulated': days,
            'total_sales': 0,
            'total_revenue': 0,
            'total_profit': 0,
            'skills_gained': {},
            'level_ups': [],
            'daily_breakdown': []
        }
        
        for day in range(1, days + 1):
            # 일일 활동 시뮬레이션 (초 단위로 100번 반복)
            daily_sales = 0
            daily_revenue = 0
            
            for _ in range(self.simulation_speed):
                if random.random() < params['sales_rate'] / self.simulation_speed:
                    sale_amount = random.randint(3000, 8000) * (1 + random.uniform(-params['price_variance'], params['price_variance']))
                    daily_sales += 1
                    daily_revenue += sale_amount
            
            daily_profit = daily_revenue * (1 - params['risk'])
            
            results['total_sales'] += daily_sales
            results['total_revenue'] += daily_revenue
            results['total_profit'] += daily_profit
            
            results['daily_breakdown'].append({
                'day': day,
                'sales': daily_sales,
                'revenue': daily_revenue,
                'profit': daily_profit
            })
            
            # 주간 마일스톤 출력
            if day % 7 == 0:
                print(f"  Week {day//7}: {daily_sales}건 판매, 수익 {daily_profit:,.0f}원")
        
        # 스킬 획득 계산
        results['skills_gained'] = {
            'sales': results['total_sales'] * 10,
            'marketing': int(results['total_sales'] / days * 100),
            'pricing': int(results['total_profit'] / 1000),
            'financial': int(results['total_profit'] / results['total_revenue'] * 1000) if results['total_revenue'] > 0 else 0
        }
        
        print(f"\n✅ 시뮬레이션 완료!")
        print(f"   총 판매: {results['total_sales']}건")
        print(f"   총 수익: {results['total_profit']:,.0f}원")
        print(f"   획득 경험치: {sum(results['skills_gained'].values()):,}")
        
        return results


# ============================================
# 2. 합성 데이터 생성 (Synthetic Data)
# ============================================

class SyntheticDataGenerator:
    """실제 경험 없이도 다양한 상황을 학습할 수 있는 합성 데이터"""
    
    def __init__(self):
        self.scenarios = self._init_scenarios()
        
    def _init_scenarios(self):
        """시나리오 템플릿 초기화"""
        return {
            'seasonal_demand': {
                'winter': {'multiplier': 1.5, 'products': ['감자', '배추', '난방용품']},
                'spring': {'multiplier': 1.2, 'products': ['새싹채소', '봄나물']},
                'summer': {'multiplier': 0.8, 'products': ['수박', '오이', '냉방용품']},
                'fall': {'multiplier': 1.0, 'products': ['사과', '배', '밤']}
            },
            'price_shock': {
                'supply_shortage': {'price_change': 0.5, 'demand_change': 0.3},
                'oversupply': {'price_change': -0.3, 'demand_change': -0.1},
                'competitor_entry': {'price_change': -0.2, 'demand_change': -0.2}
            },
            'customer_types': {
                'demanding': {'patience': 0.3, 'price_sensitivity': 0.7, 'quality_focus': 0.9},
                'emotional': {'patience': 0.5, 'price_sensitivity': 0.4, 'quality_focus': 0.5},
                'rational': {'patience': 0.8, 'price_sensitivity': 0.8, 'quality_focus': 0.7},
                'impulse': {'patience': 0.2, 'price_sensitivity': 0.3, 'quality_focus': 0.3}
            }
        }
    
    def generate_seasonal_scenario(self, season: str, product: str, base_demand: int):
        """계절별 수요 변동 시나리오"""
        
        season_data = self.scenarios['seasonal_demand'].get(season, self.scenarios['seasonal_demand']['fall'])
        multiplier = season_data['multiplier']
        
        # 제품이 계절 적합 상품인지 확인
        if product in season_data['products']:
            multiplier *= 1.3
        
        expected_demand = int(base_demand * multiplier * random.uniform(0.9, 1.1))
        
        return {
            'season': season,
            'product': product,
            'base_demand': base_demand,
            'expected_demand': expected_demand,
            'multiplier': multiplier,
            'recommendation': f"{season}에 {product}는 수요 {multiplier:.1f}배 예상"
        }
    
    def generate_customer_interaction(self, customer_type: str, product_price: int):
        """고객 유형별 응대 시뮬레이션"""
        
        customer = self.scenarios['customer_types'].get(customer_type, self.scenarios['customer_types']['rational'])
        
        # 고객 반응 시뮬레이션
        if product_price > 10000:
            # 고가 상품
            purchase_probability = customer['price_sensitivity'] * 0.5
        elif product_price < 3000:
            # 저가 상품
            purchase_probability = customer['price_sensitivity'] * 1.5
        else:
            # 중가 상품
            purchase_probability = customer['price_sensitivity']
        
        # 품질에 따른 조정
        purchase_probability *= (1 + customer['quality_focus'] * 0.3)
        
        # 최종 구매 결정
        purchased = random.random() < purchase_probability
        
        return {
            'customer_type': customer_type,
            'product_price': product_price,
            'purchased': purchased,
            'patience_shown': customer['patience'],
            'price_sensitivity': customer['price_sensitivity'],
            'quality_focus': customer['quality_focus'],
            'learning': f"{customer_type} 고객은 {'구매' if purchased else '구매 안함'} → 가격 조정 필요" if not purchased else "성공적 판매"
        }
    
    def generate_crisis_scenario(self, crisis_type: str):
        """위기 상황 대응 시뮬레이션"""
        
        crises = {
            'supply_chain_disruption': {
                'impact': '공급망 차질로 재고 50% 감소',
                'recommended_action': '가격 30% 인상, 대체 공급처 확보',
                'skill_gain': 'crisis_management'
            },
            'natural_disaster': {
                'impact': '자연재해로 배송 불가',
                'recommended_action': '고객 소통 강화, 보상 정책 수립',
                'skill_gain': 'customer_relations'
            },
            'sudden_demand_spike': {
                'impact': '수요 300% 급증',
                'recommended_action': '긴급 재고 확보, 배송 우선순위 설정',
                'skill_gain': 'logistics_optimization'
            }
        }
        
        crisis = crises.get(crisis_type, crises['supply_chain_disruption'])
        
        return {
            'crisis_type': crisis_type,
            'impact': crisis['impact'],
            'recommended_action': crisis['recommended_action'],
            'skill_gained': crisis['skill_gain'],
            'experience_points': 200  # 위기 극복 보너스
        }


# ============================================
# 3. 전이 학습 (Transfer Learning)
# ============================================

class SkillTransferSystem:
    """한 분야에서 쌓은 스킬을 다른 분야에 적용"""
    
    def __init__(self):
        # 스킬 간 전이 가능성 매트릭스
        self.transfer_matrix = {
            ('agriculture', 'distribution'): {
                'mapping': {
                    '재배_일정_관리': '유통_일정_관리',
                    '수확량_예측': '수요_예측',
                    '병해충_진단': '문제_상품_식별'
                },
                'retention_rate': 0.7
            },
            ('marketing', 'sales'): {
                'mapping': {
                    '타겟_고객_분석': '영업_대상_선정',
                    '메시지_최적화': '세일즈_피치',
                    '캠페인_자동화': '영업_프로세스_자동화'
                },
                'retention_rate': 0.8
            },
            ('finance', 'investment'): {
                'mapping': {
                    '현금_흐름_최적화': '투자_포트폴리오_관리',
                    '리스크_관리': '투자_리스크_분석',
                    '예산_수립': '투자_계획_수립'
                },
                'retention_rate': 0.9
            }
        }
    
    def transfer_skill(self, source_skill: Dict, target_category: str) -> Dict:
        """스킬 전이 실행"""
        
        source_category = source_skill.get('category')
        transfer_key = (source_category, target_category)
        
        if transfer_key not in self.transfer_matrix:
            return {
                'success': False,
                'message': f"{source_category}에서 {target_category}로 전이 불가"
            }
        
        transfer_config = self.transfer_matrix[transfer_key]
        retention_rate = transfer_config['retention_rate']
        
        # 전이된 스킬 생성
        transferred_skill = {
            'original_skill': source_skill['skill_type'],
            'original_category': source_category,
            'new_category': target_category,
            'transferred_experience': int(source_skill['experience_points'] * retention_rate),
            'retention_rate': retention_rate,
            'mapping': transfer_config['mapping']
        }
        
        return {
            'success': True,
            'transferred_skill': transferred_skill,
            'message': f"{source_category} → {target_category} 전이 성공 ({retention_rate*100:.0f}% 보존)"
        }


# ============================================
# 4. 스킬 NFT 마켓플레이스
# ============================================

class SkillMarketplace:
    """스킬 NFT 거래 플랫폼"""
    
    def __init__(self):
        self.listings = {}  # nft_id -> listing
        self.transactions = []
        
    def list_nft(self, nft: SkillNFT, seller_id: str, price: float):
        """NFT 판매 등록"""
        
        listing_id = str(uuid.uuid4())[:8]
        
        self.listings[listing_id] = {
            'listing_id': listing_id,
            'nft': nft.to_dict(),
            'seller_id': seller_id,
            'price': price,
            'status': 'active',
            'created_at': datetime.now(),
            'views': 0,
            'favorites': 0
        }
        
        return {
            'success': True,
            'listing_id': listing_id,
            'message': f"NFT 판매 등록 완료: {price:,}원"
        }
    
    def buy_nft(self, listing_id: str, buyer_id: str):
        """NFT 구매"""
        
        if listing_id not in self.listings:
            return {'success': False, 'message': "존재하지 않는 리스팅"}
        
        listing = self.listings[listing_id]
        
        if listing['status'] != 'active':
            return {'success': False, 'message': "판매 종료된 NFT"}
        
        # 거래 실행
        price = listing['price']
        royalty_amount = price * listing['nft']['royalty']
        seller_amount = price - royalty_amount
        
        transaction = {
            'transaction_id': str(uuid.uuid4())[:8],
            'listing_id': listing_id,
            'nft_id': listing['nft']['nft_id'],
            'seller_id': listing['seller_id'],
            'buyer_id': buyer_id,
            'price': price,
            'royalty_amount': royalty_amount,
            'seller_amount': seller_amount,
            'timestamp': datetime.now()
        }
        
        self.transactions.append(transaction)
        listing['status'] = 'sold'
        
        # 구매자에게 스킬 경험치 80% 즉시 부여
        instant_experience = int(listing['nft']['metadata']['experience_points'] * 0.8)
        
        return {
            'success': True,
            'transaction': transaction,
            'instant_experience': instant_experience,
            'message': f"NFT 구매 완료! {instant_experience:,} 경험치 즉시 획득"
        }
    
    def search_nfts(self, category: str = None, min_level: int = None, max_price: float = None):
        """NFT 검색"""
        
        results = []
        
        for listing in self.listings.values():
            if listing['status'] != 'active':
                continue
            
            nft = listing['nft']
            
            # 필터링
            if category and nft['metadata'].get('category') != category:
                continue
            if min_level and nft['level'] < min_level:
                continue
            if max_price and listing['price'] > max_price:
                continue
            
            results.append(listing)
        
        # 가격 순 정렬
        results.sort(key=lambda x: x['price'])
        
        return results


# ============================================
# 5. 협업 학습 (Collaborative Learning)
# ============================================

class CollaborativeLearning:
    """여러 Agent가 함께 문제를 해결하며 상호 학습"""
    
    def __init__(self):
        self.active_collaborations = {}
        
    def create_collaboration(self, task: str, agents: List[str], learning_mode: str = "share_experience"):
        """협업 프로젝트 생성"""
        
        collab_id = str(uuid.uuid4())[:8]
        
        self.active_collaborations[collab_id] = {
            'collab_id': collab_id,
            'task': task,
            'agents': agents,
            'learning_mode': learning_mode,  # share_experience, competitive, mentor_mentee
            'status': 'active',
            'created_at': datetime.now(),
            'contributions': {agent_id: [] for agent_id in agents},
            'shared_experience': 0
        }
        
        return collab_id
    
    def add_contribution(self, collab_id: str, agent_id: str, contribution: Dict):
        """Agent의 기여 기록"""
        
        if collab_id not in self.active_collaborations:
            return {'success': False}
        
        collab = self.active_collaborations[collab_id]
        
        if agent_id not in collab['agents']:
            return {'success': False}
        
        collab['contributions'][agent_id].append({
            'timestamp': datetime.now(),
            'contribution': contribution,
            'experience_earned': contribution.get('experience', 0)
        })
        
        collab['shared_experience'] += contribution.get('experience', 0)
        
        return {'success': True}
    
    def complete_collaboration(self, collab_id: str):
        """협업 완료 및 경험치 배분"""
        
        if collab_id not in self.active_collaborations:
            return {'success': False}
        
        collab = self.active_collaborations[collab_id]
        collab['status'] = 'completed'
        
        # 경험치 배분
        total_experience = collab['shared_experience']
        agent_count = len(collab['agents'])
        
        if collab['learning_mode'] == 'share_experience':
            # 모든 Agent가 전체 경험치의 80% 획득
            experience_per_agent = int(total_experience * 0.8)
        elif collab['learning_mode'] == 'competitive':
            # 기여도에 따라 차등 배분
            contributions = {
                agent_id: sum(c['experience_earned'] for c in contribs)
                for agent_id, contribs in collab['contributions'].items()
            }
            total_contrib = sum(contributions.values())
            experience_per_agent = {
                agent_id: int(total_experience * (contrib / total_contrib))
                for agent_id, contrib in contributions.items()
            }
        else:  # mentor_mentee
            # 멘티는 120%, 멘토는 50%
            experience_per_agent = {}
            # 간단한 구현
            for i, agent_id in enumerate(collab['agents']):
                experience_per_agent[agent_id] = int(total_experience * (1.2 if i > 0 else 0.5))
        
        return {
            'success': True,
            'collab_id': collab_id,
            'total_experience': total_experience,
            'experience_per_agent': experience_per_agent,
            'duration': (datetime.now() - collab['created_at']).total_seconds() / 3600,  # 시간
            'message': "협업 완료! 모든 참여자가 경험치 획득"
        }


# ============================================
# 6. 스킬 추천 엔진 (P0 - 필수)
# ============================================

class SkillRecommendationEngine:
    """성공한 Agent들의 패턴 분석하여 다음 스킬 추천"""
    
    def __init__(self):
        self.success_patterns = defaultdict(list)
        self.skill_correlation = {}
        
    def analyze_successful_agents(self, successful_agents: List[Dict]):
        """성공한 Agent들의 스킬 조합 분석"""
        
        for agent in successful_agents:
            skill_combo = frozenset(agent['skills'].keys())
            self.success_patterns[skill_combo].append({
                'agent_id': agent['id'],
                'roi': agent['roi'],
                'revenue': agent['total_revenue']
            })
        
        # 스킬 상관관계 분석
        for combo in self.success_patterns.keys():
            for skill1 in combo:
                for skill2 in combo:
                    if skill1 != skill2:
                        key = tuple(sorted([skill1, skill2]))
                        self.skill_correlation[key] = self.skill_correlation.get(key, 0) + 1
        
        return {
            'patterns_found': len(self.success_patterns),
            'correlations_found': len(self.skill_correlation)
        }
    
    def recommend_next_skill(self, current_skills: List[str], target_category: str = None):
        """현재 스킬 기반 다음 추천 스킬"""
        
        recommendations = defaultdict(int)
        
        # 유사한 스킬 조합을 가진 성공 Agent 찾기
        for combo, agents in self.success_patterns.items():
            overlap = len(set(current_skills) & combo)
            if overlap > 0:
                # 현재 없는 스킬 추천
                for skill in combo:
                    if skill not in current_skills:
                        # 겹치는 스킬이 많을수록 높은 점수
                        recommendations[skill] += overlap * len(agents)
        
        # 상관관계 기반 추천
        for skill in current_skills:
            for (skill1, skill2), count in self.skill_correlation.items():
                if skill1 == skill and skill2 not in current_skills:
                    recommendations[skill2] += count
                elif skill2 == skill and skill1 not in current_skills:
                    recommendations[skill1] += count
        
        # 정렬
        sorted_recommendations = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'current_skills': current_skills,
            'recommendations': [
                {
                    'skill': skill,
                    'score': score,
                    'reason': f"성공 Agent의 {score} 사례에서 발견"
                }
                for skill, score in sorted_recommendations
            ]
        }
    
    def get_learning_path(self, current_skills: List[str], target_level: int = 5):
        """목표 레벨까지의 학습 경로 추천"""
        
        path = []
        skills = current_skills.copy()
        
        for _ in range(target_level - len(skills)):
            next_skills = self.recommend_next_skill(skills)
            if next_skills['recommendations']:
                recommended = next_skills['recommendations'][0]['skill']
                path.append({
                    'step': len(path) + 1,
                    'skill': recommended,
                    'reason': next_skills['recommendations'][0]['reason']
                })
                skills.append(recommended)
            else:
                break
        
        return {
            'starting_skills': current_skills,
            'target_level': target_level,
            'learning_path': path,
            'estimated_time': f"{len(path) * 30}일 (각 스킬당 30일 예상)"
        }


# ============================================
# 7. 경쟁 환경 모듈 (P2)
# ============================================

class AgentCompetition:
    """Agent 간 경쟁 대회"""
    
    def __init__(self):
        self.challenges = {}
        self.leaderboard = defaultdict(list)
        
    def create_challenge(self, title: str, category: str, entry_fee: int, prize: int, duration_days: int):
        """경쟁 대회 개최"""
        
        challenge_id = str(uuid.uuid4())[:8]
        
        self.challenges[challenge_id] = {
            'challenge_id': challenge_id,
            'title': title,
            'category': category,
            'entry_fee': entry_fee,
            'prize': prize,
            'duration_days': duration_days,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=duration_days),
            'participants': [],
            'status': 'open',
            'results': []
        }
        
        return {
            'success': True,
            'challenge_id': challenge_id,
            'message': f"챌린지 '{title}' 개최 (상금: {prize:,}원)"
        }
    
    def enter_challenge(self, challenge_id: str, agent_id: str):
        """챌린지 참가"""
        
        if challenge_id not in self.challenges:
            return {'success': False, 'message': "존재하지 않는 챌린지"}
        
        challenge = self.challenges[challenge_id]
        
        if challenge['status'] != 'open':
            return {'success': False, 'message': "참가 마감된 챌린지"}
        
        challenge['participants'].append({
            'agent_id': agent_id,
            'joined_at': datetime.now(),
            'score': 0
        })
        
        return {
            'success': True,
            'message': f"챌린지 참가 완료 (참가비: {challenge['entry_fee']:,}원)"
        }
    
    def submit_result(self, challenge_id: str, agent_id: str, score: float):
        """결과 제출"""
        
        challenge = self.challenges[challenge_id]
        
        for participant in challenge['participants']:
            if participant['agent_id'] == agent_id:
                participant['score'] = score
                break
        
        return {'success': True}
    
    def evaluate_challenge(self, challenge_id: str):
        """챌린지 평가 및 순위 결정"""
        
        challenge = self.challenges[challenge_id]
        challenge['status'] = 'evaluating'
        
        # 점수순 정렬
        participants = sorted(
            challenge['participants'],
            key=lambda x: x['score'],
            reverse=True
        )
        
        # 경험치 보너스 계산
        total_participants = len(participants)
        experience_bonuses = {}
        
        for rank, participant in enumerate(participants, 1):
            if rank <= total_participants * 0.1:  # 상위 10%
                bonus = 2.0
                tier = "🥇 Top 10%"
            elif rank <= total_participants * 0.25:  # 상위 25%
                bonus = 1.5
                tier = "🥈 Top 25%"
            else:
                bonus = 1.2  # 참가 보너스
                tier = "🥉 참가"
            
            experience_bonuses[participant['agent_id']] = {
                'rank': rank,
                'score': participant['score'],
                'bonus_multiplier': bonus,
                'tier': tier
            }
        
        challenge['status'] = 'completed'
        challenge['results'] = experience_bonuses
        
        # 리더보드 업데이트
        self.leaderboard[challenge['category']].extend(participants)
        
        return {
            'challenge_id': challenge_id,
            'total_participants': total_participants,
            'results': experience_bonuses,
            'winner': participants[0] if participants else None
        }


# ============================================
# 통합 Advanced Skill System
# ============================================

class AdvancedSkillSystem:
    """모든 기능 통합"""
    
    def __init__(self):
        self.accelerated_learning = AcceleratedLearning()
        self.synthetic_data = SyntheticDataGenerator()
        self.skill_transfer = SkillTransferSystem()
        self.marketplace = SkillMarketplace()
        self.collaboration = CollaborativeLearning()
        self.recommendation = SkillRecommendationEngine()
        self.competition = AgentCompetition()
        
    def get_available_features(self):
        """사용 가능한 기능 목록"""
        return {
            'accelerated_learning': "30일 → 1시간 타임 워프",
            'synthetic_data': "합성 데이터 생성 (시나리오, 고객, 위기)",
            'skill_transfer': "스킬 전이 학습 (70~90% 보존)",
            'nft_marketplace': "스킬 NFT 거래 (80% 경험치 즉시)",
            'collaboration': "협업 학습 (경험치 공유)",
            'recommendation': "AI 스킬 추천 엔진",
            'competition': "챌린지 (경험치 2배 보너스)"
        }


# ============================================
# 데모 실행
# ============================================

def demo_advanced_features():
    """고급 기능 데모"""
    
    print("\n" + "="*60)
    print("  🚀 Advanced Skill System Demo")
    print("  5가지 방법론 + 추가 기능")
    print("="*60 + "\n")
    
    system = AdvancedSkillSystem()
    
    # 1. 타임 워프 시뮬레이션
    print("1️⃣ 타임 워프 시뮬레이션 (30일 → 30분)")
    print("-" * 60)
    warp_result = system.accelerated_learning.warp_simulation(
        "agent_test", 
        days=30, 
        scenario="balanced"
    )
    
    # 2. 합성 데이터 - 계절별 시나리오
    print("\n2️⃣ 합성 데이터 생성")
    print("-" * 60)
    seasonal = system.synthetic_data.generate_seasonal_scenario("winter", "감자", 100)
    print(f"  {seasonal['recommendation']}")
    
    customer = system.synthetic_data.generate_customer_interaction("demanding", 5000)
    print(f"  {customer['learning']}")
    
    # 3. 스킬 추천
    print("\n3️⃣ 스킬 추천 엔진")
    print("-" * 60)
    
    # 성공 Agent 데이터 분석
    successful_agents = [
        {'id': 'agent_1', 'roi': 2000, 'total_revenue': 200000, 
         'skills': {'sales_service': 3, 'marketing_service': 4, 'pricing_service': 2}},
        {'id': 'agent_2', 'roi': 1500, 'total_revenue': 150000,
         'skills': {'sales_service': 3, 'marketing_service': 3, 'financial_general': 2}}
    ]
    
    system.recommendation.analyze_successful_agents(successful_agents)
    recommendations = system.recommendation.recommend_next_skill(['sales_service'])
    
    print(f"  현재 스킬: sales_service")
    for rec in recommendations['recommendations'][:3]:
        print(f"  → 추천: {rec['skill']} ({rec['reason']})")
    
    # 4. NFT 마켓플레이스
    print("\n4️⃣ 스킬 NFT 마켓플레이스")
    print("-" * 60)
    
    # 샘플 NFT 생성 (실제로는 SkillNFT 클래스 사용)
    sample_nft = type('NFT', (), {
        'to_dict': lambda self: {
            'nft_id': 'nft_001',
            'skill_name': 'Marketing Master',
            'level': 4,
            'rarity': 'epic',
            'royalty': 0.1,
            'metadata': {'experience_points': 2800, 'category': 'marketing'}
        }
    })()
    
    listing = system.marketplace.list_nft(sample_nft, "agent_김사과", 20000)
    print(f"  {listing['message']}")
    
    # 5. 챌린지
    print("\n5️⃣ Agent 챌린지")
    print("-" * 60)
    challenge = system.competition.create_challenge(
        "인제 감자 판매 왕",
        "agriculture",
        entry_fee=5000,
        prize=100000,
        duration_days=7
    )
    print(f"  {challenge['message']}")
    
    print("\n" + "="*60)
    print("  ✅ 모든 고급 기능 시연 완료!")
    print("="*60 + "\n")
    
    return system


if __name__ == "__main__":
    system = demo_advanced_features()
    
    print("\n💡 사용 가능한 기능:")
    for feature, desc in system.get_available_features().items():
        print(f"   - {feature}: {desc}")

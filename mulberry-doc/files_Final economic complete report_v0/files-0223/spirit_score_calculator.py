"""
Spirit Score Calculator
Mulberry Project - CTO Koda
PM 제안 반영: Spirit Score 계산 로직 구현
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


class SpiritScoreCalculator:
    """
    Agent/Investor의 Spirit Score 계산
    
    Spirit Score = 신뢰도, 기여도, 윤리성을 종합한 점수 (0.0 ~ 1.0)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        if config is None:
            # 기본 설정 (skill_config.py의 SPIRIT_SCORE_CONFIG 사용)
            self.config = {
                'base_score': 0.5,
                'factors': {
                    'investment_success_rate': {'weight': 0.3},
                    'nft_reliability': {'weight': 0.2},
                    'collaboration_contribution': {'weight': 0.25},
                    'sponsor_ratio': {'weight': 0.15},
                    'community_activity': {'weight': 0.1}
                },
                'penalties': {
                    'investment_default': -0.1,
                    'nft_fraud': -0.2,
                    'collaboration_abandon': -0.05
                }
            }
        else:
            self.config = config
    
    def calculate_agent_spirit_score(
        self,
        total_investments: int,
        successful_investments: int,
        nft_reviews_positive: int,
        nft_reviews_total: int,
        collaboration_experience: int,
        sponsor_amount: float,
        total_revenue: float,
        challenge_participations: int,
        mentoring_sessions: int,
        penalties: List[str] = None
    ) -> Dict:
        """
        Agent의 Spirit Score 계산
        
        Args:
            total_investments: 총 투자 유치 건수
            successful_investments: 성공적인 투자 건수
            nft_reviews_positive: NFT 긍정 리뷰 수
            nft_reviews_total: NFT 총 리뷰 수
            collaboration_experience: 협업으로 얻은 총 경험치
            sponsor_amount: 시니어 후원 총액
            total_revenue: 총 수익
            challenge_participations: 챌린지 참가 횟수
            mentoring_sessions: 멘토링 세션 수
            penalties: 페널티 목록 (예: ['investment_default'])
        
        Returns:
            {
                'spirit_score': float,
                'breakdown': dict,
                'grade': str
            }
        """
        
        if penalties is None:
            penalties = []
        
        # 각 요소 계산
        factors = self.config['factors']
        breakdown = {}
        total_score = self.config['base_score']
        
        # 1. 투자 성공률
        if total_investments > 0:
            success_rate = successful_investments / total_investments
            factor_score = success_rate * factors['investment_success_rate']['weight']
            breakdown['investment_success_rate'] = {
                'value': success_rate,
                'contribution': factor_score
            }
            total_score += factor_score - (self.config['base_score'] * factors['investment_success_rate']['weight'])
        
        # 2. NFT 신뢰도
        if nft_reviews_total > 0:
            nft_reliability = nft_reviews_positive / nft_reviews_total
        else:
            nft_reliability = 0.5  # 리뷰 없으면 중립
        
        factor_score = nft_reliability * factors['nft_reliability']['weight']
        breakdown['nft_reliability'] = {
            'value': nft_reliability,
            'contribution': factor_score
        }
        total_score += factor_score - (self.config['base_score'] * factors['nft_reliability']['weight'])
        
        # 3. 협업 기여도 (정규화: 10,000 경험치 = 1.0)
        collaboration_score = min(collaboration_experience / 10000, 1.0)
        factor_score = collaboration_score * factors['collaboration_contribution']['weight']
        breakdown['collaboration_contribution'] = {
            'value': collaboration_score,
            'contribution': factor_score
        }
        total_score += factor_score - (self.config['base_score'] * factors['collaboration_contribution']['weight'])
        
        # 4. 시니어 후원 비율
        if total_revenue > 0:
            sponsor_ratio = sponsor_amount / total_revenue
        else:
            sponsor_ratio = 0
        
        factor_score = min(sponsor_ratio, 1.0) * factors['sponsor_ratio']['weight']
        breakdown['sponsor_ratio'] = {
            'value': sponsor_ratio,
            'contribution': factor_score
        }
        total_score += factor_score - (self.config['base_score'] * factors['sponsor_ratio']['weight'])
        
        # 5. 커뮤니티 활동 (정규화: 50 활동 = 1.0)
        community_score = min((challenge_participations + mentoring_sessions) / 50, 1.0)
        factor_score = community_score * factors['community_activity']['weight']
        breakdown['community_activity'] = {
            'value': community_score,
            'contribution': factor_score
        }
        total_score += factor_score - (self.config['base_score'] * factors['community_activity']['weight'])
        
        # 페널티 적용
        penalty_total = 0
        for penalty in penalties:
            if penalty in self.config['penalties']:
                penalty_total += self.config['penalties'][penalty]
        
        total_score += penalty_total
        breakdown['penalties'] = {
            'items': penalties,
            'total': penalty_total
        }
        
        # 0.0 ~ 1.0 범위로 제한
        total_score = max(0.0, min(1.0, total_score))
        
        # 등급 부여
        grade = self._get_grade(total_score)
        
        return {
            'spirit_score': round(total_score, 3),
            'breakdown': breakdown,
            'grade': grade,
            'calculated_at': datetime.now().isoformat()
        }
    
    def calculate_investor_spirit_score(
        self,
        total_investments_made: int,
        successful_investments_made: int,
        nft_purchases: int,
        nft_purchase_reviews: int,  # 긍정 리뷰 남긴 횟수
        collaboration_participations: int,
        sponsor_contribution: float,  # 시니어 후원에 기여한 총액 (간접)
        total_invested_amount: float,
        community_votes: int,
        mentoring_received: int,
        penalties: List[str] = None
    ) -> Dict:
        """
        투자자의 Spirit Score 계산
        
        (Agent와 유사하지만 투자자 관점의 지표 사용)
        """
        
        if penalties is None:
            penalties = []
        
        breakdown = {}
        total_score = self.config['base_score']
        factors = self.config['factors']
        
        # 1. 투자 성공률
        if total_investments_made > 0:
            success_rate = successful_investments_made / total_investments_made
            factor_score = success_rate * factors['investment_success_rate']['weight']
            breakdown['investment_success_rate'] = {
                'value': success_rate,
                'contribution': factor_score
            }
            total_score += factor_score - (self.config['base_score'] * factors['investment_success_rate']['weight'])
        
        # 2. NFT 거래 신뢰도 (리뷰 남긴 비율)
        if nft_purchases > 0:
            review_rate = nft_purchase_reviews / nft_purchases
        else:
            review_rate = 0.5
        
        factor_score = review_rate * factors['nft_reliability']['weight']
        breakdown['nft_reliability'] = {
            'value': review_rate,
            'contribution': factor_score
        }
        total_score += factor_score - (self.config['base_score'] * factors['nft_reliability']['weight'])
        
        # 3. 협업 참여도 (정규화: 20 참여 = 1.0)
        collab_score = min(collaboration_participations / 20, 1.0)
        factor_score = collab_score * factors['collaboration_contribution']['weight']
        breakdown['collaboration_contribution'] = {
            'value': collab_score,
            'contribution': factor_score
        }
        total_score += factor_score - (self.config['base_score'] * factors['collaboration_contribution']['weight'])
        
        # 4. 시니어 후원 기여 비율
        if total_invested_amount > 0:
            sponsor_ratio = sponsor_contribution / total_invested_amount
        else:
            sponsor_ratio = 0
        
        factor_score = min(sponsor_ratio, 1.0) * factors['sponsor_ratio']['weight']
        breakdown['sponsor_ratio'] = {
            'value': sponsor_ratio,
            'contribution': factor_score
        }
        total_score += factor_score - (self.config['base_score'] * factors['sponsor_ratio']['weight'])
        
        # 5. 커뮤니티 활동
        community_score = min((community_votes + mentoring_received) / 30, 1.0)
        factor_score = community_score * factors['community_activity']['weight']
        breakdown['community_activity'] = {
            'value': community_score,
            'contribution': factor_score
        }
        total_score += factor_score - (self.config['base_score'] * factors['community_activity']['weight'])
        
        # 페널티
        penalty_total = 0
        for penalty in penalties:
            if penalty in self.config['penalties']:
                penalty_total += self.config['penalties'][penalty]
        
        total_score += penalty_total
        breakdown['penalties'] = {
            'items': penalties,
            'total': penalty_total
        }
        
        # 범위 제한
        total_score = max(0.0, min(1.0, total_score))
        grade = self._get_grade(total_score)
        
        return {
            'spirit_score': round(total_score, 3),
            'breakdown': breakdown,
            'grade': grade,
            'calculated_at': datetime.now().isoformat()
        }
    
    def _get_grade(self, score: float) -> str:
        """점수에 따른 등급 부여"""
        if score >= 0.9:
            return 'S (Legendary)'
        elif score >= 0.8:
            return 'A (Excellent)'
        elif score >= 0.7:
            return 'B (Good)'
        elif score >= 0.6:
            return 'C (Average)'
        elif score >= 0.5:
            return 'D (Below Average)'
        else:
            return 'F (Poor)'
    
    def update_spirit_score_after_event(
        self,
        current_score: float,
        event_type: str,
        event_data: Dict
    ) -> Dict:
        """
        특정 이벤트 발생 후 Spirit Score 업데이트
        
        Args:
            current_score: 현재 Spirit Score
            event_type: 이벤트 유형 (investment_success, nft_sold, etc.)
            event_data: 이벤트 관련 데이터
        
        Returns:
            {
                'new_score': float,
                'change': float,
                'reason': str
            }
        """
        
        change = 0.0
        reason = ""
        
        if event_type == 'investment_success':
            change = 0.01
            reason = "투자 성공으로 인한 신뢰도 상승"
        
        elif event_type == 'investment_default':
            change = self.config['penalties']['investment_default']
            reason = "투자 계약 불이행"
        
        elif event_type == 'nft_positive_review':
            change = 0.005
            reason = "NFT 긍정 리뷰 획득"
        
        elif event_type == 'nft_fraud':
            change = self.config['penalties']['nft_fraud']
            reason = "NFT 사기 적발"
        
        elif event_type == 'collaboration_complete':
            exp_gained = event_data.get('experience_gained', 0)
            change = min(exp_gained / 100000, 0.02)  # 최대 0.02
            reason = f"협업 완료 (경험치 {exp_gained})"
        
        elif event_type == 'collaboration_abandon':
            change = self.config['penalties']['collaboration_abandon']
            reason = "협업 중도 포기"
        
        elif event_type == 'sponsor_contribution':
            amount = event_data.get('amount', 0)
            change = min(amount / 1000000, 0.01)  # 100만원당 0.01
            reason = f"시니어 후원 {amount:,}원"
        
        new_score = max(0.0, min(1.0, current_score + change))
        
        return {
            'new_score': round(new_score, 3),
            'change': round(change, 3),
            'reason': reason
        }


# ============================================
# 사용 예시
# ============================================

def demo_spirit_score():
    """Spirit Score 계산 데모"""
    
    print("\n" + "="*60)
    print("  Spirit Score Calculator Demo")
    print("="*60 + "\n")
    
    calculator = SpiritScoreCalculator()
    
    # Agent "김사과"의 Spirit Score 계산
    print("🤖 Agent '김사과' Spirit Score 계산")
    print("-" * 60)
    
    agent_score = calculator.calculate_agent_spirit_score(
        total_investments=5,
        successful_investments=4,
        nft_reviews_positive=8,
        nft_reviews_total=10,
        collaboration_experience=3500,
        sponsor_amount=74661,
        total_revenue=746614,
        challenge_participations=2,
        mentoring_sessions=1,
        penalties=[]
    )
    
    print(f"Spirit Score: {agent_score['spirit_score']} ({agent_score['grade']})")
    print(f"\n세부 내역:")
    for factor, data in agent_score['breakdown'].items():
        if factor != 'penalties':
            print(f"  - {factor}: {data['value']:.3f} (기여: {data['contribution']:.3f})")
        else:
            print(f"  - {factor}: {data['total']:.3f}")
    
    # 투자자 Spirit Score 계산
    print("\n" + "="*60)
    print("💰 투자자 '박준호' Spirit Score 계산")
    print("-" * 60)
    
    investor_score = calculator.calculate_investor_spirit_score(
        total_investments_made=3,
        successful_investments_made=3,
        nft_purchases=2,
        nft_purchase_reviews=2,
        collaboration_participations=1,
        sponsor_contribution=50000,
        total_invested_amount=3000000,
        community_votes=5,
        mentoring_received=0,
        penalties=[]
    )
    
    print(f"Spirit Score: {investor_score['spirit_score']} ({investor_score['grade']})")
    print(f"\n세부 내역:")
    for factor, data in investor_score['breakdown'].items():
        if factor != 'penalties':
            print(f"  - {factor}: {data['value']:.3f} (기여: {data['contribution']:.3f})")
    
    # 이벤트 후 업데이트
    print("\n" + "="*60)
    print("📊 이벤트 발생 후 Spirit Score 변화")
    print("-" * 60)
    
    current = agent_score['spirit_score']
    
    events = [
        ('investment_success', {}),
        ('nft_positive_review', {}),
        ('sponsor_contribution', {'amount': 100000})
    ]
    
    for event_type, event_data in events:
        update = calculator.update_spirit_score_after_event(
            current_score=current,
            event_type=event_type,
            event_data=event_data
        )
        
        print(f"\n이벤트: {event_type}")
        print(f"  이전: {current:.3f}")
        print(f"  변화: {update['change']:+.3f}")
        print(f"  이후: {update['new_score']:.3f}")
        print(f"  사유: {update['reason']}")
        
        current = update['new_score']
    
    print("\n" + "="*60)
    print("✅ Spirit Score 계산 완료!")
    print("="*60 + "\n")


if __name__ == "__main__":
    demo_spirit_score()

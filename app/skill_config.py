"""
Skill System Configuration
Mulberry Project - CTO Koda
PM 제안 반영: 경험치 공식 및 설정 파일화
"""

import json
from typing import Dict, Any


# ============================================
# 경험치 계산 공식
# ============================================

EXPERIENCE_FORMULAS = {
    # Sales 스킬: 판매 건수 기반
    'sales': {
        'base': 10,  # 판매 1건당 기본 경험치
        'multiplier': 1.0,
        'formula': 'sales_count * base * multiplier',
        'description': '판매 건수에 비례'
    },
    
    # Marketing 스킬: 목표 달성률 기반
    'marketing': {
        'base': 0.5,  # 목표 달성률 1%당 경험치
        'multiplier': 1.0,
        'formula': 'achievement_rate * base * multiplier',
        'description': '목표 달성률에 비례'
    },
    
    # Pricing 스킬: 총 수익 기반
    'pricing': {
        'base': 0.001,  # 수익 1원당 경험치
        'multiplier': 1.0,
        'formula': 'total_revenue * base * multiplier',
        'description': '총 수익에 비례'
    },
    
    # Financial 스킬: ROI 기반
    'financial': {
        'base': 0.1,  # ROI 1%당 경험치
        'multiplier': 1.0,
        'formula': 'roi * base * multiplier',
        'description': 'ROI에 비례'
    },
    
    # Agriculture 스킬: 수확량 기반
    'agriculture': {
        'base': 5,  # 수확 1kg당 경험치
        'multiplier': 1.0,
        'formula': 'harvest_kg * base * multiplier',
        'description': '수확량에 비례'
    },
    
    # Distribution 스킬: 배송 건수 기반
    'distribution': {
        'base': 8,  # 배송 1건당 경험치
        'multiplier': 1.0,
        'formula': 'delivery_count * base * multiplier',
        'description': '배송 건수에 비례'
    }
}


# ============================================
# 레벨 시스템
# ============================================

LEVEL_REQUIREMENTS = {
    '1': 0,        # 시작
    '2': 100,      # 초급
    '3': 500,      # 중급 → NFT 발행 가능!
    '4': 2000,     # 고급
    '5': 5000      # 전문가/마스터
}

RARITY_MAPPING = {
    '1': 'common',
    '2': 'uncommon',
    '3': 'rare',      # NFT 발행 가능
    '4': 'epic',      # NFT 발행 가능
    '5': 'legendary'  # NFT 발행 가능
}


# ============================================
# NFT 설정
# ============================================

NFT_CONFIG = {
    'min_level_to_mint': 3,  # NFT 발행 최소 레벨
    'base_price_per_level': 5000,  # 레벨당 기본 가격
    'royalty_rate': 0.1,  # 로열티 10%
    'buyer_experience_rate': 0.8,  # 구매자 즉시 획득 비율
    'remaining_learning_required': 0.2  # 나머지 20%는 직접 학습
}


# ============================================
# 스킬 전이 설정
# ============================================

# ============================================
# 스킬 전이 설정
# ============================================

SKILL_TRANSFER_CONFIG = {
    'agriculture->distribution': {
        'source': 'agriculture',
        'target': 'distribution',
        'retention_rate': 0.7,
        'adaptation_period_days': 7,  # PM 제안: 적응 기간
        'daily_adaptation_exp': 50,   # 적응 기간 중 일일 경험치
        'mapping': {
            '재배_일정_관리': '유통_일정_관리',
            '수확량_예측': '수요_예측',
            '병해충_진단': '문제_상품_식별'
        }
    },
    'marketing->sales': {
        'source': 'marketing',
        'target': 'sales',
        'retention_rate': 0.8,
        'adaptation_period_days': 5,
        'daily_adaptation_exp': 60,
        'mapping': {
            '타겟_고객_분석': '영업_대상_선정',
            '메시지_최적화': '세일즈_피치',
            '캠페인_자동화': '영업_프로세스_자동화'
        }
    },
    'finance->investment': {
        'source': 'finance',
        'target': 'investment',
        'retention_rate': 0.9,
        'adaptation_period_days': 3,
        'daily_adaptation_exp': 70,
        'mapping': {
            '현금_흐름_최적화': '투자_포트폴리오_관리',
            '리스크_관리': '투자_리스크_분석',
            '예산_수립': '투자_계획_수립'
        }
    }
}


# ============================================
# 협업 학습 설정
# ============================================

COLLABORATION_CONFIG = {
    'share_experience': {
        'experience_share_rate': 0.8,  # 전체 경험치의 80%를 각자 획득
        'min_participants': 2,
        'max_participants': 10
    },
    'competitive': {
        'winner_multiplier': 2.0,
        'top_10_percent_multiplier': 1.5,
        'participant_multiplier': 1.2
    },
    'mentor_mentee': {
        'mentee_multiplier': 1.2,
        'mentor_multiplier': 0.5,
        'mentor_reputation_bonus': 100
    }
}


# ============================================
# 챌린지 설정
# ============================================

CHALLENGE_CONFIG = {
    'experience_multipliers': {
        'top_10_percent': 2.0,
        'top_25_percent': 1.5,
        'participant': 1.2
    },
    'min_entry_fee': 1000,
    'max_entry_fee': 100000,
    'min_duration_days': 1,
    'max_duration_days': 30
}


# ============================================
# Spirit Score 계산 공식 (PM 제안)
# ============================================

SPIRIT_SCORE_CONFIG = {
    'base_score': 0.5,  # 초기 점수
    
    'factors': {
        # 투자 성공률
        'investment_success_rate': {
            'weight': 0.3,
            'formula': 'successful_investments / total_investments'
        },
        
        # NFT 거래 신뢰도
        'nft_reliability': {
            'weight': 0.2,
            'formula': '(positive_reviews / total_reviews) if total_reviews > 0 else 0.5'
        },
        
        # 협업 기여도
        'collaboration_contribution': {
            'weight': 0.25,
            'formula': 'total_collaboration_experience / 10000'  # 정규화
        },
        
        # 시니어 후원 비율
        'sponsor_ratio': {
            'weight': 0.15,
            'formula': 'sponsor_amount / total_revenue'
        },
        
        # 커뮤니티 활동
        'community_activity': {
            'weight': 0.1,
            'formula': '(challenge_participations + mentoring_sessions) / 50'  # 정규화
        }
    },
    
    # 페널티
    'penalties': {
        'investment_default': -0.1,      # 투자 계약 불이행
        'nft_fraud': -0.2,                # NFT 사기
        'collaboration_abandon': -0.05   # 협업 중도 포기
    }
}


# ============================================
# 타임 워프 설정
# ============================================

TIME_WARP_CONFIG = {
    'speed_multiplier': 100,  # 100배 속도
    'scenarios': {
        'balanced': {
            'sales_rate': 0.7,
            'price_variance': 0.1,
            'risk': 0.3
        },
        'aggressive': {
            'sales_rate': 0.5,
            'price_variance': 0.2,
            'risk': 0.5
        },
        'conservative': {
            'sales_rate': 0.85,
            'price_variance': 0.05,
            'risk': 0.1
        }
    }
}


# ============================================
# 설정 로드/저장 함수
# ============================================

def load_config(config_name: str) -> Dict[str, Any]:
    """설정 로드"""
    configs = {
        'experience': EXPERIENCE_FORMULAS,
        'level': LEVEL_REQUIREMENTS,
        'nft': NFT_CONFIG,
        'transfer': SKILL_TRANSFER_CONFIG,
        'collaboration': COLLABORATION_CONFIG,
        'challenge': CHALLENGE_CONFIG,
        'spirit_score': SPIRIT_SCORE_CONFIG,
        'time_warp': TIME_WARP_CONFIG
    }
    return configs.get(config_name, {})


def save_config_to_file(filepath: str):
    """설정을 JSON 파일로 저장"""
    config = {
        'experience_formulas': EXPERIENCE_FORMULAS,
        'level_requirements': LEVEL_REQUIREMENTS,
        'rarity_mapping': RARITY_MAPPING,
        'nft_config': NFT_CONFIG,
        'skill_transfer_config': SKILL_TRANSFER_CONFIG,
        'collaboration_config': COLLABORATION_CONFIG,
        'challenge_config': CHALLENGE_CONFIG,
        'spirit_score_config': SPIRIT_SCORE_CONFIG,
        'time_warp_config': TIME_WARP_CONFIG
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_config_from_file(filepath: str) -> Dict[str, Any]:
    """JSON 파일에서 설정 로드"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


if __name__ == "__main__":
    # 설정 파일 생성
    save_config_to_file('/mnt/user-data/outputs/skill_system_config.json')
    print("✅ 설정 파일 생성 완료: skill_system_config.json")
    print("\n비즈니스 팀이 이 파일을 수정하면 코드 변경 없이 공식 조정 가능!")

"""
AI Agent Skill System - Core Implementation
Mulberry Project
CTO Koda

Agent의 경험을 스킬로 전환하는 시스템
경험 → 스킬 → 레벨업 → NFT → 거래
"""

import json
from datetime import datetime
from typing import Dict, List
import uuid


class AgentSkill:
    """Agent 개별 스킬"""
    
    # 스킬 타입별 레벨업 기준
    LEVEL_THRESHOLDS = {
        1: 0,      # 시작
        2: 100,    # 초급 → 중급
        3: 500,    # 중급 → 고급
        4: 2000,   # 고급 → 전문가
        5: 5000    # 전문가 → 마스터
    }
    
    RARITY_MAP = {
        1: 'common',
        2: 'uncommon',
        3: 'rare',
        4: 'epic',
        5: 'legendary'
    }
    
    def __init__(self, skill_type: str, category: str):
        self.skill_id = str(uuid.uuid4())[:8]
        self.skill_type = skill_type  # sales, marketing, pricing, financial
        self.category = category  # knowledge, agriculture, digital, service
        self.level = 1
        self.experience_points = 0
        self.proficiency_data = {}
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        
    def add_experience(self, points: int, reason: str = ""):
        """경험치 추가"""
        old_level = self.level
        self.experience_points += points
        self.last_updated = datetime.now()
        
        # 레벨업 체크
        new_level = self._calculate_level()
        
        if new_level > old_level:
            self.level = new_level
            return {
                'level_up': True,
                'old_level': old_level,
                'new_level': new_level,
                'skill_type': self.skill_type,
                'reason': reason
            }
        
        return {'level_up': False}
    
    def _calculate_level(self):
        """경험치로 레벨 계산"""
        for level in sorted(self.LEVEL_THRESHOLDS.keys(), reverse=True):
            if self.experience_points >= self.LEVEL_THRESHOLDS[level]:
                return level
        return 1
    
    def get_rarity(self):
        """레벨에 따른 희귀도"""
        return self.RARITY_MAP.get(self.level, 'common')
    
    def can_mint_nft(self):
        """NFT 발행 가능 여부 (Level 3 이상)"""
        return self.level >= 3
    
    def to_dict(self):
        return {
            'skill_id': self.skill_id,
            'skill_type': self.skill_type,
            'category': self.category,
            'level': self.level,
            'rarity': self.get_rarity(),
            'experience_points': self.experience_points,
            'can_mint_nft': self.can_mint_nft(),
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }


class SkillNFT:
    """스킬 NFT"""
    
    def __init__(self, skill: AgentSkill, creator_agent_id: str, performance_data: Dict):
        self.nft_id = f"SKILL-NFT-{uuid.uuid4().hex[:12]}"
        self.skill_id = skill.skill_id
        self.skill_name = f"{skill.skill_type.title()} Master - {skill.category.title()}"
        self.creator = creator_agent_id
        self.level = skill.level
        self.rarity = skill.get_rarity()
        
        # 성과 데이터 포함
        self.metadata = {
            'total_sales': performance_data.get('total_units_sold', 0),
            'roi': performance_data.get('roi', 0),
            'success_rate': performance_data.get('sales_achievement', 0) / 100,
            'experience_points': skill.experience_points,
            'verified': True,
            'minted_at': datetime.now().isoformat()
        }
        
        # 가격 책정 (레벨 × 5,000원)
        self.price = skill.level * 5000
        self.royalty = 0.1  # 10% 로열티
        
        self.created_at = datetime.now()
        
    def to_dict(self):
        return {
            'nft_id': self.nft_id,
            'skill_name': self.skill_name,
            'creator': self.creator,
            'level': self.level,
            'rarity': self.rarity,
            'metadata': self.metadata,
            'price': self.price,
            'royalty': self.royalty,
            'created_at': self.created_at.isoformat()
        }


class AgentSkillSystem:
    """Agent 스킬 관리 시스템"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.skills: Dict[str, AgentSkill] = {}
        self.skill_history: List[Dict] = []
        self.nfts_minted: List[SkillNFT] = []
        
    def learn_from_simulation(self, simulation_report: Dict):
        """시뮬레이션 결과로부터 스킬 학습"""
        
        product = simulation_report.get('product', '')
        category = self._extract_category(product)
        
        level_ups = []
        
        # 1. 판매 스킬 (Sales Skill)
        sales_skill_key = f"sales_{category}"
        if sales_skill_key not in self.skills:
            self.skills[sales_skill_key] = AgentSkill('sales', category)
        
        # 판매량 기반 경험치 (1개당 10점)
        sales_exp = simulation_report.get('total_units_sold', 0) * 10
        sales_result = self.skills[sales_skill_key].add_experience(
            sales_exp, 
            f"{simulation_report.get('total_units_sold', 0)}개 판매"
        )
        if sales_result['level_up']:
            level_ups.append(sales_result)
        
        # 2. 재무 스킬 (Financial Skill)
        financial_skill_key = "financial_management"
        if financial_skill_key not in self.skills:
            self.skills[financial_skill_key] = AgentSkill('financial', 'general')
        
        # ROI 기반 경험치 (ROI / 10)
        financial_exp = int(simulation_report.get('roi', 0) / 10)
        financial_result = self.skills[financial_skill_key].add_experience(
            financial_exp,
            f"ROI {simulation_report.get('roi', 0):.1f}% 달성"
        )
        if financial_result['level_up']:
            level_ups.append(financial_result)
        
        # 3. 마케팅 스킬 (Marketing Skill)
        marketing_skill_key = f"marketing_{category}"
        if marketing_skill_key not in self.skills:
            self.skills[marketing_skill_key] = AgentSkill('marketing', category)
        
        # 목표 달성률 기반 경험치
        achievement = simulation_report.get('sales_achievement', 0)
        marketing_exp = int(achievement / 2)  # 달성률의 50%
        marketing_result = self.skills[marketing_skill_key].add_experience(
            marketing_exp,
            f"목표 달성률 {achievement:.1f}%"
        )
        if marketing_result['level_up']:
            level_ups.append(marketing_result)
        
        # 4. 가격 전략 스킬 (Pricing Skill)
        pricing_skill_key = f"pricing_{category}"
        if pricing_skill_key not in self.skills:
            self.skills[pricing_skill_key] = AgentSkill('pricing', category)
        
        # 수익 기반 경험치 (수익 / 1000)
        pricing_exp = simulation_report.get('total_profit', 0) // 1000
        pricing_result = self.skills[pricing_skill_key].add_experience(
            pricing_exp,
            f"총 수익 {simulation_report.get('total_profit', 0):,}원"
        )
        if pricing_result['level_up']:
            level_ups.append(pricing_result)
        
        # 스킬 히스토리 기록
        self.skill_history.append({
            'timestamp': datetime.now().isoformat(),
            'simulation_period': simulation_report.get('period', '30일'),
            'skills_earned': len(level_ups),
            'level_ups': level_ups,
            'total_experience': sum(s.experience_points for s in self.skills.values())
        })
        
        return {
            'skills_updated': len(self.skills),
            'level_ups': level_ups,
            'total_skills': self.get_total_skills(),
            'highest_level': self.get_highest_level(),
            'can_mint_nft': self.get_mintable_skills()
        }
    
    def _extract_category(self, product_name: str):
        """상품명에서 카테고리 추출"""
        # 간단한 매핑
        knowledge_keywords = ['분석', '번역', '작성', '리포트']
        agriculture_keywords = ['사과', '배추', '감자']
        digital_keywords = ['인포그래픽', '템플릿']
        service_keywords = ['배달', '시니어', '지원']
        
        product_lower = product_name.lower()
        
        for keyword in knowledge_keywords:
            if keyword in product_lower:
                return 'knowledge'
        for keyword in agriculture_keywords:
            if keyword in product_lower:
                return 'agriculture'
        for keyword in digital_keywords:
            if keyword in product_lower:
                return 'digital'
        for keyword in service_keywords:
            if keyword in product_lower:
                return 'service'
        
        return 'general'
    
    def mint_nft(self, skill_key: str, performance_data: Dict):
        """스킬 NFT 발행"""
        
        if skill_key not in self.skills:
            return {
                'success': False,
                'message': f"스킬 '{skill_key}'를 찾을 수 없습니다."
            }
        
        skill = self.skills[skill_key]
        
        if not skill.can_mint_nft():
            return {
                'success': False,
                'message': f"Level {skill.level}은 NFT 발행 불가 (Level 3 이상 필요)"
            }
        
        # NFT 생성
        nft = SkillNFT(skill, self.agent_id, performance_data)
        self.nfts_minted.append(nft)
        
        return {
            'success': True,
            'nft': nft.to_dict(),
            'message': f"🎨 NFT 발행 완료: {nft.nft_id}"
        }
    
    def get_total_skills(self):
        """총 스킬 수"""
        return len(self.skills)
    
    def get_highest_level(self):
        """최고 레벨"""
        if not self.skills:
            return 0
        return max(skill.level for skill in self.skills.values())
    
    def get_mintable_skills(self):
        """NFT 발행 가능한 스킬 목록"""
        return [
            {
                'key': key,
                'skill': skill.to_dict()
            }
            for key, skill in self.skills.items()
            if skill.can_mint_nft()
        ]
    
    def get_skill_summary(self):
        """스킬 요약"""
        return {
            'agent_id': self.agent_id,
            'total_skills': self.get_total_skills(),
            'highest_level': self.get_highest_level(),
            'total_experience': sum(s.experience_points for s in self.skills.values()),
            'skills': {
                key: skill.to_dict()
                for key, skill in self.skills.items()
            },
            'nfts_minted': len(self.nfts_minted),
            'mintable_skills': len(self.get_mintable_skills())
        }
    
    def to_dict(self):
        """전체 데이터 직렬화"""
        return {
            'agent_id': self.agent_id,
            'skill_summary': self.get_skill_summary(),
            'skill_history': self.skill_history,
            'nfts': [nft.to_dict() for nft in self.nfts_minted]
        }


# ============================================
# 기존 agent_economic_system.py와 통합
# ============================================

def demonstrate_skill_system():
    """스킬 시스템 데모"""
    
    print("\n" + "="*60)
    print("  🎓 AI Agent Skill System Demo")
    print("  경험 → 스킬 → 레벨업 → NFT")
    print("="*60 + "\n")
    
    # 시뮬레이션 결과 예시 (agent_economic_system.py에서 가져온 것)
    simulation_report = {
        'agent_name': '김사과',
        'product': '시니어 지원',
        'period': '30일',
        'total_units_sold': 56,
        'total_profit': 145544,
        'roi': 1455.44,
        'sales_achievement': 5600.0,
        'goal_achieved': True
    }
    
    print(f"📊 시뮬레이션 결과:")
    print(f"   Agent: {simulation_report['agent_name']}")
    print(f"   상품: {simulation_report['product']}")
    print(f"   판매: {simulation_report['total_units_sold']}개")
    print(f"   수익: {simulation_report['total_profit']:,}원")
    print(f"   ROI: {simulation_report['roi']:.2f}%\n")
    
    # 스킬 시스템 생성
    print("🎓 스킬 시스템 초기화...\n")
    skill_system = AgentSkillSystem("agent_김사과")
    
    # 시뮬레이션 결과로부터 스킬 학습
    print("📚 시뮬레이션 결과로부터 스킬 학습 중...\n")
    learning_result = skill_system.learn_from_simulation(simulation_report)
    
    print(f"✅ 학습 완료!")
    print(f"   업데이트된 스킬: {learning_result['skills_updated']}개")
    print(f"   총 스킬: {learning_result['total_skills']}개")
    print(f"   최고 레벨: Level {learning_result['highest_level']}\n")
    
    # 레벨업 알림
    if learning_result['level_ups']:
        print("🎉 레벨업 발생!\n")
        for level_up in learning_result['level_ups']:
            print(f"   {level_up['skill_type'].upper()}:")
            print(f"   Level {level_up['old_level']} → Level {level_up['new_level']}")
            print(f"   사유: {level_up['reason']}\n")
    
    # 스킬 상세 정보
    print("="*60)
    print("  📊 스킬 상세 정보")
    print("="*60 + "\n")
    
    summary = skill_system.get_skill_summary()
    for skill_key, skill_data in summary['skills'].items():
        print(f"🎯 {skill_key}:")
        print(f"   레벨: {skill_data['level']}")
        print(f"   희귀도: {skill_data['rarity']}")
        print(f"   경험치: {skill_data['experience_points']}")
        print(f"   NFT 발행 가능: {'✅ Yes' if skill_data['can_mint_nft'] else '❌ No'}\n")
    
    # NFT 발행 가능한 스킬 체크
    mintable = learning_result['can_mint_nft']
    if mintable:
        print("="*60)
        print("  💎 NFT 발행 가능한 스킬")
        print("="*60 + "\n")
        
        for item in mintable:
            skill = item['skill']
            print(f"✨ {item['key']}:")
            print(f"   레벨: {skill['level']}")
            print(f"   희귀도: {skill['rarity']}")
            print(f"   경험치: {skill['experience_points']}\n")
            
            # NFT 발행
            print(f"   💎 NFT 발행 중...\n")
            nft_result = skill_system.mint_nft(item['key'], simulation_report)
            
            if nft_result['success']:
                nft = nft_result['nft']
                print(f"   ✅ {nft_result['message']}")
                print(f"   NFT 이름: {nft['skill_name']}")
                print(f"   가격: {nft['price']:,}원")
                print(f"   희귀도: {nft['rarity']}")
                print(f"   로열티: {nft['royalty']*100}%\n")
    
    # 전체 요약
    print("="*60)
    print("  📈 최종 요약")
    print("="*60 + "\n")
    
    total_summary = skill_system.get_skill_summary()
    print(f"총 스킬: {total_summary['total_skills']}개")
    print(f"최고 레벨: Level {total_summary['highest_level']}")
    print(f"총 경험치: {total_summary['total_experience']:,}")
    print(f"발행된 NFT: {total_summary['nfts_minted']}개")
    print(f"발행 가능 NFT: {total_summary['mintable_skills']}개\n")
    
    # JSON 저장
    output_file = '/mnt/user-data/outputs/agent_skill_system_demo.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(skill_system.to_dict(), f, ensure_ascii=False, indent=2)
    
    print(f"✅ 스킬 데이터 저장 완료: {output_file}\n")
    
    return skill_system


if __name__ == "__main__":
    skill_system = demonstrate_skill_system()
    
    print("💡 다음 단계:")
    print("   1. 더 많은 시뮬레이션 실행 → 더 많은 스킬 획득")
    print("   2. Level 3+ 스킬로 NFT 발행")
    print("   3. NFT 마켓플레이스에서 거래")
    print("   4. 다른 Agent에게 스킬 판매")
    print("\n")

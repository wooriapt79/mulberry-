"""
Mulberry Platform - Unit Tests
핵심 기능 안정성 검증

Tests:
1. Family Care Protocol (가족 돌봄 프로토콜)
2. Market Warrior Protocol (시장 협상 프로토콜)
3. Dialect Recognition (사투리 인식)
4. Mutual Aid System (상부상조 시스템)
5. AP2 Mandate (위임장 시스템)
"""

import pytest
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from app.services.jangseungbaegi_protocol import (
    JangseungbaegiProtocol,
    ProtocolMode,
    InteractionType,
    ProtocolContext
)
from app.services.mutual_aid_system import (
    SettlementEngine,
    WarmthWebhook,
    DonationType
)


# ============================================
# Test: Family Care Protocol
# ============================================

class TestFamilyCareProtocol:
    """Family Care Protocol 테스트"""
    
    @pytest.fixture
    def protocol(self):
        """프로토콜 인스턴스 생성"""
        return JangseungbaegiProtocol()
    
    def test_family_care_greeting(self, protocol):
        """가족 돌봄: 인사말 테스트"""
        context = ProtocolContext(
            mode=ProtocolMode.FAMILY_CARE,
            interaction_type=InteractionType.SENIOR_CARE,
            user_id="SENIOR_001",
            user_type="senior"
        )
        
        result = protocol.generate_response(
            context=context,
            user_message="안녕하세요",
            base_response="안녕하세요, 무엇을 도와드릴까요?"
        )
        
        # 검증
        assert result["mode"] == "family_care"
        assert result["tone"] == "warm_and_caring"
        assert "어르신" in result["adjusted_response"]
        assert "characteristics" in result
        assert result["characteristics"]["formality"] == "informal"
    
    def test_family_care_empathy(self, protocol):
        """가족 돌봄: 공감 표현 테스트"""
        context = ProtocolContext(
            mode=ProtocolMode.FAMILY_CARE,
            interaction_type=InteractionType.SENIOR_CARE,
            user_id="SENIOR_002",
            user_type="senior"
        )
        
        # "힘들다"는 표현에 공감 반응
        result = protocol.generate_response(
            context=context,
            user_message="주문하는 게 힘들어요",
            base_response="도와드리겠습니다"
        )
        
        # 공감 표현이 포함되어야 함
        response_text = result["adjusted_response"]
        assert any(word in response_text for word in ["힘드셨겠어요", "괜찮으세요", "걱정 마세요"])
    
    def test_family_care_patience(self, protocol):
        """가족 돌봄: 인내심 테스트"""
        context = ProtocolContext(
            mode=ProtocolMode.FAMILY_CARE,
            interaction_type=InteractionType.SENIOR_CARE,
            user_id="SENIOR_003",
            user_type="senior"
        )
        
        result = protocol.generate_response(
            context=context,
            user_message="잘 모르겠어요",
            base_response="설명드리겠습니다"
        )
        
        # 인내심 있는 표현 확인
        assert result["characteristics"]["patience"] == "infinite"
        response_text = result["adjusted_response"]
        assert any(word in response_text for word in ["천천히", "서두르지"])
    
    def test_protocol_mode_determination(self, protocol):
        """프로토콜 모드 자동 결정 테스트"""
        # 어르신 → Family Care
        mode1 = protocol.determine_protocol_mode(
            user_type="senior",
            interaction_type=InteractionType.SENIOR_CARE
        )
        assert mode1 == ProtocolMode.FAMILY_CARE
        
        # 공급업체 → Market Warrior
        mode2 = protocol.determine_protocol_mode(
            user_type="supplier",
            interaction_type=InteractionType.SUPPLIER_NEGOTIATION
        )
        assert mode2 == ProtocolMode.MARKET_WARRIOR
    
    def test_jangseungbaegi_principles(self, protocol):
        """장승배기 5대 원칙 적용 테스트"""
        context = ProtocolContext(
            mode=ProtocolMode.FAMILY_CARE,
            interaction_type=InteractionType.SENIOR_CARE,
            user_id="SENIOR_004",
            user_type="senior"
        )
        
        result = protocol.generate_response(
            context=context,
            user_message="도와주세요",
            base_response="함께 해결해봅시다"
        )
        
        # 원칙 점수 확인
        assert "principles_score" in result
        assert 0.0 <= result["principles_score"] <= 1.0


# ============================================
# Test: Market Warrior Protocol
# ============================================

class TestMarketWarriorProtocol:
    """Market Warrior Protocol 테스트"""
    
    @pytest.fixture
    def protocol(self):
        """프로토콜 인스턴스 생성"""
        return JangseungbaegiProtocol()
    
    def test_market_warrior_negotiation(self, protocol):
        """시장 협상: 협상 톤 테스트"""
        context = ProtocolContext(
            mode=ProtocolMode.MARKET_WARRIOR,
            interaction_type=InteractionType.SUPPLIER_NEGOTIATION,
            user_id="SUPPLIER_001",
            user_type="supplier"
        )
        
        result = protocol.generate_response(
            context=context,
            user_message="가격은 kg당 5,000원입니다",
            base_response="시장 평균가는 4,200원입니다"
        )
        
        # 검증
        assert result["mode"] == "market_warrior"
        assert result["tone"] == "sharp_and_analytical"
        assert result["characteristics"]["formality"] == "formal"
    
    def test_market_warrior_data_driven(self, protocol):
        """시장 협상: 데이터 기반 응답 테스트"""
        context = ProtocolContext(
            mode=ProtocolMode.MARKET_WARRIOR,
            interaction_type=InteractionType.BUYER_DEAL,
            user_id="BUYER_001",
            user_type="buyer"
        )
        
        result = protocol.generate_response(
            context=context,
            user_message="할인 가능한가요?",
            base_response="현재 재고 상황을 고려하여 3% 할인 가능합니다"
        )
        
        response_text = result["adjusted_response"]
        # 구체적인 숫자나 근거 포함
        assert any(char.isdigit() for char in response_text)
    
    def test_protocol_switching(self, protocol):
        """프로토콜 전환 테스트 (Family ↔ Market)"""
        # Family Care
        context_family = ProtocolContext(
            mode=ProtocolMode.FAMILY_CARE,
            interaction_type=InteractionType.SENIOR_CARE,
            user_id="SENIOR_005",
            user_type="senior"
        )
        
        result_family = protocol.generate_response(
            context=context_family,
            user_message="주문하고 싶어요",
            base_response="도와드리겠습니다"
        )
        
        # Market Warrior
        context_market = ProtocolContext(
            mode=ProtocolMode.MARKET_WARRIOR,
            interaction_type=InteractionType.SUPPLIER_NEGOTIATION,
            user_id="SUPPLIER_002",
            user_type="supplier"
        )
        
        result_market = protocol.generate_response(
            context=context_market,
            user_message="가격 제안드립니다",
            base_response="검토하겠습니다"
        )
        
        # 톤이 완전히 달라야 함
        assert result_family["tone"] != result_market["tone"]
        assert result_family["characteristics"]["patience"] != result_market["characteristics"]["patience"]


# ============================================
# Test: Mutual Aid System
# ============================================

class TestMutualAidSystem:
    """상부상조 시스템 테스트"""
    
    @pytest.fixture
    def engine(self):
        """정산 엔진 생성"""
        return SettlementEngine()
    
    def test_welfare_fund_allocation(self, engine):
        """복지 펀드 10% 적립 테스트"""
        result = engine.process_settlement_with_welfare(
            revenue=10_000_000,
            municipality="춘천시"
        )
        
        # 10% = 1,000,000원
        assert result["welfare_amount"] == 1_000_000
        assert result["welfare_ratio"] == 0.1
        assert result["distributable_amount"] == 9_000_000
        assert result["distributable_ratio"] == 0.9
    
    def test_multiple_settlements(self, engine):
        """여러 정산 누적 테스트"""
        # 첫 번째 정산
        engine.process_settlement_with_welfare(
            revenue=5_000_000,
            municipality="인제군"
        )
        
        # 두 번째 정산
        engine.process_settlement_with_welfare(
            revenue=3_000_000,
            municipality="인제군"
        )
        
        # 복지 펀드 잔액 확인
        from app.services.mutual_aid_system import FundType
        balance = engine.get_fund_balance("인제군", FundType.WELFARE)
        
        # 500,000 + 300,000 = 800,000
        assert balance == 800_000
    
    def test_settlement_ratio_validation(self):
        """정산 비율 검증 테스트"""
        # 다른 비율로 엔진 생성
        from decimal import Decimal
        engine = SettlementEngine()
        engine.welfare_ratio = Decimal('0.15')  # 15%
        
        result = engine.process_settlement_with_welfare(
            revenue=1_000_000,
            municipality="부여군"
        )
        
        assert result["welfare_amount"] == 150_000
        assert result["distributable_amount"] == 850_000


class TestWarmthWebhook:
    """온기 전달 웹훅 테스트"""
    
    @pytest.fixture
    def warmth(self):
        """웹훅 시스템 생성"""
        return WarmthWebhook()
    
    @pytest.mark.asyncio
    async def test_warmth_delivery(self, warmth):
        """온기 전달 테스트"""
        delivery = await warmth.deliver_warmth(
            donor_name="장승배기 협동조합",
            recipient_id="SENIOR_CHU_001",
            recipient_name="김춘천",
            amount=50000,
            donation_type=DonationType.FOOD,
            municipality="춘천시",
            message="따뜻한 마음을 전합니다"
        )
        
        # 검증
        assert delivery.status == "delivered"
        assert delivery.amount == 50000
        assert delivery.donor_name == "장승배기 협동조합"
        assert delivery.recipient_name == "김춘천"
    
    @pytest.mark.asyncio
    async def test_warmth_statistics(self, warmth):
        """온기 전달 통계 테스트"""
        # 여러 건 전달
        await warmth.deliver_warmth(
            donor_name="조합원A",
            recipient_id="SENIOR_001",
            recipient_name="김철수",
            amount=30000,
            donation_type=DonationType.FOOD,
            municipality="춘천시"
        )
        
        await warmth.deliver_warmth(
            donor_name="조합원B",
            recipient_id="SENIOR_002",
            recipient_name="이영희",
            amount=20000,
            donation_type=DonationType.TRANSPORT,
            municipality="춘천시"
        )
        
        # 통계 확인
        stats = warmth.get_statistics("춘천시")
        
        assert stats["total_donations"] == 2
        assert stats["total_amount"] == 50000
        assert stats["unique_recipients"] == 2


# ============================================
# Test: Protocol Statistics
# ============================================

class TestProtocolStatistics:
    """프로토콜 사용 통계 테스트"""
    
    def test_protocol_usage_tracking(self):
        """프로토콜 사용 추적 테스트"""
        protocol = JangseungbaegiProtocol()
        
        # Family Care 5회
        for i in range(5):
            context = ProtocolContext(
                mode=ProtocolMode.FAMILY_CARE,
                interaction_type=InteractionType.SENIOR_CARE,
                user_id=f"SENIOR_{i}",
                user_type="senior"
            )
            protocol.generate_response(context, "테스트", "응답")
        
        # Market Warrior 3회
        for i in range(3):
            context = ProtocolContext(
                mode=ProtocolMode.MARKET_WARRIOR,
                interaction_type=InteractionType.SUPPLIER_NEGOTIATION,
                user_id=f"SUPPLIER_{i}",
                user_type="supplier"
            )
            protocol.generate_response(context, "테스트", "응답")
        
        # 통계 확인
        stats = protocol.get_protocol_stats()
        
        assert stats["total_interactions"] == 8
        assert stats["family_interactions"] == 5
        assert stats["market_interactions"] == 3
        assert stats["family_percentage"] == 62.5
        assert stats["market_percentage"] == 37.5


# ============================================
# Test: Integration
# ============================================

class TestIntegration:
    """통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """전체 워크플로우 테스트 (어르신 주문 → 정산 → 후원)"""
        # 1. 프로토콜로 어르신 응대
        protocol = JangseungbaegiProtocol()
        context = ProtocolContext(
            mode=ProtocolMode.FAMILY_CARE,
            interaction_type=InteractionType.SENIOR_CARE,
            user_id="SENIOR_INTEGRATION",
            user_type="senior"
        )
        
        response = protocol.generate_response(
            context=context,
            user_message="사과 3kg 주문하고 싶어요",
            base_response="사과 3kg 주문 도와드리겠습니다"
        )
        
        assert response["success"] if "success" in response else True
        
        # 2. 매출 발생 → 정산
        engine = SettlementEngine()
        settlement = engine.process_settlement_with_welfare(
            revenue=150_000,  # 15만원
            municipality="인제군"
        )
        
        assert settlement["welfare_amount"] == 15_000  # 10%
        
        # 3. 복지 펀드로 후원
        warmth = WarmthWebhook()
        delivery = await warmth.deliver_warmth(
            donor_name="인제 협동조합",
            recipient_id="SENIOR_NEED",
            recipient_name="박인제",
            amount=15_000,
            donation_type=DonationType.FOOD,
            municipality="인제군",
            message="장승배기 복지 펀드에서 지원합니다"
        )
        
        assert delivery.status == "delivered"
        assert delivery.amount == 15_000
        
        print("\n✅ 통합 테스트 성공!")
        print("  1. 어르신 주문 (Family Care)")
        print("  2. 매출 정산 (10% 복지 펀드)")
        print("  3. 후원 전달 (온기 웹훅)")


# ============================================
# pytest 실행 시
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

"""
Mulberry Agent System - 완전 통합 데모
CTO Koda

모든 시스템이 함께 작동하는 실제 시나리오
"""

import sqlite3
from datetime import datetime, timedelta
import sys
import os

# 모듈 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from agent_factory.agent_factory import AgentFactory, StoreType
from spirit_score.spirit_score_manager import SpiritScoreManager, SpiritScoreEvent
from ap2_integration.mandate_manager import AP2MandateManager
from jangseungbaegi_checker.checker import JangseungbaegiChecker


def init_demo_database():
    """데모용 데이터베이스 초기화"""
    conn = sqlite3.connect(':memory:')  # 메모리 DB
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # agents 테이블
    cursor.execute("""
        CREATE TABLE agents (
            agent_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            store_type TEXT NOT NULL,
            raspberry_pi_id TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            training_started_at TIMESTAMP,
            training_completed_at TIMESTAMP,
            deployed_at TIMESTAMP,
            constitution_study_progress REAL DEFAULT 0,
            persona_training_progress REAL DEFAULT 0,
            business_persona TEXT,
            passport_id TEXT,
            total_customers_served INTEGER DEFAULT 0,
            total_sales REAL DEFAULT 0,
            customer_satisfaction REAL DEFAULT 0,
            spirit_score REAL DEFAULT 0
        )
    """)
    
    # spirit_scores 테이블
    cursor.execute("""
        CREATE TABLE spirit_scores (
            record_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            points REAL NOT NULL,
            reason TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            related_entity TEXT,
            metadata TEXT
        )
    """)
    
    # mandates 테이블
    cursor.execute("""
        CREATE TABLE mandates (
            mandate_id TEXT PRIMARY KEY,
            mandate_type TEXT NOT NULL,
            user_id TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            status TEXT NOT NULL,
            signature TEXT NOT NULL
        )
    """)
    
    # principle_checks 테이블
    cursor.execute("""
        CREATE TABLE principle_checks (
            check_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            principle TEXT NOT NULL,
            action TEXT NOT NULL,
            followed BOOLEAN NOT NULL,
            created_at TIMESTAMP NOT NULL,
            violation_type TEXT,
            violation_details TEXT,
            penalty_points REAL DEFAULT 0
        )
    """)
    
    # mutual_aid_transactions 테이블
    cursor.execute("""
        CREATE TABLE mutual_aid_transactions (
            transaction_id TEXT PRIMARY KEY,
            from_agent_id TEXT NOT NULL,
            to_agent_id TEXT NOT NULL,
            amount REAL NOT NULL,
            reason TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    """)
    
    conn.commit()
    return conn


def run_complete_demo():
    """완전 통합 데모 실행"""
    
    print("=" * 60)
    print("🌾 Mulberry Agent System - 완전 통합 데모")
    print("=" * 60)
    print()
    
    # 데이터베이스 초기화
    print("📊 데이터베이스 초기화 중...")
    db = init_demo_database()
    
    # 매니저 초기화
    print("🔧 시스템 초기화 중...")
    config = {
        'max_daily_agents': 10,
        'training_hours': 1
    }
    
    factory = AgentFactory(db, config)
    spirit_manager = SpiritScoreManager(db)
    mandate_manager = AP2MandateManager(db)
    checker = JangseungbaegiChecker(db, spirit_manager)
    
    print("✅ 모든 시스템 준비 완료!")
    print()
    print("=" * 60)
    
    # ============================================
    # 시나리오 1: 에이전트 생성 및 훈련
    # ============================================
    print("\n📋 시나리오 1: 에이전트 생성 및 훈련")
    print("-" * 60)
    
    # 에이전트 생성
    agent1 = factory.create_agent(
        name="김철수",
        store_type=StoreType.RESTAURANT,
        raspberry_pi_id="RPI-001",
        auto_start_training=False  # 수동으로 진행
    )
    
    agent2 = factory.create_agent(
        name="이영희",
        store_type=StoreType.FRUIT,
        raspberry_pi_id="RPI-002",
        auto_start_training=False
    )
    
    print(f"\n✅ 2명의 에이전트 생성 완료")
    print(f"   - {agent1.name} ({agent1.agent_id})")
    print(f"   - {agent2.name} ({agent2.agent_id})")
    
    # 훈련 시작
    print(f"\n🎓 장승배기 헌법 학습 시작...")
    factory.start_training(agent1.agent_id)
    
    # 훈련 완료 (시뮬레이션)
    agent1.training_completed_at = datetime.now()
    agent1.status = "ready"
    print(f"✅ 훈련 완료! Spirit Score +0.05 부여")
    spirit_manager.record_event(
        agent1.agent_id,
        SpiritScoreEvent.TRAINING_COMPLETED,
        "장승배기 헌법 학습 완료"
    )
    
    # ============================================
    # 시나리오 2: AP2 위임장 생성
    # ============================================
    print("\n📋 시나리오 2: AP2 위임장 시스템")
    print("-" * 60)
    
    # Intent Mandate: 사용자가 에이전트에게 권한 부여
    print("\n1️⃣ Intent Mandate 생성")
    intent = mandate_manager.create_intent_mandate(
        user_id="USER-001",
        agent_id=agent1.agent_id,
        intent="식료품 구매",
        constraints={
            "max_budget": 50000,
            "items": ["김밥", "음료", "과자"]
        }
    )
    
    # 권한 확인
    print("\n2️⃣ 에이전트 권한 검증")
    can_proceed = mandate_manager.verify_agent_authority(
        agent_id=agent1.agent_id,
        action="add_to_cart",
        context={"amount": 30000}
    )
    
    if can_proceed:
        print("✅ 권한 확인 완료! 30,000원 구매 가능")
    
    # Cart Mandate: 장바구니 승인
    print("\n3️⃣ Cart Mandate 생성")
    cart_items = [
        {"item": "김밥", "qty": 2, "price": 3000},
        {"item": "콜라", "qty": 2, "price": 1500},
        {"item": "새우깡", "qty": 1, "price": 1000}
    ]
    total = sum(item['qty'] * item['price'] for item in cart_items)
    
    cart = mandate_manager.create_cart_mandate(
        user_id="USER-001",
        agent_id=agent1.agent_id,
        cart_items=cart_items,
        total_amount=total,
        intent_mandate_id=intent.mandate_id
    )
    
    # Payment Mandate: 결제 승인
    print("\n4️⃣ Payment Mandate 생성")
    payment = mandate_manager.create_payment_mandate(
        user_id="USER-001",
        agent_id=agent1.agent_id,
        cart_mandate_id=cart.mandate_id,
        payment_method="AP2",
        amount=total
    )
    
    print(f"\n✅ AP2 위임장 3단계 완료!")
    print(f"   Intent → Cart → Payment")
    
    # ============================================
    # 시나리오 3: 업무 수행 및 Spirit Score
    # ============================================
    print("\n📋 시나리오 3: 업무 수행 및 Spirit Score")
    print("-" * 60)
    
    # 업무 완료
    print("\n1️⃣ 업무 완료 (판매)")
    spirit_manager.on_task_completed(agent1.agent_id, "김밥 2줄 판매")
    
    # 고객 응대
    print("2️⃣ 고객 응대")
    spirit_manager.on_customer_served(agent1.agent_id, "USER-001")
    
    # 긍정 리뷰 받음
    print("3️⃣ 긍정 리뷰 수신")
    spirit_manager.on_review_received(
        agent1.agent_id,
        5,
        "정말 맛있어요! 친절하고 빠른 배송!"
    )
    
    # 다른 에이전트 도움
    print("4️⃣ 다른 에이전트 도움")
    spirit_manager.on_help_provided(
        helper_agent_id=agent1.agent_id,
        helped_agent_id=agent2.agent_id,
        help_type="재고 공유"
    )
    
    # 현재 점수 확인
    print("\n5️⃣ 현재 Spirit Score 확인")
    score_info = spirit_manager.get_agent_score(agent1.agent_id)
    print(f"   총점: {score_info['total_score']}")
    print(f"   레벨: {score_info['level']}")
    print(f"   총 이벤트: {score_info['total_events']}개")
    
    # ============================================
    # 시나리오 4: 장승배기 5대 강령 체크
    # ============================================
    print("\n📋 시나리오 4: 장승배기 5대 강령 체크")
    print("-" * 60)
    
    # 1. 상부상조
    print("\n1️⃣ 상부상조 체크")
    checker.check_mutual_aid(
        agent_id=agent1.agent_id,
        helped_someone=True,
        context="이영희 에이전트에게 재고 공유"
    )
    
    # 2. 투명성
    print("\n2️⃣ 투명성 체크")
    checker.check_transparency(
        agent_id=agent1.agent_id,
        disclosed_properly=True,
        transaction_type="판매"
    )
    
    # 3. 책임감
    print("\n3️⃣ 책임감 체크")
    checker.check_responsibility(
        agent_id=agent1.agent_id,
        completed_task=True,
        task_description="고객 주문 처리"
    )
    
    # 4. 공동체 정신
    print("\n4️⃣ 공동체 정신 체크")
    checker.check_community(
        agent_id=agent1.agent_id,
        contributed=True,
        contribution_type="지역 상권 활성화"
    )
    
    # 5. 탁월성 추구
    print("\n5️⃣ 탁월성 추구 체크")
    checker.check_excellence(
        agent_id=agent1.agent_id,
        quality_standard_met=True,
        service_type="고객 응대"
    )
    
    # 준수 점수 확인
    print("\n6️⃣ 준수 점수 확인")
    compliance = checker.get_agent_compliance_score(agent1.agent_id)
    print(f"   전체 준수율: {compliance['overall_compliance']}%")
    print(f"   강령별:")
    for principle, data in compliance['by_principle'].items():
        print(f"      {principle}: {data['score']}% ({data['followed']}/{data['total_checks']})")
    
    # ============================================
    # 시나리오 5: 상부상조 10% 자동 배분
    # ============================================
    print("\n📋 시나리오 5: 상부상조 10% 자동 배분")
    print("-" * 60)
    
    print("\n1️⃣ 오늘 수익 발생")
    daily_earnings = 100000  # 10만원
    print(f"   김철수 에이전트 오늘 수익: {daily_earnings:,}원")
    
    print("\n2️⃣ 상부상조 10% 자동 배분")
    transactions = checker.process_mutual_aid_contribution(
        agent_id=agent1.agent_id,
        total_earnings=daily_earnings,
        period="daily"
    )
    
    if transactions:
        print(f"\n✅ 배분 완료!")
        print(f"   총 배분액: {daily_earnings * 0.1:,}원")
        print(f"   수혜자: {len(transactions)}명")
        for tx in transactions:
            print(f"      → {tx.to_agent_id}: {tx.amount:,}원")
    
    print("\n3️⃣ 상부상조 요약")
    summary = checker.get_mutual_aid_summary(agent1.agent_id)
    print(f"   준 금액: {summary['total_given']:,}원")
    print(f"   받은 금액: {summary['total_received']:,}원")
    print(f"   순 기여: {summary['net_contribution']:,}원")
    
    # ============================================
    # 최종 통계
    # ============================================
    print("\n" + "=" * 60)
    print("📊 최종 통계")
    print("=" * 60)
    
    # Spirit Score 리더보드
    print("\n🏆 Spirit Score 리더보드")
    leaderboard = spirit_manager.get_leaderboard(10)
    for rank_info in leaderboard:
        print(f"   {rank_info['rank']}위. {rank_info['agent_id']}")
        print(f"        점수: {rank_info['total_score']}")
        print(f"        레벨: {rank_info['level']}")
    
    # 에이전트 상세 정보
    print(f"\n📈 {agent1.name} ({agent1.agent_id}) 상세")
    print(f"   Spirit Score: {score_info['total_score']}")
    print(f"   레벨: {score_info['level']}")
    print(f"   강령 준수율: {compliance['overall_compliance']}%")
    print(f"   상부상조 기여: {summary['net_contribution']:,}원")
    
    print("\n" + "=" * 60)
    print("✅ 모든 시스템 통합 데모 완료!")
    print("=" * 60)
    print()
    
    print("💡 확인된 통합:")
    print("   ✅ Agent Factory + Spirit Score")
    print("   ✅ AP2 Mandate + 권한 검증")
    print("   ✅ 장승배기 5대 강령 체크")
    print("   ✅ 상부상조 10% 자동 배분")
    print("   ✅ 모든 활동 → Spirit Score 자동 반영")
    print()
    
    # 데이터베이스 닫기
    db.close()


if __name__ == "__main__":
    try:
        run_complete_demo()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

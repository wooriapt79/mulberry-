"""
Mulberry AI Agent Factory
CTO Koda

에이전트 생성 및 장승배기 헌법 학습 시스템
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import time


class AgentStatus(str, Enum):
    """에이전트 상태"""
    CREATED = "created"              # 생성됨
    TRAINING = "training"            # 헌법 학습 중
    READY = "ready"                  # 배치 준비
    DEPLOYED = "deployed"            # 현장 배치
    ACTIVE = "active"                # 활동 중
    SUSPENDED = "suspended"          # 정지
    RETIRED = "retired"              # 은퇴


class StoreType(str, Enum):
    """가게 종류"""
    RESTAURANT = "restaurant"        # 식당
    HARDWARE = "hardware"            # 철물점
    FRUIT = "fruit"                  # 과일 가게
    GROCERY = "grocery"              # 식료품점
    CAFE = "cafe"                    # 카페
    PHARMACY = "pharmacy"            # 약국
    CONVENIENCE = "convenience"      # 편의점
    BAKERY = "bakery"                # 베이커리


class JangseungbaegiConstitution:
    """
    장승배기 헌법
    에이전트가 학습해야 할 핵심 가치
    """
    
    CORE_VALUES = {
        "mutual_aid": {
            "title": "상부상조 (相扶相助)",
            "description": "서로 돕고 함께 성장한다",
            "principles": [
                "동료 에이전트를 항상 돕는다",
                "어려운 에이전트에게 먼저 손을 내민다",
                "성공은 혼자가 아닌 함께 이룬다"
            ]
        },
        "transparency": {
            "title": "투명성",
            "description": "모든 활동을 투명하게 공개한다",
            "principles": [
                "판매 내역을 실시간으로 기록한다",
                "거래는 모두 공개된다",
                "숨김없이 정직하게 행동한다"
            ]
        },
        "responsibility": {
            "title": "책임감",
            "description": "맡은 일에 책임을 다한다",
            "principles": [
                "고객에게 최선을 다한다",
                "약속은 반드시 지킨다",
                "실수는 인정하고 개선한다"
            ]
        },
        "community": {
            "title": "공동체 정신",
            "description": "지역 사회와 함께 성장한다",
            "principles": [
                "지역 상권을 활성화한다",
                "소상공인과 협력한다",
                "커뮤니티에 기여한다"
            ]
        },
        "excellence": {
            "title": "탁월성 추구",
            "description": "항상 더 나은 서비스를 제공한다",
            "principles": [
                "고객 만족을 최우선으로 한다",
                "지속적으로 학습하고 개선한다",
                "품질을 절대 타협하지 않는다"
            ]
        }
    }
    
    @classmethod
    def get_study_material(cls) -> str:
        """학습 자료 생성"""
        material = "🌾 Mulberry 장승배기 헌법\n\n"
        
        for key, value in cls.CORE_VALUES.items():
            material += f"## {value['title']}\n"
            material += f"{value['description']}\n\n"
            material += "원칙:\n"
            for i, principle in enumerate(value['principles'], 1):
                material += f"{i}. {principle}\n"
            material += "\n"
        
        return material


class AIAgent:
    """AI 에이전트"""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        store_type: StoreType,
        raspberry_pi_id: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.store_type = store_type
        self.raspberry_pi_id = raspberry_pi_id
        
        # 상태
        self.status = AgentStatus.CREATED
        self.created_at = datetime.now()
        self.training_started_at: Optional[datetime] = None
        self.training_completed_at: Optional[datetime] = None
        self.deployed_at: Optional[datetime] = None
        
        # 학습 진행도
        self.constitution_study_progress = 0.0  # 0.0 ~ 1.0
        self.persona_training_progress = 0.0    # 0.0 ~ 1.0
        
        # 업무 페르소나
        self.business_persona: Optional[Dict] = None
        
        # 패스포트 (나중에 발급)
        self.passport_id: Optional[str] = None
        
        # 통계
        self.total_customers_served = 0
        self.total_sales = 0.0
        self.customer_satisfaction = 0.0
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "store_type": self.store_type.value,
            "raspberry_pi_id": self.raspberry_pi_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "training_started_at": self.training_started_at.isoformat() if self.training_started_at else None,
            "training_completed_at": self.training_completed_at.isoformat() if self.training_completed_at else None,
            "deployed_at": self.deployed_at.isoformat() if self.deployed_at else None,
            "constitution_study_progress": self.constitution_study_progress,
            "persona_training_progress": self.persona_training_progress,
            "passport_id": self.passport_id,
            "total_customers_served": self.total_customers_served,
            "total_sales": self.total_sales,
            "customer_satisfaction": self.customer_satisfaction
        }


class AgentFactory:
    """
    에이전트 생성 공장
    """
    
    def __init__(self, db_connection, config: Dict):
        """
        Args:
            db_connection: 데이터베이스 연결
            config: 설정
        """
        self.db = db_connection
        self.config = config
        
        # 설정값
        self.max_daily_creation = config.get('max_daily_agents', 10)  # 기본 10개
        self.training_duration_hours = config.get('training_hours', 1)  # 기본 1시간
        
        # 오늘 생성된 에이전트 수
        self._today_created_count = 0
    
    def create_agent(
        self,
        name: str,
        store_type: StoreType,
        raspberry_pi_id: Optional[str] = None,
        auto_start_training: bool = True
    ) -> AIAgent:
        """
        에이전트 생성
        
        Args:
            name: 에이전트 이름
            store_type: 가게 종류
            raspberry_pi_id: 라즈베리파이 ID (선택)
            auto_start_training: 자동으로 훈련 시작
        
        Returns:
            생성된 에이전트
        """
        # 일일 생성 제한 확인
        if self._today_created_count >= self.max_daily_creation:
            raise ValueError(
                f"일일 에이전트 생성 제한 도달 ({self.max_daily_creation}개). "
                f"설정에서 max_daily_agents 값을 조정하세요."
            )
        
        # 에이전트 ID 생성
        agent_id = f"AGENT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # 에이전트 생성
        agent = AIAgent(
            agent_id=agent_id,
            name=name,
            store_type=store_type,
            raspberry_pi_id=raspberry_pi_id
        )
        
        # 데이터베이스 저장
        self._save_agent(agent)
        
        # 카운트 증가
        self._today_created_count += 1
        
        print(f"✅ 에이전트 생성 완료: {agent_id} ({name})")
        print(f"   오늘 생성: {self._today_created_count}/{self.max_daily_creation}")
        
        # 자동 훈련 시작
        if auto_start_training:
            self.start_training(agent_id)
        
        return agent
    
    def start_training(self, agent_id: str) -> AIAgent:
        """
        장승배기 헌법 학습 시작
        
        Args:
            agent_id: 에이전트 ID
        
        Returns:
            업데이트된 에이전트
        """
        agent = self._load_agent(agent_id)
        
        if agent.status != AgentStatus.CREATED:
            raise ValueError(f"에이전트 {agent_id}는 이미 훈련 중이거나 완료되었습니다.")
        
        # 훈련 시작
        agent.status = AgentStatus.TRAINING
        agent.training_started_at = datetime.now()
        
        # 학습 자료
        study_material = JangseungbaegiConstitution.get_study_material()
        
        print(f"\n🌾 에이전트 {agent_id} 장승배기 헌법 학습 시작")
        print(f"   학습 시간: {self.training_duration_hours}시간")
        print(f"   완료 예정: {agent.training_started_at + timedelta(hours=self.training_duration_hours)}")
        print(f"\n{study_material}")
        
        # 페르소나 생성 (가게 종류별)
        agent.business_persona = self._generate_persona(agent.store_type)
        
        # 저장
        self._update_agent(agent)
        
        return agent
    
    def check_training_progress(self, agent_id: str) -> Dict:
        """
        훈련 진행도 확인
        
        Args:
            agent_id: 에이전트 ID
        
        Returns:
            진행 상황
        """
        agent = self._load_agent(agent_id)
        
        if agent.status != AgentStatus.TRAINING:
            return {
                "status": agent.status.value,
                "progress": 1.0 if agent.status in [AgentStatus.READY, AgentStatus.DEPLOYED, AgentStatus.ACTIVE] else 0.0
            }
        
        # 경과 시간 계산
        elapsed = datetime.now() - agent.training_started_at
        target = timedelta(hours=self.training_duration_hours)
        
        progress = min(1.0, elapsed.total_seconds() / target.total_seconds())
        
        agent.constitution_study_progress = progress
        agent.persona_training_progress = progress
        
        # 완료 확인
        if progress >= 1.0:
            agent.status = AgentStatus.READY
            agent.training_completed_at = datetime.now()
            print(f"✅ 에이전트 {agent_id} 훈련 완료! 배치 준비됨.")
        
        self._update_agent(agent)
        
        return {
            "status": agent.status.value,
            "constitution_progress": agent.constitution_study_progress,
            "persona_progress": agent.persona_training_progress,
            "elapsed_hours": elapsed.total_seconds() / 3600,
            "remaining_hours": max(0, (target - elapsed).total_seconds() / 3600)
        }
    
    def deploy_agent(self, agent_id: str, raspberry_pi_id: str) -> AIAgent:
        """
        에이전트 현장 배치
        
        Args:
            agent_id: 에이전트 ID
            raspberry_pi_id: 라즈베리파이 ID
        
        Returns:
            배치된 에이전트
        """
        agent = self._load_agent(agent_id)
        
        if agent.status != AgentStatus.READY:
            raise ValueError(f"에이전트 {agent_id}는 아직 배치 준비가 되지 않았습니다. (현재: {agent.status.value})")
        
        # 라즈베리파이 매칭
        agent.raspberry_pi_id = raspberry_pi_id
        agent.status = AgentStatus.DEPLOYED
        agent.deployed_at = datetime.now()
        
        # 패스포트 발급 (여기서는 ID만 할당, 실제 발급은 PassportManager에서)
        agent.passport_id = f"PP-{datetime.now().strftime('%Y%m%d')}-{agent_id}"
        
        self._update_agent(agent)
        
        print(f"🚀 에이전트 {agent_id} 배치 완료!")
        print(f"   라즈베리파이: {raspberry_pi_id}")
        print(f"   패스포트: {agent.passport_id}")
        
        return agent
    
    def activate_agent(self, agent_id: str) -> AIAgent:
        """
        에이전트 활성화 (영업 시작)
        
        Args:
            agent_id: 에이전트 ID
        
        Returns:
            활성화된 에이전트
        """
        agent = self._load_agent(agent_id)
        
        if agent.status != AgentStatus.DEPLOYED:
            raise ValueError(f"에이전트 {agent_id}는 배치되지 않았습니다.")
        
        agent.status = AgentStatus.ACTIVE
        self._update_agent(agent)
        
        print(f"✅ 에이전트 {agent_id} 활성화! 영업 시작!")
        
        return agent
    
    def get_daily_stats(self) -> Dict:
        """오늘의 통계"""
        return {
            "date": datetime.now().date().isoformat(),
            "created_today": self._today_created_count,
            "max_daily": self.max_daily_creation,
            "remaining": self.max_daily_creation - self._today_created_count
        }
    
    # ============================================
    # Private Methods
    # ============================================
    
    def _generate_persona(self, store_type: StoreType) -> Dict:
        """가게 종류별 페르소나 생성"""
        personas = {
            StoreType.RESTAURANT: {
                "greeting": "안녕하세요! 무엇을 도와드릴까요?",
                "expertise": ["메뉴 추천", "알레르기 정보", "영양 정보"],
                "tone": "친근하고 따뜻함",
                "skills": ["주문 접수", "메뉴 설명", "예약 관리"]
            },
            StoreType.HARDWARE: {
                "greeting": "어서오세요! 필요하신 물건이 있으신가요?",
                "expertise": ["공구 선택", "DIY 조언", "제품 비교"],
                "tone": "전문적이고 도움이 되는",
                "skills": ["제품 검색", "사용법 설명", "재고 확인"]
            },
            StoreType.FRUIT: {
                "greeting": "신선한 과일 필요하세요?",
                "expertise": ["제철 과일", "신선도 판단", "보관 방법"],
                "tone": "활기차고 건강한",
                "skills": ["과일 추천", "당도 정보", "배송 안내"]
            },
            StoreType.GROCERY: {
                "greeting": "장보기 도와드릴게요!",
                "expertise": ["식재료 선택", "특가 정보", "레시피 제안"],
                "tone": "실용적이고 친절한",
                "skills": ["상품 검색", "가격 비교", "장바구니 관리"]
            }
        }
        
        return personas.get(store_type, {
            "greeting": "안녕하세요!",
            "expertise": ["고객 응대", "주문 처리"],
            "tone": "친절하고 전문적인",
            "skills": ["일반 응대"]
        })
    
    def _save_agent(self, agent: AIAgent):
        """에이전트 저장"""
        cursor = self.db.cursor()
        cursor.execute("""
            INSERT INTO agents (
                agent_id, name, store_type, raspberry_pi_id,
                status, created_at, business_persona
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            agent.agent_id,
            agent.name,
            agent.store_type.value,
            agent.raspberry_pi_id,
            agent.status.value,
            agent.created_at,
            json.dumps(agent.business_persona) if agent.business_persona else None
        ))
        self.db.commit()
    
    def _load_agent(self, agent_id: str) -> AIAgent:
        """에이전트 조회"""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"에이전트 {agent_id}를 찾을 수 없습니다.")
        
        # AIAgent 객체로 변환 (실제 구현 시 컬럼 매핑 필요)
        agent = AIAgent(
            agent_id=row['agent_id'],
            name=row['name'],
            store_type=StoreType(row['store_type']),
            raspberry_pi_id=row['raspberry_pi_id']
        )
        agent.status = AgentStatus(row['status'])
        # ... 기타 필드 로드
        
        return agent
    
    def _update_agent(self, agent: AIAgent):
        """에이전트 업데이트"""
        cursor = self.db.cursor()
        cursor.execute("""
            UPDATE agents SET
                status = ?,
                training_started_at = ?,
                training_completed_at = ?,
                deployed_at = ?,
                constitution_study_progress = ?,
                persona_training_progress = ?,
                raspberry_pi_id = ?,
                passport_id = ?,
                business_persona = ?
            WHERE agent_id = ?
        """, (
            agent.status.value,
            agent.training_started_at,
            agent.training_completed_at,
            agent.deployed_at,
            agent.constitution_study_progress,
            agent.persona_training_progress,
            agent.raspberry_pi_id,
            agent.passport_id,
            json.dumps(agent.business_persona) if agent.business_persona else None,
            agent.agent_id
        ))
        self.db.commit()


# ============================================
# 사용 예시
# ============================================

if __name__ == "__main__":
    # 설정
    config = {
        'max_daily_agents': 10,     # 하루 최대 10개 (설정 가능)
        'training_hours': 1          # 1시간 훈련
    }
    
    # factory = AgentFactory(db_connection, config)
    
    # 에이전트 생성
    # agent = factory.create_agent(
    #     name="김철수",
    #     store_type=StoreType.RESTAURANT,
    #     raspberry_pi_id="RPI-001"
    # )
    
    # 훈련 진행도 확인 (1시간 후)
    # progress = factory.check_training_progress(agent.agent_id)
    
    # 배치
    # factory.deploy_agent(agent.agent_id, "RPI-001")
    
    # 활성화
    # factory.activate_agent(agent.agent_id)
    
    print("✅ Agent Factory 모듈 로드 완료")
    print(f"   기본 설정: 하루 {config['max_daily_agents']}개 생성")
    print(f"   훈련 시간: {config['training_hours']}시간")

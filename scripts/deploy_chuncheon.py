"""
Mulberry - 춘천시 배치 스크립트
Chuncheon City Deployment Script

인제군 → 춘천시 확장
"""

import asyncio
from datetime import datetime
from loguru import logger

from app.services.guardian_system import GuardianSystem, GuardianType
from app.services.webhook_engine import WebhookEngine
from app.services.jangseungbaegi_core import JangseungbaegiCore, CooperativeRole


# ============================================
# 춘천시 배치
# ============================================

class ChuncheonDeployment:
    """춘천시 Mulberry Trust 배치"""
    
    def __init__(self):
        """배치 초기화"""
        # 시스템
        self.guardian_system = GuardianSystem()
        self.webhook_engine = WebhookEngine(base_url="https://mulberry.ai")
        self.cooperative_core = JangseungbaegiCore()
        
        # 통계
        self.total_guardians = 0
        self.total_seniors = 0
        self.total_endpoints = 0
        
        logger.info("=" * 80)
        logger.info("🚀 춘천시 Mulberry Trust 배치 시작")
        logger.info("=" * 80)
    
    async def deploy(self):
        """전체 배치 실행"""
        try:
            # 1단계: Guardian 에이전트 생성
            await self._create_guardians()
            
            # 2단계: 웹훅 엔드포인트 생성
            await self._create_webhooks()
            
            # 3단계: 협동조합 구성원 등록
            await self._setup_cooperative()
            
            # 4단계: 시범 어르신 등록 (100명)
            await self._register_pilot_seniors()
            
            # 5단계: 시스템 검증
            await self._verify_system()
            
            # 6단계: 배치 완료 보고
            self._generate_report()
            
            logger.info("=" * 80)
            logger.info("✅ 춘천시 배치 완료!")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ 배치 실패: {str(e)}")
            raise
    
    async def _create_guardians(self):
        """1단계: Guardian 에이전트 생성"""
        logger.info("\n[1단계] Guardian 에이전트 생성 중...")
        
        # 춘천시는 인구가 많으므로 3개 Guardian 배치
        guardians_config = [
            {
                "name": "춘천시_동부_후견인",
                "district": "동부권 (소양로, 효자동, 석사동)",
                "target_seniors": 350
            },
            {
                "name": "춘천시_중부_후견인",
                "district": "중부권 (중앙로, 조양동, 근화동)",
                "target_seniors": 300
            },
            {
                "name": "춘천시_서부_후견인",
                "district": "서부권 (신북읍, 동면, 남면)",
                "target_seniors": 350
            }
        ]
        
        self.guardians = []
        
        for config in guardians_config:
            guardian = self.guardian_system.create_guardian_agent(
                agent_name=config["name"],
                guardian_type=GuardianType.DONATION_MANAGER
            )
            
            self.guardians.append({
                "agent": guardian,
                "config": config
            })
            
            self.total_guardians += 1
            
            logger.info(f"✅ {config['name']} 생성 완료")
            logger.info(f"   담당 지역: {config['district']}")
            logger.info(f"   목표 어르신: {config['target_seniors']}명")
        
        logger.info(f"\n총 {self.total_guardians}개 Guardian 생성 완료 ✅")
    
    async def _create_webhooks(self):
        """2단계: 웹훅 엔드포인트 생성"""
        logger.info("\n[2단계] 웹훅 엔드포인트 생성 중...")
        
        for guardian_info in self.guardians:
            guardian = guardian_info["agent"]
            config = guardian_info["config"]
            
            # 웹훅 엔드포인트 생성
            endpoint = self.webhook_engine.create_endpoint(
                agent_id=guardian.agent_id,
                agent_name=config["name"]
            )
            
            guardian_info["endpoint"] = endpoint
            self.total_endpoints += 1
            
            logger.info(f"✅ {config['name']} 웹훅 생성")
            logger.info(f"   URL: {endpoint.webhook_url}")
            logger.info(f"   Email: {endpoint.email_address}")
        
        logger.info(f"\n총 {self.total_endpoints}개 엔드포인트 생성 완료 ✅")
    
    async def _setup_cooperative(self):
        """3단계: 협동조합 구성원 등록"""
        logger.info("\n[3단계] 협동조합 구성원 등록 중...")
        
        # 각 Guardian을 협동조합 구성원으로 등록
        for guardian_info in self.guardians:
            guardian = guardian_info["agent"]
            config = guardian_info["config"]
            
            member = self.cooperative_core.add_member(
                agent_name=config["name"],
                role=CooperativeRole.GUARDIAN
            )
            
            guardian_info["member"] = member
            
            logger.info(f"✅ {config['name']} 협동조합 가입")
        
        logger.info(f"\n협동조합 구성원 {self.total_guardians}명 등록 완료 ✅")
    
    async def _register_pilot_seniors(self):
        """4단계: 시범 어르신 등록"""
        logger.info("\n[4단계] 시범 어르신 등록 중...")
        
        # 각 Guardian당 시범 어르신 등록
        for guardian_info in self.guardians:
            guardian = guardian_info["agent"]
            config = guardian_info["config"]
            
            # 시범 운영: 각 Guardian당 30-35명
            pilot_count = 33  # 총 ~100명
            
            for i in range(pilot_count):
                senior = self.guardian_system.register_senior(
                    name=f"{config['name']}_어르신_{i+1:03d}",
                    age=70 + (i % 15),  # 70-85세
                    address=f"춘천시 {config['district'].split('(')[1].split(',')[0].strip()}",
                    phone=f"010-{9000+i:04d}-{1000+i:04d}",
                    municipality="춘천시",
                    district=config['district'].split('(')[1].split(',')[0].strip()
                )
                
                # Guardian 배정
                self.guardian_system.assign_guardian(
                    senior.senior_id,
                    guardian.agent_id
                )
                
                self.total_seniors += 1
            
            logger.info(f"✅ {config['name']}: {pilot_count}명 등록 완료")
        
        logger.info(f"\n총 {self.total_seniors}명 시범 어르신 등록 완료 ✅")
    
    async def _verify_system(self):
        """5단계: 시스템 검증"""
        logger.info("\n[5단계] 시스템 검증 중...")
        
        # 웹훅 테스트
        logger.info("웹훅 테스트...")
        test_result = await self.webhook_engine.process_webhook(
            agent_id=self.guardians[0]["agent"].agent_id,
            event_type="test",
            payload={"test": "춘천 배치 테스트"}
        )
        logger.info(f"✅ 웹훅 응답 시간: {test_result.get('processing_time_ms', 0):.1f}ms")
        
        # Guardian 시스템 통계
        logger.info("Guardian 시스템 통계...")
        stats = self.guardian_system.get_system_stats()
        logger.info(f"✅ 등록 어르신: {stats['total_seniors']}명")
        logger.info(f"✅ Guardian: {stats['total_agents']}개")
        
        # 협동조합 통계
        logger.info("협동조합 통계...")
        coop_stats = self.cooperative_core.get_cooperative_stats()
        logger.info(f"✅ 협동조합 구성원: {coop_stats['total_members']}명")
        
        logger.info("\n시스템 검증 완료 ✅")
    
    def _generate_report(self):
        """6단계: 배치 완료 보고서"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 춘천시 배치 완료 보고서")
        logger.info("=" * 80)
        
        logger.info(f"\n배치 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"배치 지역: 춘천시 (강원도)")
        
        logger.info(f"\n[시스템 구성]")
        logger.info(f"Guardian 에이전트: {self.total_guardians}개")
        logger.info(f"웹훅 엔드포인트: {self.total_endpoints}개")
        logger.info(f"협동조합 구성원: {self.total_guardians}명")
        
        logger.info(f"\n[시범 운영]")
        logger.info(f"등록 어르신: {self.total_seniors}명")
        logger.info(f"운영 기간: 3개월 (시범)")
        
        logger.info(f"\n[Guardian 상세]")
        for i, guardian_info in enumerate(self.guardians, 1):
            config = guardian_info["config"]
            endpoint = guardian_info["endpoint"]
            
            logger.info(f"\n{i}. {config['name']}")
            logger.info(f"   담당 지역: {config['district']}")
            logger.info(f"   목표: {config['target_seniors']}명")
            logger.info(f"   현재: ~33명 (시범)")
            logger.info(f"   웹훅: {endpoint.webhook_url}")
            logger.info(f"   이메일: {endpoint.email_address}")
        
        logger.info(f"\n[다음 단계]")
        logger.info(f"1. 춘천시청 협의 및 MOU")
        logger.info(f"2. 시범 운영 3개월")
        logger.info(f"3. 목표 1,000명 확대")
        logger.info(f"4. 강원도 전역 확산")
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ 춘천시 Mulberry Trust 구축 완료!")
        logger.info("=" * 80)


# ============================================
# 실행
# ============================================

async def main():
    """춘천시 배치 실행"""
    deployment = ChuncheonDeployment()
    await deployment.deploy()


if __name__ == "__main__":
    asyncio.run(main())

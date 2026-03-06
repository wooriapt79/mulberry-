"""
Mulberry Phase 3 - Strategy Advisor Agent
전체 시스템 메트릭 분석 및 Sentinel 연동
"""

import asyncio
import json
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger

from app.agents.base import BaseAgent, MessageBus, MessageType, AgentMessage


class StrategyAdvisorAgent(BaseAgent):
    """
    전략 자문 비서
    
    기능:
    - 전체 에이전트 활동 데이터 취합
    - 인제군 경제 활성화 지표 생성
    - 대시보드 데이터 제공
    - Sentinel(Malu) 연동 및 보안 검증
    """
    
    def __init__(self, message_bus: MessageBus, config: Optional[Dict[str, Any]] = None):
        """Strategy Advisor 초기화"""
        super().__init__(
            agent_name="Strategy_Advisor",
            message_bus=message_bus,
            config=config or {}
        )
        
        # 메트릭 저장소
        self.metrics_history: List[Dict[str, Any]] = []
        
        # 일일 집계
        self.daily_aggregates: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # 경제 지표
        self.economic_indicators = {
            "total_revenue": 0.0,
            "total_orders": 0,
            "active_farms": 0,
            "active_customers": 0,
            "avg_order_value": 0.0,
            "customer_satisfaction": 0.0
        }
        
        # 🆕 SNS 활동 지표 (Phase 3-C)
        self.sns_metrics = {
            "total_posts_today": 0,
            "senior_posts_today": 0,  # 시니어가 직접 작성한 포스트
            "engagement_rate": 0.0,  # 참여율 (좋아요, 댓글 등)
            "reach": 0,  # 도달 수
            "active_users": 0,  # 활성 사용자
            "top_hashtags": [],  # 인기 해시태그
            "sentiment_score": 0.0  # 감성 점수 (긍정적 반응)
        }
        
        # Sentinel 설정
        self.sentinel_endpoint = "https://sentinel.mulberry.kr/api/advisor/report"
        self.sentinel_alert_threshold = {
            "revenue_drop_pct": 20,  # 20% 매출 하락
            "error_rate_pct": 5,  # 5% 오류율
            "response_time_ms": 1000  # 1초 응답 시간
        }
        
        # HTTP 클라이언트
        self.http_client = httpx.AsyncClient(timeout=10)
        
        logger.info("✅ Strategy Advisor initialized")
    
    def _register_message_handlers(self):
        """메시지 핸들러 등록"""
        # 모든 메트릭 업데이트 수신
        self.message_bus.subscribe(
            MessageType.METRICS_UPDATE,
            self.handle_metrics_update
        )
        
        # Sentinel 알림 처리
        self.message_bus.subscribe(
            MessageType.SENTINEL_ALERT,
            self.handle_sentinel_alert
        )
        
        # 🆕 SNS 활동 추적 (Phase 3-C)
        self.message_bus.subscribe(
            MessageType.POST_PUBLISHED,
            self.handle_post_published
        )
    
    async def start(self):
        """Strategy Advisor 시작"""
        await super().start()
        
        # 정기 보고 작업 시작
        asyncio.create_task(self._run_periodic_reporting())
        
        logger.info("🚀 Strategy Advisor started with Sentinel integration")
    
    async def stop(self):
        """Strategy Advisor 종료"""
        await super().stop()
        await self.http_client.aclose()
    
    async def _run_periodic_reporting(self):
        """정기 보고 (Sentinel에게)"""
        while self.is_active:
            try:
                # 1시간마다 보고
                await asyncio.sleep(3600)
                
                await self.generate_report()
                await self.report_to_sentinel()
                
            except Exception as e:
                logger.error(f"❌ Periodic reporting error: {str(e)}")
    
    async def handle_metrics_update(self, message: AgentMessage):
        """
        메트릭 업데이트 처리
        
        모든 에이전트로부터 메트릭을 받아 집계
        
        Payload 예시:
        {
            "date": "2024-02-11",
            "total_orders": 150,
            "total_revenue": 3500000,
            "active_customers": 45
        }
        """
        try:
            self.stats["messages_received"] += 1
            
            payload = message.payload
            date = payload.get("date", datetime.now().strftime("%Y-%m-%d"))
            from_agent = message.from_agent
            
            # 메트릭 저장
            metric_entry = {
                "timestamp": datetime.now().isoformat(),
                "date": date,
                "from_agent": from_agent,
                "metrics": payload
            }
            
            self.metrics_history.append(metric_entry)
            
            # 일일 집계에 추가
            if date not in self.daily_aggregates:
                self.daily_aggregates[date] = {}
            
            self.daily_aggregates[date][from_agent] = payload
            
            # 경제 지표 업데이트
            await self.update_economic_indicators()
            
            self.stats["tasks_completed"] += 1
            
            logger.debug(f"📊 Metrics updated from {from_agent}")
            
        except Exception as e:
            logger.error(f"❌ Metrics update error: {str(e)}")
            self.stats["errors"] += 1
    
    async def handle_sentinel_alert(self, message: AgentMessage):
        """
        Sentinel 알림 처리
        
        Sentinel로부터 보안/성능 알림 수신
        """
        try:
            self.stats["messages_received"] += 1
            
            payload = message.payload
            alert_type = payload.get("alert_type")
            severity = payload.get("severity", "medium")
            
            logger.warning(f"🚨 Sentinel Alert: {alert_type} (severity: {severity})")
            
            # 알림 기록
            alert_record = {
                "timestamp": datetime.now().isoformat(),
                "alert_type": alert_type,
                "severity": severity,
                "details": payload
            }
            
            # 심각한 알림은 즉시 처리
            if severity == "critical":
                await self._handle_critical_alert(alert_record)
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Sentinel alert handling error: {str(e)}")
    
    async def handle_post_published(self, message: AgentMessage):
        """
        🆕 SNS 포스트 발행 추적 (Phase 3-C)
        
        SNS Manager로부터 포스트 발행 알림 수신
        
        Payload:
        {
            "post_type": "senior_story" | "harvest" | "promotion",
            "farm_name": "푸른골농원",
            "user_type": "senior" | "agent",
            "reach_estimate": 100,
            "hashtags": ["인제군", "로컬푸드"]
        }
        """
        try:
            self.stats["messages_received"] += 1
            
            payload = message.payload
            post_type = payload.get("post_type")
            user_type = payload.get("user_type", "agent")
            
            logger.info(f"📊 SNS activity tracked: {post_type} by {user_type}")
            
            # SNS 지표 업데이트
            self.sns_metrics["total_posts_today"] += 1
            
            # 시니어가 직접 작성한 포스트
            if user_type == "senior":
                self.sns_metrics["senior_posts_today"] += 1
            
            # 도달 추정치 업데이트
            reach_estimate = payload.get("reach_estimate", 50)
            self.sns_metrics["reach"] += reach_estimate
            
            # 해시태그 빈도 집계
            hashtags = payload.get("hashtags", [])
            for tag in hashtags:
                # 해시태그 카운트 (실제로는 Counter 사용)
                pass
            
            # 참여율 계산 (샘플)
            # 실제로는 마스토돈 API에서 좋아요, 댓글 수 가져오기
            self.sns_metrics["engagement_rate"] = 0.15  # 15%
            
            self.stats["tasks_completed"] += 1
            
        except Exception as e:
            logger.error(f"❌ Post tracking error: {str(e)}")
    
    async def _handle_critical_alert(self, alert: Dict[str, Any]):
        """긴급 알림 처리"""
        logger.critical(f"🚨 CRITICAL ALERT: {alert}")
        
        # 긴급 조치 (예: 특정 에이전트 재시작, 트래픽 제한 등)
        # 향후 구현
    
    async def update_economic_indicators(self):
        """경제 지표 업데이트"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            today_data = self.daily_aggregates.get(today, {})
            
            # 매출
            total_revenue = 0.0
            total_orders = 0
            
            for agent_data in today_data.values():
                total_revenue += agent_data.get("total_revenue", 0.0)
                total_orders += agent_data.get("total_orders", 0)
            
            # 평균 주문 금액
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
            
            # 지표 업데이트
            self.economic_indicators.update({
                "total_revenue": total_revenue,
                "total_orders": total_orders,
                "avg_order_value": avg_order_value,
                "last_updated": datetime.now().isoformat()
            })
            
            # 이상 감지
            await self._detect_anomalies()
            
        except Exception as e:
            logger.error(f"❌ Economic indicators update error: {str(e)}")
    
    async def _detect_anomalies(self):
        """
        이상 감지
        
        급격한 매출 하락, 오류율 증가 등 감지
        """
        try:
            # 어제와 오늘 비교
            today = datetime.now().strftime("%Y-%m-%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            today_revenue = self.daily_aggregates.get(today, {}).get("Sales_Agent", {}).get("total_revenue", 0)
            yesterday_revenue = self.daily_aggregates.get(yesterday, {}).get("Sales_Agent", {}).get("total_revenue", 1)
            
            if yesterday_revenue > 0:
                revenue_change_pct = ((today_revenue - yesterday_revenue) / yesterday_revenue) * 100
                
                # 매출 급감 감지
                if revenue_change_pct < -self.sentinel_alert_threshold["revenue_drop_pct"]:
                    logger.warning(f"⚠️ Revenue drop detected: {revenue_change_pct:.1f}%")
                    
                    # Sentinel에게 알림
                    await self.send_message(
                        MessageType.SENTINEL_ALERT,
                        payload={
                            "alert_type": "revenue_drop",
                            "severity": "high",
                            "revenue_change_pct": revenue_change_pct,
                            "today_revenue": today_revenue,
                            "yesterday_revenue": yesterday_revenue
                        },
                        priority=1
                    )
            
        except Exception as e:
            logger.error(f"❌ Anomaly detection error: {str(e)}")
    
    async def generate_report(self) -> Dict[str, Any]:
        """
        인제군 경제 활성화 지표 보고서 생성
        
        Returns:
            dict: 보고서 데이터
        """
        try:
            logger.info("📊 Generating economic activity report...")
            
            today = datetime.now().strftime("%Y-%m-%d")
            today_data = self.daily_aggregates.get(today, {})
            
            # 에이전트별 통계
            agent_stats = {}
            
            for agent_name, data in today_data.items():
                agent_stats[agent_name] = {
                    "metrics": data,
                    "status": "active"
                }
            
            # 보고서 구성
            report = {
                "generated_at": datetime.now().isoformat(),
                "date": today,
                "economic_indicators": self.economic_indicators,
                "sns_metrics": self.sns_metrics,  # 🆕 SNS 활동 지표
                "agent_stats": agent_stats,
                "alerts": self._get_recent_alerts(),
                "summary": {
                    "total_revenue_krw": self.economic_indicators["total_revenue"],
                    "total_orders": self.economic_indicators["total_orders"],
                    "avg_order_value_krw": self.economic_indicators["avg_order_value"],
                    "sns_posts_today": self.sns_metrics["total_posts_today"],  # 🆕
                    "senior_engagement": self.sns_metrics["senior_posts_today"],  # 🆕
                    "platform_health": "healthy"  # 향후 계산
                }
            }
            
            self.stats["tasks_completed"] += 1
            
            logger.info(f"✅ Report generated: {report['summary']}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Report generation error: {str(e)}")
            return {}
    
    def _get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """최근 알림 조회"""
        # 메트릭 히스토리에서 알림 필터
        cutoff = datetime.now() - timedelta(hours=hours)
        
        alerts = []
        
        for metric in self.metrics_history:
            timestamp = datetime.fromisoformat(metric["timestamp"])
            
            if timestamp >= cutoff:
                # 알림 판단 로직
                pass
        
        return alerts
    
    async def report_to_sentinel(self):
        """
        Sentinel(Malu)에게 보고
        
        전체 시스템 상태 및 경제 지표 전송
        """
        try:
            logger.info("📡 Reporting to Sentinel...")
            
            report = await self.generate_report()
            
            # Sentinel API 호출
            try:
                response = await self.http_client.post(
                    self.sentinel_endpoint,
                    json=report,
                    headers={"X-Agent": "Strategy_Advisor"}
                )
                
                if response.status_code == 200:
                    logger.info("✅ Report sent to Sentinel successfully")
                    
                    # Sentinel 응답 처리
                    sentinel_response = response.json()
                    
                    # Sentinel의 지시사항 확인
                    instructions = sentinel_response.get("instructions", [])
                    
                    for instruction in instructions:
                        await self._execute_sentinel_instruction(instruction)
                else:
                    logger.warning(f"⚠️ Sentinel report failed: {response.status_code}")
                
            except httpx.RequestError as e:
                logger.error(f"❌ Sentinel connection error: {str(e)}")
                # Fallback: 로컬 저장
                await self._save_report_locally(report)
            
        except Exception as e:
            logger.error(f"❌ Sentinel reporting error: {str(e)}")
    
    async def _execute_sentinel_instruction(self, instruction: Dict[str, Any]):
        """
        Sentinel의 지시사항 실행
        
        Args:
            instruction: {
                "type": "scale_down", "restart_agent", etc.
                "target": "Sales_Agent",
                "params": {...}
            }
        """
        try:
            instruction_type = instruction.get("type")
            target = instruction.get("target")
            
            logger.info(f"🎯 Executing Sentinel instruction: {instruction_type} on {target}")
            
            if instruction_type == "restart_agent":
                # 에이전트 재시작 요청
                pass
            
            elif instruction_type == "adjust_threshold":
                # 임계값 조정
                pass
            
            # 실행 결과 Sentinel에게 보고
            
        except Exception as e:
            logger.error(f"❌ Instruction execution error: {str(e)}")
    
    async def _save_report_locally(self, report: Dict[str, Any]):
        """보고서 로컬 저장 (Sentinel 연결 실패 시)"""
        try:
            import os
            
            report_dir = "/tmp/mulberry_reports"
            os.makedirs(report_dir, exist_ok=True)
            
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(report_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Report saved locally: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Local save error: {str(e)}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        대시보드 데이터 생성
        
        웹 대시보드에서 사용할 데이터
        
        Returns:
            dict: 대시보드 데이터
        """
        try:
            # 최근 7일 데이터
            recent_days = []
            
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                day_data = self.daily_aggregates.get(date, {})
                
                total_revenue = sum(
                    data.get("total_revenue", 0)
                    for data in day_data.values()
                )
                
                total_orders = sum(
                    data.get("total_orders", 0)
                    for data in day_data.values()
                )
                
                recent_days.append({
                    "date": date,
                    "revenue": total_revenue,
                    "orders": total_orders
                })
            
            dashboard = {
                "current_indicators": self.economic_indicators,
                "sns_metrics": self.sns_metrics,  # 🆕 SNS 활동 지표
                "recent_trend": recent_days,
                "agent_health": self._get_agent_health(),
                "top_products": [],  # 향후 구현
                "customer_insights": {},  # 향후 구현
                "sns_insights": {  # 🆕 SNS 인사이트
                    "engagement_trend": "상승",  # 샘플
                    "peak_posting_time": "12:00-14:00",  # 샘플
                    "most_active_users": 15  # 샘플
                }
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Dashboard data error: {str(e)}")
            return {}
    
    def _get_agent_health(self) -> Dict[str, str]:
        """에이전트 상태 요약"""
        # 메시지 버스에서 에이전트 상태 가져오기
        # 향후 구현
        return {
            "SNS_Manager": "healthy",
            "Sales_Agent": "healthy",
            "Inventory_Manager": "healthy",
            "CRM_Manager": "healthy",
            "Strategy_Advisor": "healthy"
        }


# ============================================
# 싱글톤 인스턴스
# ============================================

_strategy_advisor_instance: Optional[StrategyAdvisorAgent] = None


def get_strategy_advisor(message_bus: MessageBus) -> StrategyAdvisorAgent:
    """싱글톤 Strategy Advisor"""
    global _strategy_advisor_instance
    
    if _strategy_advisor_instance is None:
        _strategy_advisor_instance = StrategyAdvisorAgent(message_bus)
    
    return _strategy_advisor_instance

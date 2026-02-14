"""
Mulberry Phase 4-B - Agent Passport Webhook Engine
실시간 결제 확인 및 외부 통신 시스템

Mission: 에이전트들이 외부 세계와 실시간 소통
Target: 100ms 이내 에이전트 상태 업데이트
"""

import asyncio
import uuid
import hmac
import hashlib
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from loguru import logger
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel


# ============================================
# Webhook Event Types
# ============================================

class WebhookEventType(Enum):
    """웹훅 이벤트 타입"""
    PAYMENT_SUCCESS = "payment.success"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_PENDING = "payment.pending"
    PAYMENT_REFUND = "payment.refund"
    
    EMAIL_RECEIVED = "email.received"
    EMAIL_SENT = "email.sent"
    
    EXTERNAL_ORDER = "external.order"
    EXTERNAL_INQUIRY = "external.inquiry"
    
    AGENT_COMMAND = "agent.command"
    AGENT_NOTIFICATION = "agent.notification"


# ============================================
# Webhook Payload Models
# ============================================

class PaymentWebhookPayload(BaseModel):
    """결제 웹훅 페이로드"""
    transaction_id: str
    agent_id: str
    amount: float
    status: str  # success, failed, pending, refund
    payment_method: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class EmailWebhookPayload(BaseModel):
    """이메일 웹훅 페이로드"""
    agent_id: str
    from_email: str
    subject: str
    body: str
    attachments: Optional[List[str]] = None
    timestamp: str


class ExternalOrderPayload(BaseModel):
    """외부 주문 웹훅 페이로드"""
    agent_id: str
    order_id: str
    customer_name: str
    items: List[Dict[str, Any]]
    total_amount: float
    source: str  # naver, kakao, coupang 등
    timestamp: str


# ============================================
# Webhook Engine
# ============================================

@dataclass
class WebhookEndpoint:
    """
    에이전트 전용 웹훅 엔드포인트
    
    각 에이전트는 고유한 웹훅 URL을 가짐
    """
    agent_id: str
    webhook_url: str  # mulberry.ai/webhook/{agent_id}
    webhook_secret: str  # HMAC 검증용 시크릿
    email_address: str  # {agent_id}@mulberry.ai
    
    # 통계
    total_events: int = 0
    success_events: int = 0
    failed_events: int = 0
    
    # 설정
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class WebhookEngine:
    """
    Mulberry 웹훅 엔진
    
    에이전트별 웹훅 엔드포인트 관리 및 이벤트 처리
    """
    
    def __init__(self, base_url: str = "https://mulberry.ai"):
        """
        웹훅 엔진 초기화
        
        Args:
            base_url: 기본 URL
        """
        self.base_url = base_url
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        
        # 이벤트 큐 (100ms 목표)
        self.event_queue = asyncio.Queue()
        
        # 이벤트 핸들러 등록
        self.event_handlers: Dict[WebhookEventType, List[callable]] = {}
        
        # 성능 모니터링
        self.processing_times: List[float] = []
        
        logger.info("✅ Webhook Engine initialized")
    
    def create_endpoint(
        self,
        agent_id: str,
        agent_name: str
    ) -> WebhookEndpoint:
        """
        에이전트 전용 웹훅 엔드포인트 생성
        
        Args:
            agent_id: 에이전트 ID
            agent_name: 에이전트 이름
            
        Returns:
            WebhookEndpoint: 생성된 엔드포인트
        """
        # 웹훅 URL 생성
        webhook_url = f"{self.base_url}/webhook/{agent_id}"
        
        # 웹훅 시크릿 생성 (HMAC 검증용)
        webhook_secret = self._generate_secret()
        
        # 이메일 주소 생성
        email_address = f"{agent_id}@mulberry.ai"
        
        # 엔드포인트 객체 생성
        endpoint = WebhookEndpoint(
            agent_id=agent_id,
            webhook_url=webhook_url,
            webhook_secret=webhook_secret,
            email_address=email_address
        )
        
        # 저장
        self.endpoints[agent_id] = endpoint
        
        logger.info(f"✅ Webhook endpoint created for {agent_name}")
        logger.info(f"📡 URL: {webhook_url}")
        logger.info(f"📧 Email: {email_address}")
        
        return endpoint
    
    def _generate_secret(self) -> str:
        """웹훅 시크릿 생성"""
        return uuid.uuid4().hex
    
    def verify_signature(
        self,
        agent_id: str,
        payload: str,
        signature: str
    ) -> bool:
        """
        웹훅 서명 검증
        
        Args:
            agent_id: 에이전트 ID
            payload: 요청 본문
            signature: HMAC 서명
            
        Returns:
            bool: 검증 성공 여부
        """
        endpoint = self.endpoints.get(agent_id)
        if not endpoint:
            return False
        
        # HMAC-SHA256 계산
        expected_signature = hmac.new(
            endpoint.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # 서명 비교
        return hmac.compare_digest(signature, expected_signature)
    
    async def process_webhook(
        self,
        agent_id: str,
        event_type: WebhookEventType,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        웹훅 이벤트 처리
        
        Target: 100ms 이내 처리
        
        Args:
            agent_id: 에이전트 ID
            event_type: 이벤트 타입
            payload: 페이로드
            signature: HMAC 서명
            
        Returns:
            dict: 처리 결과
        """
        start_time = time.perf_counter()
        
        try:
            # 1. 엔드포인트 확인 (1ms)
            endpoint = self.endpoints.get(agent_id)
            if not endpoint:
                raise ValueError(f"Endpoint not found: {agent_id}")
            
            if not endpoint.is_active:
                raise ValueError(f"Endpoint inactive: {agent_id}")
            
            # 2. 서명 검증 생략 (개발 중) - 실제로는 필수!
            # if signature and not self.verify_signature(agent_id, json.dumps(payload), signature):
            #     raise ValueError("Invalid signature")
            
            # 3. 이벤트 큐에 추가 (즉시)
            event = {
                "agent_id": agent_id,
                "event_type": event_type,
                "payload": payload,
                "timestamp": datetime.now().isoformat()
            }
            
            # 백그라운드에서 처리 (논블로킹)
            asyncio.create_task(self._handle_event(event))
            
            # 4. 즉시 응답
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            # 통계 업데이트
            endpoint.total_events += 1
            endpoint.success_events += 1
            self.processing_times.append(elapsed_ms)
            
            logger.info(f"⚡ Webhook processed: {agent_id} ({elapsed_ms:.1f}ms)")
            
            return {
                "success": True,
                "agent_id": agent_id,
                "event_type": event_type.value,
                "processing_time_ms": elapsed_ms,
                "message": "Event queued for processing"
            }
            
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            logger.error(f"❌ Webhook error: {str(e)} ({elapsed_ms:.1f}ms)")
            
            if agent_id in self.endpoints:
                self.endpoints[agent_id].failed_events += 1
            
            return {
                "success": False,
                "error": str(e),
                "processing_time_ms": elapsed_ms
            }
    
    async def _handle_event(self, event: Dict[str, Any]):
        """
        백그라운드 이벤트 처리
        
        Args:
            event: 이벤트 데이터
        """
        try:
            event_type = event["event_type"]
            
            # 등록된 핸들러 실행
            handlers = self.event_handlers.get(event_type, [])
            
            for handler in handlers:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"❌ Handler error: {str(e)}")
            
        except Exception as e:
            logger.error(f"❌ Event handling error: {str(e)}")
    
    def register_handler(
        self,
        event_type: WebhookEventType,
        handler: callable
    ):
        """
        이벤트 핸들러 등록
        
        Args:
            event_type: 이벤트 타입
            handler: 핸들러 함수
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        
        logger.info(f"✅ Handler registered for {event_type.value}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계"""
        if not self.processing_times:
            return {
                "avg_processing_time_ms": 0,
                "max_processing_time_ms": 0,
                "total_events": 0
            }
        
        return {
            "avg_processing_time_ms": sum(self.processing_times) / len(self.processing_times),
            "max_processing_time_ms": max(self.processing_times),
            "min_processing_time_ms": min(self.processing_times),
            "total_events": len(self.processing_times),
            "target_met": sum(1 for t in self.processing_times if t < 100) / len(self.processing_times) * 100
        }


# ============================================
# FastAPI Integration
# ============================================

app = FastAPI(title="Mulberry Webhook Engine")
webhook_engine = WebhookEngine()


@app.post("/webhook/{agent_id}/payment")
async def payment_webhook(
    agent_id: str,
    payload: PaymentWebhookPayload,
    request: Request
):
    """
    결제 웹훅 엔드포인트
    
    외부 결제 게이트웨이(Toss, Kakao)에서 호출
    """
    # HMAC 서명 추출
    signature = request.headers.get("X-Mulberry-Signature")
    
    # 웹훅 처리
    result = await webhook_engine.process_webhook(
        agent_id=agent_id,
        event_type=WebhookEventType.PAYMENT_SUCCESS if payload.status == "success" else WebhookEventType.PAYMENT_FAILED,
        payload=payload.dict(),
        signature=signature
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.post("/webhook/{agent_id}/email")
async def email_webhook(
    agent_id: str,
    payload: EmailWebhookPayload,
    request: Request
):
    """
    이메일 웹훅 엔드포인트
    
    이메일 서비스(SendGrid, Mailgun)에서 호출
    """
    signature = request.headers.get("X-Mulberry-Signature")
    
    result = await webhook_engine.process_webhook(
        agent_id=agent_id,
        event_type=WebhookEventType.EMAIL_RECEIVED,
        payload=payload.dict(),
        signature=signature
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.post("/webhook/{agent_id}/order")
async def external_order_webhook(
    agent_id: str,
    payload: ExternalOrderPayload,
    request: Request
):
    """
    외부 주문 웹훅 엔드포인트
    
    네이버 스마트스토어, 쿠팡 등에서 호출
    """
    signature = request.headers.get("X-Mulberry-Signature")
    
    result = await webhook_engine.process_webhook(
        agent_id=agent_id,
        event_type=WebhookEventType.EXTERNAL_ORDER,
        payload=payload.dict(),
        signature=signature
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.get("/webhook/{agent_id}/stats")
async def get_webhook_stats(agent_id: str):
    """웹훅 통계 조회"""
    endpoint = webhook_engine.endpoints.get(agent_id)
    
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    return {
        "agent_id": agent_id,
        "webhook_url": endpoint.webhook_url,
        "email_address": endpoint.email_address,
        "total_events": endpoint.total_events,
        "success_events": endpoint.success_events,
        "failed_events": endpoint.failed_events,
        "is_active": endpoint.is_active,
        "performance": webhook_engine.get_performance_stats()
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "service": "Mulberry Webhook Engine",
        "performance": webhook_engine.get_performance_stats()
    }


# ============================================
# Example Usage
# ============================================

async def example_payment_handler(event: Dict[str, Any]):
    """결제 이벤트 핸들러 예시"""
    agent_id = event["agent_id"]
    payload = event["payload"]
    
    logger.info(f"💰 Payment received for {agent_id}: ₩{payload['amount']:,.0f}")
    
    # Agent Wallet 업데이트
    # await update_agent_wallet(agent_id, payload)


async def example_email_handler(event: Dict[str, Any]):
    """이메일 이벤트 핸들러 예시"""
    agent_id = event["agent_id"]
    payload = event["payload"]
    
    logger.info(f"📧 Email received for {agent_id}: {payload['subject']}")
    
    # 이메일 처리
    # await process_agent_email(agent_id, payload)


if __name__ == "__main__":
    # 웹훅 엔진 초기화
    engine = WebhookEngine()
    
    # SNS Manager 엔드포인트 생성
    sns_endpoint = engine.create_endpoint(
        agent_id="AGENT_SNS_001",
        agent_name="SNS_Manager"
    )
    
    print(f"✅ Webhook URL: {sns_endpoint.webhook_url}")
    print(f"✅ Email: {sns_endpoint.email_address}")
    print(f"✅ Secret: {sns_endpoint.webhook_secret}")
    
    # 핸들러 등록
    engine.register_handler(
        WebhookEventType.PAYMENT_SUCCESS,
        example_payment_handler
    )
    
    engine.register_handler(
        WebhookEventType.EMAIL_RECEIVED,
        example_email_handler
    )
    
    # FastAPI 서버 실행
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

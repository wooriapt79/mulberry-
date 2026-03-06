"""
Mulberry Phase 1+ - Payment Service
Google Pay API 및 AP2 (Agent-to-Agent Payment) 프로토콜 연동
"""

import json
import uuid
import hmac
import hashlib
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from loguru import logger

from app.config import settings


class PaymentService:
    """
    결제 서비스
    - Google Pay API 연동
    - Agent-to-Person (A2P) 결제
    - Agent-to-Agent (A2A) 자율 정산 (AP2 프로토콜)
    """
    
    def __init__(self):
        """Payment Service 초기화"""
        self.merchant_id = settings.google_pay_merchant_id
        self.merchant_name = settings.google_pay_merchant_name
        self.environment = settings.google_pay_environment
        self.currency = settings.payment_currency
        
        # Google Pay API 엔드포인트
        if self.environment == "PRODUCTION":
            self.base_url = "https://pay.google.com/gp/v/pay"
        else:
            self.base_url = "https://pay.google.com/gp/v/test"
        
        # HTTP 클라이언트
        self.client = httpx.AsyncClient(
            timeout=30,
            headers={
                "Content-Type": "application/json"
            }
        )
        
        # AP2 설정
        self.ap2_enabled = settings.ap2_enabled
        self.ap2_settlement_interval = settings.ap2_settlement_interval_hours
        
        logger.info(f"✅ Payment service initialized (env={self.environment}, AP2={self.ap2_enabled})")
    
    async def close(self):
        """HTTP 클라이언트 종료"""
        await self.client.aclose()
    
    # ============================================
    # 1. Google Pay 통합 (A2P: Agent-to-Person)
    # ============================================
    
    async def create_payment_intent(
        self,
        order_id: int,
        amount: Decimal,
        currency: str = None,
        description: Optional[str] = None,
        customer_email: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        결제 요청 생성 (Google Pay Payment Intent)
        
        Args:
            order_id: 주문 ID
            amount: 결제 금액
            currency: 통화 (기본: KRW)
            description: 결제 설명
            customer_email: 고객 이메일
            metadata: 추가 메타데이터
            
        Returns:
            dict: 결제 Intent 정보
        """
        try:
            if currency is None:
                currency = self.currency
            
            # 금액 검증
            amount_int = int(amount)
            if amount_int < settings.payment_min_amount:
                raise ValueError(f"Amount too small: {amount_int} < {settings.payment_min_amount}")
            if amount_int > settings.payment_max_amount:
                raise ValueError(f"Amount too large: {amount_int} > {settings.payment_max_amount}")
            
            # Transaction ID 생성
            transaction_id = f"MULB{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
            
            logger.info(f"💳 Creating payment intent for Order #{order_id}: {amount_int} {currency}")
            
            # Google Pay Payment Data 구조
            payment_data = {
                "apiVersion": 2,
                "apiVersionMinor": 0,
                "allowedPaymentMethods": [
                    {
                        "type": "CARD",
                        "parameters": {
                            "allowedAuthMethods": ["PAN_ONLY", "CRYPTOGRAM_3DS"],
                            "allowedCardNetworks": ["MASTERCARD", "VISA"]
                        },
                        "tokenizationSpecification": {
                            "type": "PAYMENT_GATEWAY",
                            "parameters": {
                                "gateway": "example",  # 실제 PG사로 교체 필요
                                "gatewayMerchantId": self.merchant_id
                            }
                        }
                    }
                ],
                "merchantInfo": {
                    "merchantId": self.merchant_id,
                    "merchantName": self.merchant_name
                },
                "transactionInfo": {
                    "totalPriceStatus": "FINAL",
                    "totalPriceLabel": "Total",
                    "totalPrice": str(amount_int),
                    "currencyCode": currency,
                    "countryCode": "KR"
                }
            }
            
            # 내부 결제 Intent 저장 (DB에 저장 예정)
            payment_intent = {
                "transaction_id": transaction_id,
                "order_id": order_id,
                "amount": float(amount),
                "currency": currency,
                "status": "pending",
                "payment_method": "google_pay",
                "description": description or f"Order #{order_id}",
                "customer_email": customer_email,
                "metadata": metadata or {},
                "google_pay_data": payment_data,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
            logger.info(f"✅ Payment intent created: {transaction_id}")
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "payment_intent": payment_intent,
                "google_pay_config": payment_data
            }
            
        except ValueError as e:
            logger.error(f"❌ Payment validation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"❌ Failed to create payment intent: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_payment(
        self,
        transaction_id: str,
        payment_token: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Google Pay 결제 완료 검증
        
        Args:
            transaction_id: Transaction ID
            payment_token: Google Pay가 반환한 결제 토큰
            
        Returns:
            dict: 검증 결과
        """
        try:
            logger.info(f"🔍 Verifying payment: {transaction_id}")
            
            # Google Pay 토큰 검증
            signature = payment_token.get("signature")
            signed_message = payment_token.get("signedMessage")
            
            # 서명 검증 (실제로는 Google의 공개키로 검증)
            is_valid = self._verify_signature(signed_message, signature)
            
            if not is_valid:
                logger.error(f"❌ Invalid payment signature")
                return {
                    "success": False,
                    "error": "Invalid signature"
                }
            
            # 결제 데이터 파싱
            payment_data = json.loads(signed_message)
            
            # DB에서 결제 Intent 조회 및 상태 업데이트 (향후 구현)
            # payment_intent = await db.get_payment_intent(transaction_id)
            # payment_intent.status = "completed"
            
            logger.info(f"✅ Payment verified: {transaction_id}")
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": "completed",
                "payment_data": payment_data,
                "verified_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Payment verification failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _verify_signature(self, message: str, signature: str) -> bool:
        """
        Google Pay 서명 검증 (간소화 버전)
        실제로는 Google의 공개키를 사용해야 함
        """
        # 실제 구현 시: Google의 공개키로 서명 검증
        # 여기서는 간단히 HMAC으로 대체
        try:
            expected_signature = hmac.new(
                key=settings.secret_key.encode(),
                msg=message.encode(),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        결제 환불
        
        Args:
            transaction_id: Transaction ID
            amount: 환불 금액 (None이면 전액)
            reason: 환불 사유
            
        Returns:
            dict: 환불 결과
        """
        try:
            logger.info(f"💸 Processing refund for {transaction_id}")
            
            # DB에서 원본 결제 조회 (향후 구현)
            # original_payment = await db.get_payment(transaction_id)
            
            # 환불 ID 생성
            refund_id = f"REFUND{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
            
            # Google Pay Refund API 호출 (실제 구현 필요)
            # ...
            
            refund_data = {
                "refund_id": refund_id,
                "original_transaction_id": transaction_id,
                "amount": float(amount) if amount else None,
                "reason": reason,
                "status": "completed",
                "refunded_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Refund completed: {refund_id}")
            
            return {
                "success": True,
                "refund_data": refund_data
            }
            
        except Exception as e:
            logger.error(f"❌ Refund failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================
    # 2. AP2 프로토콜 (Agent-to-Agent Payment)
    # ============================================
    
    async def create_agent_payment(
        self,
        from_agent_id: str,
        to_agent_id: str,
        amount: Decimal,
        purpose: str,
        metadata: Optional[Dict] = None,
        use_local_cache: bool = True  # 산간 지역 대비
    ) -> Dict[str, Any]:
        """
        에이전트 간 자율 정산 (A2A) - 네트워크 장애 대비 강화
        
        Args:
            from_agent_id: 지불 에이전트 ID
            to_agent_id: 수취 에이전트 ID
            amount: 금액
            purpose: 목적 (commission, revenue_share, service_fee 등)
            metadata: 추가 메타데이터
            use_local_cache: 로컬 캐시 사용 여부 (산간 지역 true)
            
        Returns:
            dict: 정산 결과
        """
        try:
            if not self.ap2_enabled:
                logger.warning("⚠️ AP2 protocol is disabled")
                return {
                    "success": False,
                    "error": "AP2 protocol not enabled"
                }
            
            logger.info(f"🤝 Creating agent payment: {from_agent_id} → {to_agent_id} ({amount} {self.currency})")
            
            # AP2 Transaction ID
            ap2_tx_id = f"AP2{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
            
            # AP2 프로토콜 페이로드
            ap2_payload = {
                "protocol_version": "AP2_v1.0",
                "transaction_id": ap2_tx_id,
                "from_agent": {
                    "agent_id": from_agent_id,
                    "agent_type": "mulberry_ai_assistant"
                },
                "to_agent": {
                    "agent_id": to_agent_id,
                    "agent_type": "mulberry_ai_assistant"
                },
                "payment": {
                    "amount": float(amount),
                    "currency": self.currency,
                    "purpose": purpose,
                    "settlement_type": "instant"  # instant, batch, scheduled
                },
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "signature": self._generate_ap2_signature(from_agent_id, to_agent_id, float(amount)),
                "network_status": "online"  # 초기 상태
            }
            
            # ============================================
            # 🆕 산간 지역 네트워크 장애 대비 로직
            # ============================================
            if use_local_cache:
                try:
                    # 1. 로컬 캐시 선행 저장 (SQLite 또는 파일)
                    await self._save_to_local_cache(ap2_payload)
                    logger.info(f"💾 AP2 transaction cached locally: {ap2_tx_id}")
                    
                    # 2. 네트워크 연결 테스트 (Timeout 3초)
                    network_available = await self._test_network_connection(timeout=3)
                    
                    if network_available:
                        # 네트워크 정상 → 즉시 브로드캐스트
                        broadcast_success = await self._broadcast_to_ap2_network(
                            ap2_payload, 
                            timeout=5  # 5초 타임아웃
                        )
                        
                        if broadcast_success:
                            ap2_payload["network_status"] = "synced"
                            logger.info(f"✅ AP2 transaction synced to network: {ap2_tx_id}")
                        else:
                            # 브로드캐스트 실패 → 백그라운드 재시도 큐에 추가
                            ap2_payload["network_status"] = "pending_sync"
                            await self._enqueue_for_retry(ap2_payload)
                            logger.warning(f"⏳ AP2 transaction queued for retry: {ap2_tx_id}")
                    else:
                        # 네트워크 불안정 → 사후 동기화 대기열
                        ap2_payload["network_status"] = "offline_cached"
                        await self._enqueue_for_retry(ap2_payload)
                        logger.warning(f"📡 Network unavailable. AP2 cached for later sync: {ap2_tx_id}")
                    
                except Exception as cache_error:
                    logger.error(f"❌ Local cache error: {str(cache_error)}")
                    # 캐시 실패해도 계속 진행 (resilience)
            
            # AP2 네트워크로 브로드캐스트 (실제로는 분산 원장에 기록)
            # await self._broadcast_to_ap2_network(ap2_payload)
            
            logger.info(f"✅ Agent payment created: {ap2_tx_id}")
            
            return {
                "success": True,
                "ap2_transaction_id": ap2_tx_id,
                "payload": ap2_payload,
                "status": "pending_settlement",
                "network_status": ap2_payload["network_status"]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to create agent payment: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_ap2_signature(
        self,
        from_agent: str,
        to_agent: str,
        amount: float
    ) -> str:
        """AP2 트랜잭션 서명 생성"""
        message = f"{from_agent}|{to_agent}|{amount}|{datetime.now().isoformat()}"
        
        signature = hmac.new(
            key=settings.secret_key.encode(),
            msg=message.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return signature
    
    async def settle_agent_payments(
        self,
        batch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        일괄 정산 처리 (배치 처리)
        
        Args:
            batch_id: 배치 ID (None이면 대기 중인 모든 정산 처리)
            
        Returns:
            dict: 정산 결과
        """
        try:
            logger.info(f"💰 Starting batch settlement (batch_id={batch_id})")
            
            # DB에서 대기 중인 AP2 트랜잭션 조회 (향후 구현)
            # pending_txs = await db.get_pending_ap2_transactions(batch_id)
            
            # 임시 데이터
            pending_txs = []
            
            settled_count = 0
            total_amount = Decimal('0')
            
            for tx in pending_txs:
                # 각 트랜잭션 정산
                tx_id = tx.get("ap2_transaction_id")
                amount = Decimal(str(tx.get("payment", {}).get("amount", 0)))
                
                # 정산 처리 (실제로는 은행 API 또는 블록체인)
                success = await self._execute_settlement(tx)
                
                if success:
                    settled_count += 1
                    total_amount += amount
                    logger.info(f"✅ Settled: {tx_id}")
                else:
                    logger.error(f"❌ Failed to settle: {tx_id}")
            
            batch_result = {
                "batch_id": batch_id or f"BATCH{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "settled_count": settled_count,
                "total_amount": float(total_amount),
                "currency": self.currency,
                "settled_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Batch settlement completed: {settled_count} transactions, {total_amount} {self.currency}")
            
            return {
                "success": True,
                "batch_result": batch_result
            }
            
        except Exception as e:
            logger.error(f"❌ Batch settlement failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_settlement(self, transaction: Dict[str, Any]) -> bool:
        """개별 정산 실행"""
        try:
            # 실제로는 은행 API 또는 스마트 컨트랙트 호출
            logger.debug(f"Executing settlement: {transaction.get('transaction_id')}")
            return True
        except Exception:
            return False
    
    # ============================================
    # 🆕 네트워크 장애 대비 헬퍼 메서드
    # ============================================
    
    async def _test_network_connection(self, timeout: int = 3) -> bool:
        """
        네트워크 연결 상태 테스트
        
        Args:
            timeout: 타임아웃 (초)
            
        Returns:
            bool: 연결 가능 여부
        """
        try:
            # 외부 API 또는 AP2 네트워크 헬스체크 엔드포인트 호출
            response = await self.client.get(
                "https://api.mulberry.kr/health",  # 실제 엔드포인트로 변경
                timeout=timeout
            )
            return response.status_code == 200
        except (httpx.TimeoutException, httpx.RequestError):
            logger.warning("⚠️ Network connection test failed")
            return False
    
    async def _save_to_local_cache(self, payload: Dict[str, Any]):
        """
        로컬 캐시에 저장 (SQLite 또는 파일 시스템)
        
        Args:
            payload: AP2 트랜잭션 페이로드
        """
        try:
            import json
            import os
            
            # 로컬 캐시 디렉토리
            cache_dir = "/tmp/mulberry_ap2_cache"
            os.makedirs(cache_dir, exist_ok=True)
            
            # 트랜잭션 ID 기반 파일명
            tx_id = payload["transaction_id"]
            cache_file = os.path.join(cache_dir, f"{tx_id}.json")
            
            # JSON 파일로 저장
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"💾 Saved to local cache: {cache_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save local cache: {str(e)}")
            raise
    
    async def _broadcast_to_ap2_network(
        self, 
        payload: Dict[str, Any],
        timeout: int = 5
    ) -> bool:
        """
        AP2 네트워크로 브로드캐스트
        
        Args:
            payload: AP2 트랜잭션 페이로드
            timeout: 타임아웃 (초)
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 실제 AP2 네트워크 엔드포인트 (분산 원장 또는 블록체인)
            ap2_endpoint = "https://ap2.mulberry.kr/v1/transactions"
            
            response = await self.client.post(
                ap2_endpoint,
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Broadcasted to AP2 network: {payload['transaction_id']}")
                return True
            else:
                logger.warning(f"⚠️ AP2 broadcast failed: {response.status_code}")
                return False
                
        except httpx.TimeoutException:
            logger.warning(f"⏱️ AP2 broadcast timeout (>{timeout}s)")
            return False
        except httpx.RequestError as e:
            logger.error(f"❌ AP2 broadcast network error: {str(e)}")
            return False
    
    async def _enqueue_for_retry(self, payload: Dict[str, Any]):
        """
        재시도 큐에 추가 (백그라운드 동기화)
        
        Args:
            payload: AP2 트랜잭션 페이로드
        """
        try:
            # Redis 큐 또는 Celery 작업으로 추가
            # 여기서는 간단히 파일 시스템 큐 사용
            
            import json
            import os
            
            queue_dir = "/tmp/mulberry_ap2_retry_queue"
            os.makedirs(queue_dir, exist_ok=True)
            
            tx_id = payload["transaction_id"]
            queue_file = os.path.join(queue_dir, f"{tx_id}_retry.json")
            
            # 재시도 메타데이터 추가
            retry_payload = {
                **payload,
                "retry_count": 0,
                "max_retries": 5,
                "next_retry_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
                "queued_at": datetime.now().isoformat()
            }
            
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(retry_payload, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📥 Enqueued for retry: {tx_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to enqueue for retry: {str(e)}")
    
    async def process_retry_queue(self) -> Dict[str, Any]:
        """
        재시도 큐 처리 (백그라운드 작업)
        
        Returns:
            dict: 처리 결과
        """
        try:
            import json
            import os
            
            queue_dir = "/tmp/mulberry_ap2_retry_queue"
            
            if not os.path.exists(queue_dir):
                return {"processed": 0, "success": 0, "failed": 0}
            
            processed = 0
            success = 0
            failed = 0
            
            # 큐의 모든 파일 처리
            for filename in os.listdir(queue_dir):
                if not filename.endswith("_retry.json"):
                    continue
                
                file_path = os.path.join(queue_dir, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        retry_payload = json.load(f)
                    
                    # 재시도 시간 확인
                    next_retry = datetime.fromisoformat(retry_payload["next_retry_at"])
                    if datetime.now() < next_retry:
                        continue  # 아직 시간 안 됨
                    
                    # 재시도 횟수 확인
                    if retry_payload["retry_count"] >= retry_payload["max_retries"]:
                        logger.error(f"❌ Max retries reached: {retry_payload['transaction_id']}")
                        os.remove(file_path)
                        failed += 1
                        continue
                    
                    # 브로드캐스트 재시도
                    broadcast_success = await self._broadcast_to_ap2_network(
                        retry_payload,
                        timeout=10  # 재시도 시 더 긴 타임아웃
                    )
                    
                    if broadcast_success:
                        # 성공 → 큐에서 제거
                        os.remove(file_path)
                        success += 1
                        logger.info(f"✅ Retry successful: {retry_payload['transaction_id']}")
                    else:
                        # 실패 → 재시도 카운트 증가
                        retry_payload["retry_count"] += 1
                        retry_payload["next_retry_at"] = (
                            datetime.now() + timedelta(minutes=10 * retry_payload["retry_count"])
                        ).isoformat()
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(retry_payload, f, ensure_ascii=False, indent=2)
                        
                        failed += 1
                        logger.warning(f"⏳ Retry failed, will retry again: {retry_payload['transaction_id']}")
                    
                    processed += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error processing retry file {filename}: {str(e)}")
                    continue
            
            result = {
                "processed": processed,
                "success": success,
                "failed": failed
            }
            
            logger.info(f"📊 Retry queue processed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Retry queue processing error: {str(e)}")
            return {"error": str(e)}
    
    # ============================================
    # 3. 결제 수단 관리
    # ============================================
    
    async def save_payment_method(
        self,
        user_id: int,
        payment_method_type: str,
        token: str,
        is_default: bool = False
    ) -> Dict[str, Any]:
        """
        결제 수단 저장 (Google Pay 토큰 등)
        
        Args:
            user_id: 사용자 ID
            payment_method_type: 결제 수단 종류 (google_pay, card, bank_transfer)
            token: 토큰화된 결제 정보
            is_default: 기본 결제 수단 여부
            
        Returns:
            dict: 저장 결과
        """
        try:
            payment_method_id = f"PM{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
            
            payment_method = {
                "payment_method_id": payment_method_id,
                "user_id": user_id,
                "type": payment_method_type,
                "token": token,  # 실제로는 암호화 필요
                "is_default": is_default,
                "created_at": datetime.now().isoformat()
            }
            
            # DB 저장 (향후 구현)
            # await db.save_payment_method(payment_method)
            
            logger.info(f"✅ Payment method saved: {payment_method_id}")
            
            return {
                "success": True,
                "payment_method_id": payment_method_id
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to save payment method: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_payment_methods(self, user_id: int) -> List[Dict[str, Any]]:
        """사용자의 저장된 결제 수단 목록 조회"""
        try:
            # DB 조회 (향후 구현)
            # payment_methods = await db.get_payment_methods(user_id)
            
            return []
        except Exception as e:
            logger.error(f"❌ Failed to get payment methods: {str(e)}")
            return []


# ============================================
# 싱글톤 인스턴스
# ============================================

_payment_service_instance: Optional[PaymentService] = None


def get_payment_service() -> PaymentService:
    """
    싱글톤 Payment 서비스 인스턴스 반환
    
    Returns:
        PaymentService: 서비스 인스턴스
    """
    global _payment_service_instance
    
    if _payment_service_instance is None:
        _payment_service_instance = PaymentService()
    
    return _payment_service_instance


# ============================================
# 테스트용 메인 함수
# ============================================

async def test_payment_service():
    """Payment Service 테스트"""
    service = get_payment_service()
    
    # 1. Google Pay 결제 Intent 생성
    payment_intent = await service.create_payment_intent(
        order_id=1,
        amount=Decimal('50000'),
        description="사과 10kg",
        customer_email="customer@example.com"
    )
    logger.info(f"Payment Intent: {payment_intent}")
    
    # 2. AP2 에이전트 간 결제
    agent_payment = await service.create_agent_payment(
        from_agent_id="agent_farmer_001",
        to_agent_id="agent_delivery_002",
        amount=Decimal('3000'),
        purpose="delivery_commission"
    )
    logger.info(f"Agent Payment: {agent_payment}")
    
    # 3. 일괄 정산
    settlement = await service.settle_agent_payments()
    logger.info(f"Settlement: {settlement}")
    
    await service.close()


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    asyncio.run(test_payment_service())

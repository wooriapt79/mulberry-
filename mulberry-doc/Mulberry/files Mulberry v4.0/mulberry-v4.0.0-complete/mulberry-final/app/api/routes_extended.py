"""
Mulberry Phase 1+ - Extended API Routes
예약, 결제, 구글 비즈니스 API 엔드포인트
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field, EmailStr
from loguru import logger

from app.database import get_async_db
from app.models import (
    Reservation, ReservationItem, Payment, Refund,
    AP2Transaction, GoogleReview, GoogleBusinessMetric, Farm
)
from app.services import (
    get_google_service,
    get_payment_service
)


# ============================================
# Pydantic Schemas
# ============================================

# Reservation Schemas
class ReservationItemCreate(BaseModel):
    """예약 항목 생성"""
    product_name: str
    quantity: float
    unit: str
    unit_price: Optional[float] = None


class VoiceReservationCreate(BaseModel):
    """음성 예약 생성 (Edge AI에서 전송)"""
    customer_phone: str = Field(..., example="010-1234-5678")
    customer_name: Optional[str] = Field(None, example="김철수")
    farm_id: int
    requested_items: List[ReservationItemCreate]
    delivery_address: Optional[str] = None
    preferred_date: Optional[date] = None
    notes: Optional[str] = None
    audio_transcription: Optional[str] = None
    dialect: Optional[str] = Field(None, example="경상도")


class ReservationResponse(BaseModel):
    """예약 응답"""
    reservation_id: int
    reservation_number: str
    customer_name: Optional[str]
    customer_phone: str
    farm_id: Optional[int]
    status: str
    total_amount: Optional[float]
    preferred_date: Optional[date]
    created_via: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Payment Schemas
class PaymentIntentCreate(BaseModel):
    """결제 Intent 생성"""
    order_id: Optional[int] = None
    reservation_id: Optional[int] = None
    amount: float = Field(..., gt=0, example=50000)
    description: Optional[str] = Field(None, example="사과 10kg 주문")
    customer_email: Optional[EmailStr] = None


class PaymentResponse(BaseModel):
    """결제 응답"""
    payment_id: int
    transaction_id: str
    amount: float
    currency: str
    payment_method: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Google Business Schemas
class GoogleReviewResponse(BaseModel):
    """구글 리뷰 응답"""
    review_id: int
    gmb_review_id: str
    farm_id: int
    star_rating: Optional[int]
    comment: Optional[str]
    reply_text: Optional[str]
    reply_status: str
    reviewer_name: Optional[str]
    
    class Config:
        from_attributes = True


# ============================================
# Router Initialization
# ============================================

router = APIRouter(prefix="/api/v1", tags=["Mulberry API v1 - Extended"])


# ============================================
# Reservation Endpoints
# ============================================

@router.post("/reservations/voice", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_voice_reservation(
    reservation_data: VoiceReservationCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    음성 예약 생성 (Edge AI 라즈베리파이에서 호출)
    
    - 전화 통화를 통한 음성 주문 처리
    - DeepSeek-R1 + 사투리 인식
    - 자동 예약 번호 생성
    """
    google_service = get_google_service()
    
    # Google Service를 통해 음성 예약 처리
    call_data = {
        "customer_phone": reservation_data.customer_phone,
        "customer_name": reservation_data.customer_name,
        "farm_id": reservation_data.farm_id,
        "requested_items": [item.dict() for item in reservation_data.requested_items],
        "delivery_address": reservation_data.delivery_address,
        "preferred_date": str(reservation_data.preferred_date) if reservation_data.preferred_date else None,
        "notes": reservation_data.notes,
        "audio_transcription": reservation_data.audio_transcription,
        "dialect": reservation_data.dialect
    }
    
    result = await google_service.handle_voice_reservation(call_data)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to process voice reservation")
        )
    
    # DB에 예약 저장
    reservation_number = result["reservation_number"]
    res_data = result["reservation_data"]
    
    # 총액 계산
    total_amount = sum(
        Decimal(str(item.get("quantity", 0))) * Decimal(str(item.get("unit_price", 0)))
        for item in res_data["items"]
        if item.get("quantity") and item.get("unit_price")
    )
    
    new_reservation = Reservation(
        reservation_number=reservation_number,
        farm_id=res_data["farm_id"],
        customer_name=res_data["customer_name"],
        customer_phone=res_data["customer_phone"],
        delivery_address=res_data.get("delivery_address"),
        preferred_date=res_data.get("preferred_date"),
        total_amount=total_amount,
        status="pending",
        created_via="voice_call",
        dialect_detected=res_data.get("dialect_detected"),
        original_transcription=res_data.get("original_transcription"),
        notes=res_data.get("notes")
    )
    
    db.add(new_reservation)
    await db.flush()
    
    # 예약 항목 저장
    for item in res_data["items"]:
        res_item = ReservationItem(
            reservation_id=new_reservation.reservation_id,
            product_name=item["product_name"],
            quantity=Decimal(str(item.get("quantity", 0))),
            unit=item.get("unit"),
            unit_price=Decimal(str(item.get("unit_price", 0))) if item.get("unit_price") else None,
            subtotal=Decimal(str(item.get("quantity", 0))) * Decimal(str(item.get("unit_price", 0))) if item.get("quantity") and item.get("unit_price") else None
        )
        db.add(res_item)
    
    await db.commit()
    await db.refresh(new_reservation)
    
    logger.info(f"✅ Voice reservation created in DB: {reservation_number}")
    
    return {
        "success": True,
        "reservation_number": reservation_number,
        "reservation_id": new_reservation.reservation_id,
        "message": result.get("message"),
        "total_amount": float(total_amount)
    }


@router.get("/reservations", response_model=List[ReservationResponse])
async def get_reservations(
    farm_id: Optional[int] = Query(None, description="농장 ID"),
    status: Optional[str] = Query(None, description="예약 상태"),
    customer_phone: Optional[str] = Query(None, description="고객 전화번호"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """
    예약 목록 조회
    
    - 농장별, 상태별, 고객별 필터링
    """
    stmt = select(Reservation)
    
    if farm_id:
        stmt = stmt.where(Reservation.farm_id == farm_id)
    
    if status:
        stmt = stmt.where(Reservation.status == status)
    
    if customer_phone:
        stmt = stmt.where(Reservation.customer_phone == customer_phone)
    
    stmt = stmt.order_by(Reservation.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    reservations = result.scalars().all()
    
    return reservations


@router.patch("/reservations/{reservation_id}/status")
async def update_reservation_status(
    reservation_id: int,
    new_status: str = Query(..., regex="^(pending|confirmed|completed|cancelled)$"),
    db: AsyncSession = Depends(get_async_db)
):
    """예약 상태 업데이트"""
    stmt = select(Reservation).where(Reservation.reservation_id == reservation_id)
    result = await db.execute(stmt)
    reservation = result.scalar_one_or_none()
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation {reservation_id} not found"
        )
    
    reservation.status = new_status
    
    if new_status == "confirmed":
        reservation.confirmed_at = datetime.now()
    elif new_status == "completed":
        reservation.completed_at = datetime.now()
    
    await db.commit()
    
    logger.info(f"✅ Reservation status updated: {reservation_id} → {new_status}")
    
    return {"reservation_id": reservation_id, "status": new_status}


# ============================================
# Payment Endpoints
# ============================================

@router.post("/payments/intent", response_model=Dict[str, Any])
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Google Pay 결제 Intent 생성
    
    - 주문 또는 예약에 대한 결제 요청 생성
    - Google Pay 설정 반환
    """
    payment_service = get_payment_service()
    
    # Order ID 또는 Reservation ID 필수
    if not payment_data.order_id and not payment_data.reservation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either order_id or reservation_id must be provided"
        )
    
    # 결제 Intent 생성
    result = await payment_service.create_payment_intent(
        order_id=payment_data.order_id or 0,
        amount=Decimal(str(payment_data.amount)),
        description=payment_data.description,
        customer_email=payment_data.customer_email,
        metadata={
            "order_id": payment_data.order_id,
            "reservation_id": payment_data.reservation_id
        }
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to create payment intent")
        )
    
    # DB에 결제 저장
    payment_intent = result["payment_intent"]
    
    new_payment = Payment(
        transaction_id=payment_intent["transaction_id"],
        order_id=payment_data.order_id,
        reservation_id=payment_data.reservation_id,
        amount=Decimal(str(payment_intent["amount"])),
        currency=payment_intent["currency"],
        payment_method="google_pay",
        status="pending",
        description=payment_intent["description"],
        customer_email=payment_intent.get("customer_email"),
        google_pay_data=payment_intent["google_pay_data"],
        expires_at=datetime.fromisoformat(payment_intent["expires_at"])
    )
    
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)
    
    logger.info(f"✅ Payment intent created: {payment_intent['transaction_id']}")
    
    return {
        "success": True,
        "transaction_id": payment_intent["transaction_id"],
        "payment_id": new_payment.payment_id,
        "google_pay_config": result["google_pay_config"],
        "expires_at": payment_intent["expires_at"]
    }


@router.post("/payments/{transaction_id}/verify")
async def verify_payment(
    transaction_id: str,
    payment_token: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Google Pay 결제 검증
    
    - 클라이언트에서 Google Pay 토큰 전송
    - 서명 검증 후 결제 완료 처리
    """
    payment_service = get_payment_service()
    
    # 결제 검증
    result = await payment_service.verify_payment(transaction_id, payment_token)
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Payment verification failed")
        )
    
    # DB 업데이트
    stmt = select(Payment).where(Payment.transaction_id == transaction_id)
    db_result = await db.execute(stmt)
    payment = db_result.scalar_one_or_none()
    
    if payment:
        payment.status = "completed"
        payment.completed_at = datetime.now()
        payment.payment_token = str(payment_token)
        await db.commit()
    
    logger.info(f"✅ Payment verified: {transaction_id}")
    
    return {
        "success": True,
        "transaction_id": transaction_id,
        "status": "completed"
    }


@router.get("/payments", response_model=List[PaymentResponse])
async def get_payments(
    status: Optional[str] = Query(None, description="결제 상태"),
    order_id: Optional[int] = Query(None, description="주문 ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """결제 내역 조회"""
    stmt = select(Payment)
    
    if status:
        stmt = stmt.where(Payment.status == status)
    
    if order_id:
        stmt = stmt.where(Payment.order_id == order_id)
    
    stmt = stmt.order_by(Payment.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    payments = result.scalars().all()
    
    return payments


# ============================================
# Google Business Endpoints
# ============================================

@router.post("/google/reviews/collect/{farm_id}")
async def collect_google_reviews(
    farm_id: int,
    location_id: str = Query(..., description="Google Location ID"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    특정 농장의 구글 리뷰 수집
    
    - GMB API에서 리뷰 조회
    - DB에 저장
    """
    google_service = get_google_service()
    
    # 농장 확인
    stmt = select(Farm).where(Farm.farm_id == farm_id)
    result = await db.execute(stmt)
    farm = result.scalar_one_or_none()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm {farm_id} not found"
        )
    
    # 리뷰 수집
    reviews = await google_service.fetch_reviews(location_id, page_size=50)
    
    collected_count = 0
    for review_data in reviews:
        # 중복 확인
        stmt = select(GoogleReview).where(GoogleReview.gmb_review_id == review_data["review_id"])
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            continue
        
        # 새 리뷰 저장
        new_review = GoogleReview(
            gmb_review_id=review_data["review_id"],
            farm_id=farm_id,
            location_id=location_id,
            reviewer_name=review_data.get("reviewer_name"),
            star_rating=review_data.get("star_rating"),
            comment=review_data.get("comment"),
            reply_text=review_data.get("reply"),
            reply_status="replied" if review_data.get("reply") else "pending",
            review_create_time=review_data.get("create_time"),
            review_update_time=review_data.get("update_time")
        )
        
        db.add(new_review)
        collected_count += 1
    
    await db.commit()
    
    logger.info(f"✅ Collected {collected_count} new reviews for farm {farm_id}")
    
    return {
        "farm_id": farm_id,
        "collected_count": collected_count,
        "total_reviews": len(reviews)
    }


@router.post("/google/reviews/{review_id}/auto-reply")
async def auto_reply_to_review(
    review_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    구글 리뷰에 AI 자동 답변
    
    - Qwen AI로 답변 생성
    - GMB API로 답변 게시
    """
    google_service = get_google_service()
    
    # 리뷰 조회
    stmt = select(GoogleReview).where(GoogleReview.review_id == review_id)
    result = await db.execute(stmt)
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review {review_id} not found"
        )
    
    if review.reply_status == "replied":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review already has a reply"
        )
    
    # 농장 정보 조회
    stmt = select(Farm).where(Farm.farm_id == review.farm_id)
    result = await db.execute(stmt)
    farm = result.scalar_one_or_none()
    
    # AI 답변 생성 및 게시
    success = await google_service.auto_reply_to_review(
        location_id=review.location_id,
        review_data={
            "review_id": review.gmb_review_id,
            "comment": review.comment,
            "star_rating": review.star_rating,
            "reviewer_name": review.reviewer_name,
            "reply": review.reply_text
        },
        farm_name=farm.farm_name if farm else "농장"
    )
    
    if success:
        review.reply_status = "replied"
        review.replied_at = datetime.now()
        await db.commit()
        
        logger.info(f"✅ AI reply posted for review {review_id}")
        
        return {
            "success": True,
            "review_id": review_id,
            "reply_status": "replied"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to post AI reply"
        )


@router.get("/google/reviews", response_model=List[GoogleReviewResponse])
async def get_google_reviews(
    farm_id: Optional[int] = Query(None, description="농장 ID"),
    reply_status: Optional[str] = Query(None, description="답변 상태"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="최소 별점"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """구글 리뷰 목록 조회"""
    stmt = select(GoogleReview)
    
    if farm_id:
        stmt = stmt.where(GoogleReview.farm_id == farm_id)
    
    if reply_status:
        stmt = stmt.where(GoogleReview.reply_status == reply_status)
    
    if min_rating:
        stmt = stmt.where(GoogleReview.star_rating >= min_rating)
    
    stmt = stmt.order_by(GoogleReview.collected_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    reviews = result.scalars().all()
    
    return reviews


# ============================================
# Export router
# ============================================

__all__ = ["router"]

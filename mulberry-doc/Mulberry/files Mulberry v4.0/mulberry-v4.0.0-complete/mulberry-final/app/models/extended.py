"""
Mulberry Phase 1+ - Extended Models
예약, 결제, 구글 비즈니스 관련 SQLAlchemy 모델
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    Integer, String, Text, DateTime, Date, Boolean, 
    Numeric, ForeignKey, JSON, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


# ============================================
# 1. 예약 관리
# ============================================

class Reservation(Base):
    """예약 정보"""
    __tablename__ = "reservations"
    
    reservation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reservation_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("elderly_users.user_id", ondelete="CASCADE")
    )
    farm_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("farms.farm_id", ondelete="SET NULL")
    )
    customer_name: Mapped[Optional[str]] = mapped_column(String(100))
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    delivery_address: Mapped[Optional[str]] = mapped_column(Text)
    preferred_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    created_via: Mapped[str] = mapped_column(String(50), default="web")
    dialect_detected: Mapped[Optional[str]] = mapped_column(String(50))
    original_transcription: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    items: Mapped[List["ReservationItem"]] = relationship(
        "ReservationItem",
        back_populates="reservation",
        cascade="all, delete-orphan"
    )
    payment: Mapped[Optional["Payment"]] = relationship(
        "Payment",
        back_populates="reservation",
        uselist=False
    )
    
    def __repr__(self):
        return f"<Reservation(number='{self.reservation_number}', status='{self.status}')>"


class ReservationItem(Base):
    """예약 상품 항목"""
    __tablename__ = "reservation_items"
    
    reservation_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reservation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reservations.reservation_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    subtotal: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    # Relationships
    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="items")
    
    def __repr__(self):
        return f"<ReservationItem(product='{self.product_name}')>"


# ============================================
# 2. 결제 관리
# ============================================

class Payment(Base):
    """결제 트랜잭션"""
    __tablename__ = "payments"
    
    payment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    order_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("orders.order_id", ondelete="SET NULL"),
        index=True
    )
    reservation_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("reservations.reservation_id", ondelete="SET NULL")
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="KRW")
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    customer_email: Mapped[Optional[str]] = mapped_column(String(255))
    payment_token: Mapped[Optional[str]] = mapped_column(Text)
    google_pay_data: Mapped[Optional[dict]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    refunds: Mapped[List["Refund"]] = relationship(
        "Refund",
        back_populates="payment",
        cascade="all, delete-orphan"
    )
    reservation: Mapped[Optional["Reservation"]] = relationship(
        "Reservation",
        back_populates="payment"
    )
    
    def __repr__(self):
        return f"<Payment(tx_id='{self.transaction_id}', status='{self.status}')>"


class Refund(Base):
    """환불 내역"""
    __tablename__ = "refunds"
    
    refund_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    refund_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    payment_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("payments.payment_id", ondelete="SET NULL"),
        index=True
    )
    original_transaction_id: Mapped[Optional[str]] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    payment: Mapped[Optional["Payment"]] = relationship("Payment", back_populates="refunds")
    
    def __repr__(self):
        return f"<Refund(number='{self.refund_number}', status='{self.status}')>"


class AP2Transaction(Base):
    """AP2 (Agent-to-Agent) 결제"""
    __tablename__ = "ap2_transactions"
    
    ap2_tx_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    from_agent_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    from_agent_type: Mapped[Optional[str]] = mapped_column(String(100))
    to_agent_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    to_agent_type: Mapped[Optional[str]] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="KRW")
    purpose: Mapped[Optional[str]] = mapped_column(String(100))
    settlement_type: Mapped[str] = mapped_column(String(50), default="instant")
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    signature: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    settled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    
    def __repr__(self):
        return f"<AP2Transaction(tx_id='{self.transaction_id}', status='{self.status}')>"


class PaymentMethod(Base):
    """저장된 결제 수단"""
    __tablename__ = "payment_methods"
    
    payment_method_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("elderly_users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    token: Mapped[str] = mapped_column(Text, nullable=False)
    last_four_digits: Mapped[Optional[str]] = mapped_column(String(4))
    expiry_month: Mapped[Optional[int]] = mapped_column(Integer)
    expiry_year: Mapped[Optional[int]] = mapped_column(Integer)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    def __repr__(self):
        return f"<PaymentMethod(type='{self.type}', user_id={self.user_id})>"


# ============================================
# 3. 구글 비즈니스 프로필
# ============================================

class GoogleReview(Base):
    """구글 리뷰"""
    __tablename__ = "google_reviews"
    
    review_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gmb_review_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    farm_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("farms.farm_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    location_id: Mapped[str] = mapped_column(String(255), nullable=False)
    reviewer_name: Mapped[Optional[str]] = mapped_column(String(255))
    star_rating: Mapped[Optional[int]] = mapped_column(Integer)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    reply_text: Mapped[Optional[str]] = mapped_column(Text)
    reply_status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    ai_generated_reply: Mapped[Optional[str]] = mapped_column(Text)
    review_create_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    review_update_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reply_update_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    __table_args__ = (
        CheckConstraint('star_rating >= 1 AND star_rating <= 5', name='check_star_rating'),
    )
    
    def __repr__(self):
        return f"<GoogleReview(gmb_id='{self.gmb_review_id}', rating={self.star_rating})>"


class GoogleBusinessMetric(Base):
    """구글 비즈니스 메트릭"""
    __tablename__ = "google_business_metrics"
    
    metric_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("farms.farm_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    location_id: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    views_search: Mapped[int] = mapped_column(Integer, default=0)
    views_maps: Mapped[int] = mapped_column(Integer, default=0)
    actions_website: Mapped[int] = mapped_column(Integer, default=0)
    actions_phone: Mapped[int] = mapped_column(Integer, default=0)
    actions_driving_directions: Mapped[int] = mapped_column(Integer, default=0)
    photos_views_merchant: Mapped[int] = mapped_column(Integer, default=0)
    photos_views_customers: Mapped[int] = mapped_column(Integer, default=0)
    photos_count_merchant: Mapped[int] = mapped_column(Integer, default=0)
    photos_count_customers: Mapped[int] = mapped_column(Integer, default=0)
    local_post_views: Mapped[int] = mapped_column(Integer, default=0)
    local_post_actions: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    __table_args__ = (
        Index('uq_gmb_metrics', farm_id, location_id, metric_date, unique=True),
    )
    
    def __repr__(self):
        return f"<GoogleBusinessMetric(farm_id={self.farm_id}, date={self.metric_date})>"

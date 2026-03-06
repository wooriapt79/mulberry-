"""
Mulberry Phase 1 - SQLAlchemy Models
재고 관리 및 농장 관련 모델
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    Integer, String, Text, DateTime, Date, Boolean, 
    Numeric, ForeignKey, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


# ============================================
# 1. 농장/창업자 관리
# ============================================

class Farm(Base):
    """농장 정보"""
    __tablename__ = "farms"
    
    farm_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mastodon_handle: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    farm_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_name: Mapped[Optional[str]] = mapped_column(String(100))
    region: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    address: Mapped[Optional[str]] = mapped_column(Text)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    inventory_items: Mapped[List["InventoryItem"]] = relationship(
        "InventoryItem", 
        back_populates="farm",
        cascade="all, delete-orphan"
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="farm"
    )
    deal_participations: Mapped[List["DealParticipant"]] = relationship(
        "DealParticipant",
        back_populates="farm"
    )
    agent_logs: Mapped[List["AgentLog"]] = relationship(
        "AgentLog",
        back_populates="farm"
    )
    
    def __repr__(self):
        return f"<Farm(id={self.farm_id}, name='{self.farm_name}', region='{self.region}')>"


# ============================================
# 2. 재고 관리
# ============================================

class InventoryItem(Base):
    """재고 아이템"""
    __tablename__ = "inventory_items"
    
    item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("farms.farm_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    mastodon_post_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    price_per_unit: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    total_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    harvest_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    quality_grade: Mapped[Optional[str]] = mapped_column(String(20))
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    normalized_json: Mapped[Optional[dict]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(
        String(50), 
        default="available",
        index=True
    )
    posted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        index=True
    )
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="inventory_items")
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="inventory_item"
    )
    deal_participations: Mapped[List["DealParticipant"]] = relationship(
        "DealParticipant",
        back_populates="inventory_item"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_inventory_posted_at_desc', posted_at.desc()),
    )
    
    def __repr__(self):
        return f"<InventoryItem(id={self.item_id}, product='{self.product_name}', status='{self.status}')>"


# ============================================
# 3. 공동구매(핫딜) 관리
# ============================================

class HotDeal(Base):
    """공동구매 핫딜"""
    __tablename__ = "hot_deals"
    
    deal_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    target_category: Mapped[Optional[str]] = mapped_column(String(100))
    min_quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    target_quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    current_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0'))
    discount_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(
        String(50),
        default="recruiting",
        index=True
    )
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
    participants: Mapped[List["DealParticipant"]] = relationship(
        "DealParticipant",
        back_populates="deal",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_deals_dates', start_date, end_date),
    )
    
    def __repr__(self):
        return f"<HotDeal(id={self.deal_id}, name='{self.deal_name}', status='{self.status}')>"


class DealParticipant(Base):
    """핫딜 참여 내역"""
    __tablename__ = "deal_participants"
    
    participant_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deal_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hot_deals.deal_id", ondelete="CASCADE"),
        nullable=False
    )
    farm_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("farms.farm_id", ondelete="CASCADE"),
        nullable=False
    )
    item_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("inventory_items.item_id", ondelete="SET NULL")
    )
    committed_quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    # Relationships
    deal: Mapped["HotDeal"] = relationship("HotDeal", back_populates="participants")
    farm: Mapped["Farm"] = relationship("Farm", back_populates="deal_participations")
    inventory_item: Mapped[Optional["InventoryItem"]] = relationship(
        "InventoryItem",
        back_populates="deal_participations"
    )
    
    __table_args__ = (
        UniqueConstraint('deal_id', 'farm_id', name='uq_deal_farm'),
        Index('idx_participants_deal', deal_id),
    )
    
    def __repr__(self):
        return f"<DealParticipant(deal_id={self.deal_id}, farm_id={self.farm_id})>"


# ============================================
# 4. 어르신 사용자 및 주문 관리
# ============================================

class ElderlyUser(Base):
    """어르신 사용자 정보"""
    __tablename__ = "elderly_users"
    
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    name: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    region: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    preferred_dialect: Mapped[Optional[str]] = mapped_column(String(50))
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<ElderlyUser(id={self.user_id}, device='{self.device_id}', region='{self.region}')>"


class Order(Base):
    """주문 내역"""
    __tablename__ = "orders"
    
    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("elderly_users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    farm_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("farms.farm_id", ondelete="SET NULL")
    )
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal('0'))
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        index=True
    )
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    payment_status: Mapped[str] = mapped_column(String(50), default="pending")
    delivery_address: Mapped[Optional[str]] = mapped_column(Text)
    delivery_notes: Mapped[Optional[str]] = mapped_column(Text)
    ordered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    user: Mapped["ElderlyUser"] = relationship("ElderlyUser", back_populates="orders")
    farm: Mapped[Optional["Farm"]] = relationship("Farm", back_populates="orders")
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_orders_date_desc', ordered_at.desc()),
    )
    
    def __repr__(self):
        return f"<Order(id={self.order_id}, number='{self.order_number}', status='{self.status}')>"


class OrderItem(Base):
    """주문 상세 항목"""
    __tablename__ = "order_items"
    
    order_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    item_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("inventory_items.item_id", ondelete="SET NULL")
    )
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    subtotal: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    inventory_item: Mapped[Optional["InventoryItem"]] = relationship(
        "InventoryItem",
        back_populates="order_items"
    )
    
    def __repr__(self):
        return f"<OrderItem(id={self.order_item_id}, product='{self.product_name}')>"


# ============================================
# 5. 정책 리포팅
# ============================================

class RegionalMetric(Base):
    """지역별 경제 지표"""
    __tablename__ = "regional_metrics"
    
    metric_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_sales: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0'))
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    active_farms: Mapped[int] = mapped_column(Integer, default=0)
    active_users: Mapped[int] = mapped_column(Integer, default=0)
    avg_order_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    food_desert_coverage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    __table_args__ = (
        UniqueConstraint('region', 'metric_date', name='uq_region_date'),
        Index('idx_metrics_region_date', region, metric_date.desc()),
    )
    
    def __repr__(self):
        return f"<RegionalMetric(region='{self.region}', date={self.metric_date})>"


class PolicyReport(Base):
    """정책 보고서"""
    __tablename__ = "policy_reports"
    
    report_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    report_type: Mapped[Optional[str]] = mapped_column(String(50))
    report_period_start: Mapped[Optional[date]] = mapped_column(Date)
    report_period_end: Mapped[Optional[date]] = mapped_column(Date)
    report_title: Mapped[Optional[str]] = mapped_column(String(255))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    key_findings: Mapped[Optional[dict]] = mapped_column(JSON)
    recommendations: Mapped[Optional[dict]] = mapped_column(JSON)
    report_data: Mapped[Optional[dict]] = mapped_column(JSON)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    generated_by: Mapped[str] = mapped_column(
        String(100),
        default="AI_Policy_Reporter"
    )
    
    __table_args__ = (
        Index('idx_reports_period', report_period_start, report_period_end),
    )
    
    def __repr__(self):
        return f"<PolicyReport(id={self.report_id}, title='{self.report_title}')>"


# ============================================
# 6. AI 에이전트 로그
# ============================================

class AgentLog(Base):
    """AI 에이전트 활동 로그"""
    __tablename__ = "agent_logs"
    
    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_name: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    farm_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("farms.farm_id", ondelete="SET NULL"),
        index=True
    )
    action_type: Mapped[Optional[str]] = mapped_column(String(100))
    action_details: Mapped[Optional[dict]] = mapped_column(JSON)
    mastodon_post_id: Mapped[Optional[str]] = mapped_column(String(255))
    result: Mapped[Optional[str]] = mapped_column(String(50))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    
    # Relationships
    farm: Mapped[Optional["Farm"]] = relationship("Farm", back_populates="agent_logs")
    
    __table_args__ = (
        Index('idx_logs_executed_desc', executed_at.desc()),
    )
    
    def __repr__(self):
        return f"<AgentLog(id={self.log_id}, agent='{self.agent_name}', action='{self.action_type}')>"


# ============================================
# 7. 시스템 설정
# ============================================

class SystemConfig(Base):
    """시스템 설정"""
    __tablename__ = "system_config"
    
    config_key: Mapped[str] = mapped_column(String(100), primary_key=True)
    config_value: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.config_key}', value='{self.config_value}')>"

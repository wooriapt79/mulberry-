"""
Mulberry Phase 1 - API Routes
재고 관리 및 데이터 파이프라인 API 엔드포인트
"""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from loguru import logger

from app.database import get_async_db
from app.models import Farm, InventoryItem, HotDeal, RegionalMetric
from app.services import get_mastodon_service, get_qwen_service


# ============================================
# Pydantic Schemas (Request/Response Models)
# ============================================

class FarmCreate(BaseModel):
    """농장 생성 요청"""
    mastodon_handle: str = Field(..., example="@greenvalley@mastodon.social")
    farm_name: str = Field(..., example="푸른골농원")
    owner_name: Optional[str] = Field(None, example="박민수")
    region: str = Field(..., example="강원도 인제군")
    address: Optional[str] = None
    contact_phone: Optional[str] = Field(None, example="010-1234-5678")


class FarmResponse(BaseModel):
    """농장 응답"""
    farm_id: int
    mastodon_handle: str
    farm_name: str
    owner_name: Optional[str]
    region: str
    address: Optional[str]
    contact_phone: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class InventoryItemResponse(BaseModel):
    """재고 아이템 응답"""
    item_id: int
    farm_id: int
    product_name: str
    category: Optional[str]
    quantity: Optional[float]
    unit: Optional[str]
    price_per_unit: Optional[float]
    total_price: Optional[float]
    status: str
    posted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ManualInventoryCreate(BaseModel):
    """수동 재고 등록 요청"""
    farm_id: int
    product_name: str
    category: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    price_per_unit: Optional[float] = None
    total_price: Optional[float] = None
    harvest_date: Optional[date] = None
    quality_grade: Optional[str] = None
    description: Optional[str] = None


# ============================================
# Router Initialization
# ============================================

router = APIRouter(prefix="/api/v1", tags=["Mulberry API v1"])


# ============================================
# Farm Management Endpoints
# ============================================

@router.post("/farms", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
async def create_farm(
    farm_data: FarmCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    새로운 농장 등록
    
    - 마스토돈 핸들을 기반으로 농장 정보 등록
    - 중복된 핸들은 허용되지 않음
    """
    # 중복 확인
    stmt = select(Farm).where(Farm.mastodon_handle == farm_data.mastodon_handle)
    result = await db.execute(stmt)
    existing_farm = result.scalar_one_or_none()
    
    if existing_farm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Farm with handle {farm_data.mastodon_handle} already exists"
        )
    
    # 농장 생성
    new_farm = Farm(
        mastodon_handle=farm_data.mastodon_handle,
        farm_name=farm_data.farm_name,
        owner_name=farm_data.owner_name,
        region=farm_data.region,
        address=farm_data.address,
        contact_phone=farm_data.contact_phone
    )
    
    db.add(new_farm)
    await db.commit()
    await db.refresh(new_farm)
    
    logger.info(f"✅ Farm created: {new_farm.farm_name} (@{new_farm.mastodon_handle})")
    
    return new_farm


@router.get("/farms", response_model=List[FarmResponse])
async def get_farms(
    region: Optional[str] = Query(None, description="지역별 필터링"),
    is_active: bool = Query(True, description="활성 농장만 조회"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """
    농장 목록 조회
    
    - 지역별 필터링 가능
    - 활성/비활성 상태 필터링
    """
    stmt = select(Farm).where(Farm.is_active == is_active)
    
    if region:
        stmt = stmt.where(Farm.region.contains(region))
    
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    farms = result.scalars().all()
    
    return farms


@router.get("/farms/{farm_id}", response_model=FarmResponse)
async def get_farm(
    farm_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """특정 농장 상세 조회"""
    stmt = select(Farm).where(Farm.farm_id == farm_id)
    result = await db.execute(stmt)
    farm = result.scalar_one_or_none()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id {farm_id} not found"
        )
    
    return farm


# ============================================
# Inventory Management Endpoints
# ============================================

@router.get("/inventory", response_model=List[InventoryItemResponse])
async def get_inventory(
    farm_id: Optional[int] = Query(None, description="농장 ID"),
    category: Optional[str] = Query(None, description="카테고리"),
    status: str = Query("available", description="재고 상태"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """
    재고 목록 조회
    
    - 농장별, 카테고리별, 상태별 필터링 가능
    - 최신순 정렬
    """
    stmt = select(InventoryItem).where(InventoryItem.status == status)
    
    if farm_id:
        stmt = stmt.where(InventoryItem.farm_id == farm_id)
    
    if category:
        stmt = stmt.where(InventoryItem.category == category)
    
    stmt = stmt.order_by(InventoryItem.posted_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    return items


@router.post("/inventory", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_manual(
    item_data: ManualInventoryCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    재고 수동 등록
    
    - 관리자가 직접 재고 데이터를 입력하는 경우 사용
    - Mastodon 게시물 없이도 등록 가능
    """
    # 농장 존재 확인
    stmt = select(Farm).where(Farm.farm_id == item_data.farm_id)
    result = await db.execute(stmt)
    farm = result.scalar_one_or_none()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id {item_data.farm_id} not found"
        )
    
    # 재고 아이템 생성
    new_item = InventoryItem(
        farm_id=item_data.farm_id,
        product_name=item_data.product_name,
        category=item_data.category,
        quantity=item_data.quantity,
        unit=item_data.unit,
        price_per_unit=item_data.price_per_unit,
        total_price=item_data.total_price,
        harvest_date=item_data.harvest_date,
        quality_grade=item_data.quality_grade,
        raw_text=item_data.description,
        status="available",
        posted_at=datetime.now()
    )
    
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    
    logger.info(f"✅ Inventory item created: {new_item.product_name} (farm_id={new_item.farm_id})")
    
    return new_item


@router.get("/inventory/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """특정 재고 아이템 상세 조회"""
    stmt = select(InventoryItem).where(InventoryItem.item_id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with id {item_id} not found"
        )
    
    return item


@router.patch("/inventory/{item_id}/status")
async def update_inventory_status(
    item_id: int,
    new_status: str = Query(..., regex="^(available|reserved|sold_out)$"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    재고 상태 업데이트
    
    - available: 판매 가능
    - reserved: 예약됨
    - sold_out: 품절
    """
    stmt = select(InventoryItem).where(InventoryItem.item_id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with id {item_id} not found"
        )
    
    item.status = new_status
    await db.commit()
    
    logger.info(f"✅ Inventory status updated: item_id={item_id}, status={new_status}")
    
    return {"item_id": item_id, "status": new_status}


# ============================================
# Data Pipeline Endpoints (Mastodon Integration)
# ============================================

@router.post("/pipeline/collect-posts")
async def collect_recent_posts(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db)
):
    """
    마스토돈에서 최근 게시물 수동 수집
    
    - 스트림 리스너가 아닌 수동 수집 방식
    - 초기 데이터 로드 또는 재수집 시 사용
    """
    mastodon_service = get_mastodon_service()
    qwen_service = get_qwen_service()
    
    # 최근 게시물 조회
    posts = mastodon_service.fetch_recent_posts(limit=limit)
    
    collected_items = []
    
    for post in posts:
        try:
            # 농장 조회 또는 생성
            stmt = select(Farm).where(Farm.mastodon_handle == post['mastodon_handle'])
            result = await db.execute(stmt)
            farm = result.scalar_one_or_none()
            
            if not farm:
                # 새 농장 자동 생성 (기본 정보)
                farm = Farm(
                    mastodon_handle=post['mastodon_handle'],
                    farm_name=post['mastodon_handle'].split('@')[1],  # 임시 이름
                    region="미분류"
                )
                db.add(farm)
                await db.flush()
            
            # Qwen으로 데이터 추출
            extracted = await qwen_service.extract_inventory_data(
                raw_text=post['raw_text'],
                mastodon_handle=post['mastodon_handle'],
                post_metadata={'created_at': post['created_at']}
            )
            
            # 재고 아이템 생성
            new_item = InventoryItem(
                farm_id=farm.farm_id,
                mastodon_post_id=post['post_id'],
                product_name=extracted.get('product_name', '알 수 없음'),
                category=extracted.get('category'),
                quantity=extracted.get('quantity'),
                unit=extracted.get('unit'),
                price_per_unit=extracted.get('price_per_unit'),
                total_price=extracted.get('total_price'),
                harvest_date=extracted.get('harvest_date'),
                quality_grade=extracted.get('quality_grade'),
                raw_text=post['raw_text'],
                normalized_json=extracted,
                status='available',
                posted_at=post['created_at']
            )
            
            db.add(new_item)
            collected_items.append({
                'post_id': post['post_id'],
                'product_name': new_item.product_name,
                'farm': farm.farm_name
            })
            
        except Exception as e:
            logger.error(f"❌ Failed to process post {post['post_id']}: {str(e)}")
            continue
    
    await db.commit()
    
    logger.info(f"✅ Collected {len(collected_items)} inventory items from Mastodon")
    
    return {
        "collected_count": len(collected_items),
        "items": collected_items
    }


# ============================================
# Statistics & Analytics Endpoints
# ============================================

@router.get("/stats/regional")
async def get_regional_stats(
    region: Optional[str] = Query(None, description="특정 지역"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    지역별 통계 조회
    
    - 지역별 농장 수, 재고 수, 총 거래액 등
    """
    stmt = select(
        Farm.region,
        func.count(Farm.farm_id).label('farm_count'),
        func.count(InventoryItem.item_id).label('inventory_count')
    ).outerjoin(
        InventoryItem, Farm.farm_id == InventoryItem.farm_id
    ).group_by(Farm.region)
    
    if region:
        stmt = stmt.where(Farm.region.contains(region))
    
    result = await db.execute(stmt)
    stats = result.all()
    
    return [
        {
            "region": row.region,
            "farm_count": row.farm_count,
            "inventory_count": row.inventory_count
        }
        for row in stats
    ]


# ============================================
# Export router
# ============================================

__all__ = ["router"]

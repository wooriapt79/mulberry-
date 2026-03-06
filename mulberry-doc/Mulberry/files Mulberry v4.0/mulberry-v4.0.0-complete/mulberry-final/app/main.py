"""
Mulberry Phase 1+ - FastAPI Main Application
데이터 파이프라인 엔진 + 예약/결제/구글 비즈니스 통합
"""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.config import settings, get_settings
from app.database import init_db, close_db, health_check
from app.services import (
    get_mastodon_service,
    get_qwen_service,
    get_google_service,
    get_payment_service
)


# ============================================
# Logging Configuration
# ============================================

logger.remove()  # 기본 핸들러 제거

# Console logging
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True
)

# File logging
logger.add(
    settings.log_file_path,
    rotation="500 MB",
    retention="30 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    enqueue=True  # 비동기 로깅
)


# ============================================
# Application Lifespan Events
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작/종료 시 실행되는 이벤트
    """
    # 시작 시
    logger.info("🚀 Mulberry Phase 1 - Starting up...")
    
    # 데이터베이스 초기화
    await init_db()
    logger.info("✅ Database initialized")
    
    # Mastodon 서비스 초기화
    mastodon_service = get_mastodon_service()
    try:
        account = mastodon_service.verify_credentials()
        logger.info(f"✅ Mastodon authenticated: @{account['acct']}")
    except Exception as e:
        logger.warning(f"⚠️ Mastodon authentication failed: {str(e)}")
    
    # Qwen 서비스 초기화
    qwen_service = get_qwen_service()
    logger.info(f"✅ Qwen service ready: {settings.qwen_model}")
    
    # Google Business 서비스 초기화
    google_service = get_google_service()
    logger.info(f"✅ Google Business service ready")
    
    # Payment 서비스 초기화
    payment_service = get_payment_service()
    logger.info(f"✅ Payment service ready (env={settings.google_pay_environment})")
    
    logger.info("🎉 Application startup complete!")
    
    yield  # 애플리케이션 실행
    
    # 종료 시
    logger.info("🛑 Mulberry Phase 1 - Shutting down...")
    
    # 데이터베이스 연결 종료
    await close_db()
    logger.info("✅ Database connections closed")
    
    # 서비스 HTTP 클라이언트 종료
    await qwen_service.close()
    await google_service.close()
    await payment_service.close()
    logger.info("✅ All services closed")
    
    logger.info("👋 Application shutdown complete!")


# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="Mulberry Platform API",
    description="""
    AI-powered food desert solution platform
    
    **Phase 1+: Enhanced Features**
    - 📦 Data Pipeline Engine (Mastodon + Qwen AI)
    - 📞 Voice Reservation System (Edge AI Integration)
    - 💳 Payment Processing (Google Pay + AP2 Protocol)
    - ⭐ Google Business Profile Integration
    - 🤖 AI-powered Review Management
    
    **수석 실장 피드백 반영 완료**
    """,
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ============================================
# Middleware
# ============================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Root & Health Check Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Mulberry Platform",
        "version": "1.1.0",
        "phase": "Phase 1+ - Enhanced with Reservations, Payments & Google Business",
        "status": "running",
        "features": [
            "🎧 Mastodon Real-time Listening",
            "🤖 Qwen AI Data Normalization",
            "📞 Voice Reservation System",
            "💳 Google Pay Integration",
            "🤝 AP2 Agent Payment Protocol",
            "⭐ Google Business Profile Management",
            "🗣️ AI-powered Review Responses"
        ],
        "docs": "/docs",
        "environment": settings.app_env
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    db_health = await health_check()
    
    return {
        "status": "healthy" if db_health["status"] == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": "1.1.0",
        "phase": "Phase 1+ - Data Pipeline + Reservations + Payments + Google Business",
        "components": {
            "database": db_health,
            "mastodon": {
                "status": "configured",
                "instance": settings.mastodon_instance_url
            },
            "qwen": {
                "status": "configured",
                "model": settings.qwen_model
            },
            "google_business": {
                "status": "configured",
                "account_id": settings.google_business_account_id[:10] + "..." if settings.google_business_account_id else "not_set"
            },
            "google_pay": {
                "status": "configured",
                "environment": settings.google_pay_environment,
                "merchant_name": settings.google_pay_merchant_name
            },
            "ap2_protocol": {
                "status": "enabled" if settings.ap2_enabled else "disabled",
                "settlement_interval_hours": settings.ap2_settlement_interval_hours
            }
        }
    }


@app.get("/api/v1/config")
async def get_config(settings_dep: settings = Depends(get_settings)):
    """
    애플리케이션 설정 조회 (민감 정보 제외)
    """
    return {
        "environment": settings_dep.app_env,
        "mastodon": {
            "instance": settings_dep.mastodon_instance_url,
            "hashtags": settings_dep.mastodon_hashtags_list
        },
        "qwen": {
            "model": settings_dep.qwen_model,
            "base_url": settings_dep.qwen_api_base_url
        },
        "business_logic": {
            "hot_deal_min_farms": settings_dep.hot_deal_min_farms,
            "food_desert_radius_km": settings_dep.food_desert_radius_km,
            "delivery_base_fee": settings_dep.delivery_base_fee
        }
    }


# ============================================
# API Routes
# ============================================

from app.api import core_router, extended_router

app.include_router(core_router)
app.include_router(extended_router)


# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 핸들러"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.app_debug else "An error occurred",
            "path": str(request.url)
        }
    )


# ============================================
# Development Only
# ============================================

if settings.app_env == "development":
    @app.get("/api/v1/dev/mastodon-test")
    async def test_mastodon():
        """Mastodon 연결 테스트 (개발용)"""
        try:
            mastodon_service = get_mastodon_service()
            account = mastodon_service.verify_credentials()
            recent_posts = mastodon_service.fetch_recent_posts(limit=3)
            
            return {
                "status": "success",
                "account": account,
                "recent_posts_count": len(recent_posts),
                "sample_post": recent_posts[0] if recent_posts else None
            }
        except Exception as e:
            logger.error(f"Mastodon test failed: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": str(e)}
            )
    
    @app.get("/api/v1/dev/qwen-test")
    async def test_qwen():
        """Qwen AI 연결 테스트 (개발용)"""
        test_text = """
        🍎 신선한 사과 판매합니다!
        품목: 홍로 사과
        수량: 500kg (20kg 박스 25개)
        가격: 박스당 35,000원
        등급: 특품
        """
        
        try:
            qwen_service = get_qwen_service()
            result = await qwen_service.extract_inventory_data(
                raw_text=test_text,
                mastodon_handle="@test@mastodon.social"
            )
            
            return {
                "status": "success",
                "input": test_text,
                "extracted_data": result
            }
        except Exception as e:
            logger.error(f"Qwen test failed: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": str(e)}
            )


# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Mulberry server on {settings.app_host}:{settings.app_port}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )

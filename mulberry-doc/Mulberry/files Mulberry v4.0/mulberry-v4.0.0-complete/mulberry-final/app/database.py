"""
Mulberry Phase 1 - Database Connection & Session Management
SQLAlchemy 2.0 스타일 사용
"""

from typing import AsyncGenerator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.pool import NullPool, QueuePool

from app.config import settings
from loguru import logger


# ============================================
# Base Model
# ============================================

class Base(DeclarativeBase):
    """SQLAlchemy Base Model"""
    pass


# ============================================
# Sync Engine (for Alembic migrations)
# ============================================

sync_engine = create_engine(
    settings.database_url,
    echo=settings.app_debug,
    pool_pre_ping=True,  # 연결 상태 확인
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,  # 1시간마다 connection recycle
)

# Sync Session Factory
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)


# ============================================
# Async Engine (for FastAPI)
# ============================================

async_engine = create_async_engine(
    settings.async_database_url,
    echo=settings.app_debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ============================================
# Event Listeners
# ============================================

@event.listens_for(sync_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """PostgreSQL 연결 시 설정"""
    # PostgreSQL specific settings can be added here
    pass


# ============================================
# Dependency Injection for FastAPI
# ============================================

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Dependency: Async Database Session
    
    Usage:
        @app.get("/items")
        async def read_items(db: AsyncSession = Depends(get_async_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()


def get_sync_db() -> Session:
    """
    Sync Database Session (for background tasks, scripts)
    
    Usage:
        with get_sync_db() as db:
            db.query(...)
    """
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()


# ============================================
# Database Utilities
# ============================================

async def init_db():
    """
    데이터베이스 초기화
    - 테이블 생성 (개발 환경용)
    - 프로덕션에서는 Alembic migration 사용 권장
    """
    async with async_engine.begin() as conn:
        # 개발 환경에서만 테이블 자동 생성
        if settings.app_env == "development":
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created (development mode)")
        else:
            logger.info("Database initialized (use Alembic for migrations)")


async def close_db():
    """데이터베이스 연결 종료"""
    await async_engine.dispose()
    logger.info("Database connections closed")


def check_db_connection() -> bool:
    """
    데이터베이스 연결 상태 확인
    
    Returns:
        bool: 연결 성공 여부
    """
    try:
        with sync_engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


# ============================================
# Context Manager for Sync Session
# ============================================

class DatabaseSession:
    """
    Context manager for sync database sessions
    
    Usage:
        with DatabaseSession() as db:
            user = db.query(User).first()
    """
    
    def __enter__(self) -> Session:
        self.db = SyncSessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
            logger.error(f"Database transaction rolled back: {exc_val}")
        else:
            self.db.commit()
        self.db.close()


# ============================================
# Health Check
# ============================================

async def health_check() -> dict:
    """
    데이터베이스 헬스체크
    
    Returns:
        dict: 상태 정보
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "pool_size": async_engine.pool.size(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


if __name__ == "__main__":
    # Test database connection
    import asyncio
    
    async def test():
        logger.info("Testing database connection...")
        await init_db()
        health = await health_check()
        logger.info(f"Health check result: {health}")
    
    asyncio.run(test())

"""
Mulberry Agent System - Main Application
CTO Koda

Windows/Linux 환경에서 실행 가능한 메인 서버
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 모듈 임포트
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from agent_factory.agent_factory import AgentFactory, StoreType, AgentStatus
from terminal_matching.terminal_matching import TerminalMatchingManager, StoreInfo
from jangseungbaegi_library.library import JangseungbaegiLibrary, DocumentType, MeetingType
from business_operations.operations import BusinessOperationsManager
from group_purchase.group_purchase_manager import GroupPurchaseManager, GroupPurchaseProduct, ProductCategory
from group_purchase.database_schema import init_group_purchase_tables


# ============================================
# 설정 로드
# ============================================

def load_config():
    """설정 파일 로드"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
    
    # config.json이 없으면 example 복사
    if not os.path.exists(config_path):
        example_path = config_path.replace('.json', '.example.json')
        if os.path.exists(example_path):
            import shutil
            shutil.copy(example_path, config_path)
            print("⚠️ config.json이 없어서 example에서 복사했습니다. 설정을 수정하세요.")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


CONFIG = load_config()


# ============================================
# 데이터베이스 연결
# ============================================

def get_db_connection():
    """데이터베이스 연결"""
    db_type = CONFIG['database']['type']
    
    if db_type == 'sqlite':
        db_path = CONFIG['database']['path']
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    elif db_type == 'postgresql':
        import psycopg2
        pg_config = CONFIG['database']['postgresql']
        conn = psycopg2.connect(
            host=pg_config['host'],
            port=pg_config['port'],
            database=pg_config['database'],
            user=pg_config['user'],
            password=pg_config['password']
        )
        return conn
    else:
        raise ValueError(f"지원하지 않는 데이터베이스 타입: {db_type}")


# ============================================
# FastAPI 앱 초기화
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행"""
    # 시작 시
    print("🌾 Mulberry Agent System 시작")
    print(f"📡 서버: http://{CONFIG['server']['host']}:{CONFIG['server']['port']}")
    print(f"📚 API 문서: http://localhost:{CONFIG['server']['port']}/docs")
    
    # 데이터베이스 초기화
    init_database()
    
    yield
    
    # 종료 시
    print("👋 Mulberry Agent System 종료")


app = FastAPI(
    title="Mulberry Agent System",
    description="AI 에이전트 관리 시스템",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================
# 데이터베이스 초기화
# ============================================

def init_database():
    """데이터베이스 스키마 생성"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # agents 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            store_type TEXT NOT NULL,
            raspberry_pi_id TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            training_started_at TIMESTAMP,
            training_completed_at TIMESTAMP,
            deployed_at TIMESTAMP,
            constitution_study_progress REAL DEFAULT 0,
            persona_training_progress REAL DEFAULT 0,
            business_persona TEXT,
            passport_id TEXT,
            total_customers_served INTEGER DEFAULT 0,
            total_sales REAL DEFAULT 0,
            customer_satisfaction REAL DEFAULT 0
        )
    """)
    
    # terminals 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS terminals (
            terminal_id TEXT PRIMARY KEY,
            serial_number TEXT UNIQUE NOT NULL,
            model TEXT NOT NULL,
            status TEXT NOT NULL,
            registered_at TIMESTAMP NOT NULL,
            agent_id TEXT,
            assigned_at TIMESTAMP,
            store_info TEXT,
            ip_address TEXT,
            mac_address TEXT,
            firmware_version TEXT,
            has_display BOOLEAN DEFAULT 0,
            has_scanner BOOLEAN DEFAULT 0,
            has_printer BOOLEAN DEFAULT 0,
            has_card_reader BOOLEAN DEFAULT 0,
            total_uptime_hours REAL DEFAULT 0,
            last_heartbeat TIMESTAMP
        )
    """)
    
    # documents 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            doc_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            doc_type TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            version INTEGER DEFAULT 1,
            tags TEXT,
            category TEXT,
            is_public BOOLEAN DEFAULT 1,
            view_count INTEGER DEFAULT 0,
            download_count INTEGER DEFAULT 0
        )
    """)
    
    # meetings 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            meeting_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            meeting_type TEXT NOT NULL,
            scheduled_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP NOT NULL,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            invited_agents TEXT,
            attended_agents TEXT,
            agenda TEXT,
            notes TEXT,
            decisions TEXT,
            action_items TEXT,
            is_active BOOLEAN DEFAULT 0,
            is_completed BOOLEAN DEFAULT 0
        )
    """)
    
    # interactions 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            interaction_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            channel TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            customer_name TEXT,
            customer_phone TEXT,
            customer_id TEXT,
            content TEXT NOT NULL,
            agent_response TEXT,
            sentiment TEXT,
            keywords TEXT,
            is_resolved BOOLEAN DEFAULT 0,
            resolved_at TIMESTAMP,
            customer_rating INTEGER
        )
    """)
    
    conn.commit()
    
    # 공동구매 테이블 초기화
    init_group_purchase_tables(conn)
    
    conn.close()
    
    print("✅ 데이터베이스 초기화 완료")


# ============================================
# Pydantic 모델
# ============================================

class AgentCreateRequest(BaseModel):
    name: str
    store_type: str
    raspberry_pi_id: Optional[str] = None


class TerminalRegisterRequest(BaseModel):
    serial_number: str
    store_name: str
    store_type: str
    address: str
    phone: str
    business_hours: Dict
    google_business_id: Optional[str] = None


class MeetingScheduleRequest(BaseModel):
    title: str
    meeting_type: str
    scheduled_at: str  # ISO format
    invited_agents: List[str]
    agenda: Optional[List[str]] = None


# ============================================
# API 엔드포인트
# ============================================

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "🌾 Mulberry Agent System",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================
# 에이전트 API
# ============================================

@app.post("/api/agents/create")
async def create_agent(request: AgentCreateRequest):
    """에이전트 생성"""
    try:
        conn = get_db_connection()
        factory = AgentFactory(conn, CONFIG['agent_factory'])
        
        agent = factory.create_agent(
            name=request.name,
            store_type=StoreType(request.store_type),
            raspberry_pi_id=request.raspberry_pi_id
        )
        
        conn.close()
        
        return agent.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """에이전트 조회"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="에이전트를 찾을 수 없습니다")
    
    return dict(row)


@app.get("/api/agents")
async def list_agents():
    """에이전트 목록"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM agents ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


@app.post("/api/agents/{agent_id}/deploy")
async def deploy_agent(agent_id: str, raspberry_pi_id: str):
    """에이전트 배치"""
    try:
        conn = get_db_connection()
        factory = AgentFactory(conn, CONFIG['agent_factory'])
        
        agent = factory.deploy_agent(agent_id, raspberry_pi_id)
        conn.close()
        
        return agent.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/agents/stats/daily")
async def daily_agent_stats():
    """일일 통계"""
    conn = get_db_connection()
    factory = AgentFactory(conn, CONFIG['agent_factory'])
    
    stats = factory.get_daily_stats()
    conn.close()
    
    return stats


# ============================================
# 단말기 API
# ============================================

@app.post("/api/terminals/register")
async def register_terminal(request: TerminalRegisterRequest):
    """단말기 등록"""
    try:
        conn = get_db_connection()
        manager = TerminalMatchingManager(conn)
        
        store_info = StoreInfo(
            store_name=request.store_name,
            store_type=request.store_type,
            address=request.address,
            phone=request.phone,
            business_hours=request.business_hours,
            google_business_id=request.google_business_id
        )
        
        terminal = manager.register_terminal(
            serial_number=request.serial_number,
            store_info=store_info
        )
        
        conn.close()
        
        return terminal.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/terminals")
async def list_terminals():
    """단말기 목록"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM terminals ORDER BY registered_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


@app.get("/api/terminals/stats")
async def terminal_stats():
    """단말기 통계"""
    conn = get_db_connection()
    manager = TerminalMatchingManager(conn)
    
    stats = manager.get_matching_stats()
    conn.close()
    
    return stats


# ============================================
# 도서관 API
# ============================================

@app.get("/api/library/constitution")
async def get_constitution():
    """장승배기 헌법"""
    conn = get_db_connection()
    library = JangseungbaegiLibrary(conn)
    
    constitution = library.get_constitution()
    conn.close()
    
    return constitution.to_dict()


@app.post("/api/library/meetings/schedule")
async def schedule_meeting(request: MeetingScheduleRequest):
    """회의 일정"""
    try:
        conn = get_db_connection()
        library = JangseungbaegiLibrary(conn)
        
        meeting = library.schedule_meeting(
            title=request.title,
            meeting_type=MeetingType(request.meeting_type),
            scheduled_at=datetime.fromisoformat(request.scheduled_at),
            invited_agents=request.invited_agents,
            agenda=request.agenda
        )
        
        conn.close()
        
        return meeting.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/library/stats")
async def library_stats():
    """도서관 통계"""
    conn = get_db_connection()
    library = JangseungbaegiLibrary(conn)
    
    stats = library.get_library_stats()
    conn.close()
    
    return stats


# ============================================
# 대시보드 API
# ============================================

@app.get("/api/dashboard")
async def dashboard():
    """전체 대시보드"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 에이전트 통계
    cursor.execute("SELECT COUNT(*) FROM agents")
    total_agents = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'active'")
    active_agents = cursor.fetchone()[0]
    
    # 단말기 통계
    cursor.execute("SELECT COUNT(*) FROM terminals")
    total_terminals = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM terminals WHERE status = 'active'")
    active_terminals = cursor.fetchone()[0]
    
    # 오늘의 상호작용
    cursor.execute("""
        SELECT COUNT(*) FROM interactions 
        WHERE DATE(created_at) = DATE('now')
    """)
    today_interactions = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "agents": {
            "total": total_agents,
            "active": active_agents
        },
        "terminals": {
            "total": total_terminals,
            "active": active_terminals
        },
        "interactions": {
            "today": today_interactions
        },
        "timestamp": datetime.now().isoformat()
    }


# ============================================
# 공동구매 API
# ============================================

@app.post("/api/group-purchase/products")
async def create_group_purchase_product(request: dict):
    """공동구매 상품 등록"""
    try:
        conn = get_db_connection()
        manager = GroupPurchaseManager(conn)
        
        product = manager.create_product(
            name=request['name'],
            description=request['description'],
            category=ProductCategory(request['category']),
            producer_agent_id=request['producer_agent_id'],
            producer_location=request['producer_location'],
            original_price=request['original_price'],
            group_price=request['group_price'],
            min_quantity=request.get('min_quantity', 10)
        )
        
        conn.close()
        
        return product.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/group-purchase/campaigns")
async def create_campaign(request: dict):
    """공동구매 캠페인 시작"""
    try:
        conn = get_db_connection()
        manager = GroupPurchaseManager(conn)
        
        campaign = manager.create_campaign(
            product_id=request['product_id'],
            duration_days=request.get('duration_days', 7)
        )
        
        conn.close()
        
        return campaign.get_progress()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/group-purchase/join")
async def join_campaign(request: dict):
    """공동구매 참여"""
    try:
        conn = get_db_connection()
        manager = GroupPurchaseManager(conn)
        
        result = manager.join_campaign(
            campaign_id=request['campaign_id'],
            user_id=request['user_id'],
            quantity=request.get('quantity', 1)
        )
        
        conn.close()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/group-purchase/hot-deals")
async def get_hot_deals():
    """오늘의 핫딜"""
    conn = get_db_connection()
    manager = GroupPurchaseManager(conn)
    
    hot_deals = manager.get_hot_deals(10)
    conn.close()
    
    return {"hot_deals": hot_deals}


@app.get("/api/group-purchase/village/{village_id}")
async def get_village_purchases(village_id: str):
    """우리 마을 공동구매"""
    conn = get_db_connection()
    manager = GroupPurchaseManager(conn)
    
    purchases = manager.get_village_purchases(village_id)
    conn.close()
    
    return {"purchases": purchases}


# ============================================
# 메인 실행
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=CONFIG['server']['host'],
        port=CONFIG['server']['port'],
        reload=CONFIG['server']['debug'],
        log_level="info"
    )

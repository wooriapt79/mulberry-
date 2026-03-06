"""
Mulberry Phase 3-C - Senior Story Web API
장년층용 AI 글쓰기 마법사 백엔드
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os

from app.agents import get_message_bus, get_sns_manager

# FastAPI 앱
app = FastAPI(
    title="Mulberry Senior Story API",
    description="장년층 친화형 AI 글쓰기 마법사",
    version="3.2.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 메시지 버스 및 SNS Manager
bus = get_message_bus()
sns_manager = get_sns_manager(bus)


# ============================================
# Request/Response Models
# ============================================

class StoryGenerationRequest(BaseModel):
    """스토리 생성 요청"""
    user_input: str
    farm_name: Optional[str] = None
    farmer_name: Optional[str] = None
    photo_metadata: Optional[Dict[str, Any]] = None


class StoryPostingRequest(BaseModel):
    """스토리 포스팅 요청"""
    user_input: str
    selected_version: int = 0
    farm_name: Optional[str] = None
    farmer_name: Optional[str] = None
    photo_metadata: Optional[Dict[str, Any]] = None


# ============================================
# Web UI
# ============================================

@app.get("/")
async def root():
    """모바일 웹 에디터 페이지"""
    return FileResponse("/mnt/user-data/outputs/mulberry-phase1/web/senior_editor.html")


# ============================================
# API Endpoints
# ============================================

@app.post("/api/senior-story/generate")
async def generate_senior_story(request: StoryGenerationRequest):
    """
    시니어 스토리 생성
    
    단문/키워드를 AI로 3가지 버전의 감성적인 글로 변환
    """
    try:
        result = await sns_manager.generate_senior_story(
            user_input=request.user_input,
            farm_name=request.farm_name,
            farmer_name=request.farmer_name,
            photo_metadata=request.photo_metadata
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/senior-story/post")
async def post_senior_story(request: StoryPostingRequest):
    """
    시니어 스토리 생성 및 즉시 포스팅
    
    선택한 버전을 마스토돈에 게시
    """
    try:
        result = await sns_manager.post_senior_story(
            user_input=request.user_input,
            farm_name=request.farm_name,
            farmer_name=request.farmer_name,
            photo_metadata=request.photo_metadata,
            selected_version=request.selected_version
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "version": "3.2.0",
        "service": "Senior Story API"
    }


# ============================================
# 실행
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

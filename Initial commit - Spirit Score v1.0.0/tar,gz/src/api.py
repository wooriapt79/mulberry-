"""
Spirit Score API - FastAPI Endpoints
CTO Koda

RESTful API for Spirit Score management
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import psycopg2
import os

# Spirit Score 모듈 임포트
from spirit_score_engine import SpiritScoreEngine
from activity_tracker import ActivityTracker

# ============================================
# FastAPI 앱 초기화
# ============================================

app = FastAPI(
    title="Mulberry Spirit Score API",
    description="장승배기 정신 자동화 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Database 연결
# ============================================

def get_db_connection():
    """PostgreSQL 연결"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "mulberry"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "")
    )

# 글로벌 인스턴스
db_conn = None
spirit_engine = None
activity_tracker = None

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 초기화"""
    global db_conn, spirit_engine, activity_tracker
    
    db_conn = get_db_connection()
    spirit_engine = SpiritScoreEngine(db_conn)
    activity_tracker = ActivityTracker(spirit_engine)
    
    print("✅ Spirit Score API 시작됨")

@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 정리"""
    global db_conn
    
    if db_conn:
        db_conn.close()
    
    print("👋 Spirit Score API 종료됨")

# ============================================
# Pydantic Models (Request/Response)
# ============================================

class ActivityRequest(BaseModel):
    user_id: str = Field(..., description="사용자 ID")
    activity_type: str = Field(..., description="활동 유형")
    activity_data: Optional[dict] = Field(None, description="활동 상세 정보")

class MentionRequest(BaseModel):
    mentioned_user_id: str
    mention_id: str
    mentioned_by: str
    channel: str

class MentionResponseRequest(BaseModel):
    user_id: str
    mention_id: str

class CommitRequest(BaseModel):
    user_id: str
    commit_sha: str
    repo: str
    approved: bool = True

class PRReviewRequest(BaseModel):
    reviewer_id: str
    pr_number: int
    repo: str
    review_state: str

class MeetingAttendanceRequest(BaseModel):
    meeting_id: str
    meeting_name: str
    attendees: List[str]
    all_members: List[str]

class MutualAidRequest(BaseModel):
    user_id: str
    amount: float

class ApproveActivityRequest(BaseModel):
    activity_id: str
    approved_by: str

class UserScoreResponse(BaseModel):
    username: str
    display_name: str
    spirit_score: float
    total_activities: int
    positive_activities: int
    negative_activities: int

class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    display_name: str
    role: str
    spirit_score: float

# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    """API 정보"""
    return {
        "name": "Mulberry Spirit Score API",
        "version": "1.0.0",
        "status": "running"
    }

# ──────────────────────────────────────────
# User Score APIs
# ──────────────────────────────────────────

@app.get("/api/users/{user_id}/score", response_model=UserScoreResponse)
async def get_user_score(user_id: str):
    """
    사용자 Spirit Score 조회
    """
    try:
        score_data = spirit_engine.get_user_score(user_id)
        return score_data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 10):
    """
    Spirit Score 리더보드 조회
    """
    try:
        leaderboard = spirit_engine.get_leaderboard(limit)
        return leaderboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ──────────────────────────────────────────
# Activity Recording APIs
# ──────────────────────────────────────────

@app.post("/api/activities/record")
async def record_activity(request: ActivityRequest):
    """
    활동 기록
    """
    try:
        result = spirit_engine.record_activity(
            user_id=request.user_id,
            activity_type=request.activity_type,
            activity_data=request.activity_data
        )
        return {
            "success": True,
            "activity": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/activities/approve")
async def approve_activity(request: ApproveActivityRequest):
    """
    활동 수동 승인
    """
    try:
        result = spirit_engine.approve_manual_activity(
            activity_id=request.activity_id,
            approved_by=request.approved_by
        )
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ──────────────────────────────────────────
# Tracking APIs
# ──────────────────────────────────────────

@app.post("/api/track/login")
async def track_login(user_id: str):
    """
    로그인 추적
    """
    try:
        result = activity_tracker.track_login(user_id)
        if result:
            return {"success": True, "activity": result}
        else:
            return {"success": True, "message": "Already logged in today"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/track/mention")
async def track_mention(request: MentionRequest):
    """
    @호출 기록
    """
    try:
        activity_tracker.track_mention(
            mentioned_user_id=request.mentioned_user_id,
            mention_id=request.mention_id,
            mentioned_by=request.mentioned_by,
            channel=request.channel
        )
        return {"success": True, "message": "Mention tracked"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/track/mention/response")
async def track_mention_response(request: MentionResponseRequest):
    """
    @호출 응답 추적
    """
    try:
        result = activity_tracker.track_mention_response(
            user_id=request.user_id,
            mention_id=request.mention_id
        )
        if result:
            return {"success": True, "activity": result}
        else:
            return {"success": False, "message": "Mention not found or already responded"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/track/commit")
async def track_commit(request: CommitRequest):
    """
    GitHub 커밋 추적
    """
    try:
        result = activity_tracker.track_github_commit(
            user_id=request.user_id,
            commit_sha=request.commit_sha,
            repo=request.repo,
            approved=request.approved
        )
        if result:
            return {"success": True, "activity": result}
        else:
            return {"success": True, "message": "Duplicate or not approved"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/track/pr-review")
async def track_pr_review(request: PRReviewRequest):
    """
    PR 리뷰 추적
    """
    try:
        result = activity_tracker.track_pr_review(
            reviewer_id=request.reviewer_id,
            pr_number=request.pr_number,
            repo=request.repo,
            review_state=request.review_state
        )
        if result:
            return {"success": True, "activity": result}
        else:
            return {"success": True, "message": "Duplicate or invalid state"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/track/meeting")
async def track_meeting(request: MeetingAttendanceRequest):
    """
    회의 참석 추적
    """
    try:
        activity_tracker.track_meeting_attendance(
            meeting_id=request.meeting_id,
            meeting_name=request.meeting_name,
            attendees=request.attendees,
            all_members=request.all_members
        )
        return {"success": True, "message": "Meeting attendance recorded"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ──────────────────────────────────────────
# Mutual Aid APIs
# ──────────────────────────────────────────

@app.post("/api/mutual-aid/contribute")
async def contribute_mutual_aid(request: MutualAidRequest):
    """
    상부상조 기여
    """
    try:
        result = spirit_engine.record_mutual_aid(
            user_id=request.user_id,
            amount=Decimal(str(request.amount))
        )
        return {
            "success": True,
            "contribution": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/mutual-aid/auto-contribute")
async def auto_contribute_from_revenue(
    user_id: str,
    revenue: float
):
    """
    수익의 10% 자동 기여
    """
    try:
        result = activity_tracker.track_revenue_contribution(
            user_id=user_id,
            revenue=revenue
        )
        return {
            "success": True,
            "contribution": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ──────────────────────────────────────────
# Webhook Endpoints
# ──────────────────────────────────────────

@app.post("/webhooks/github")
async def github_webhook(
    payload: dict,
    x_github_event: str = Header(None)
):
    """
    GitHub Webhook 수신
    """
    try:
        if x_github_event == "push":
            # Push 이벤트 처리
            # (GitHubWebhookHandler 사용)
            return {"success": True, "event": "push"}
        
        elif x_github_event == "pull_request_review":
            # PR 리뷰 이벤트 처리
            return {"success": True, "event": "pull_request_review"}
        
        else:
            return {"success": True, "event": x_github_event, "message": "Not processed"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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

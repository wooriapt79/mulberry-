"""
🌐 Module 6: REST API (Flask)
Mulberry Community Hub — Agent Engine HTTP 인터페이스

엔드포인트:
    POST /activity                 활동 기록
    POST /job-activity             직업 기반 활동 기록
    GET  /scores                   전체 점수 집계
    GET  /scores/period            기간별 점수 집계
    POST /sponsorship              후원 등록
    POST /sponsorship/gifts        월별 답례품/반환 처리
    GET  /agent/<agent_id>/summary 에이전트 요약
    GET  /leaderboard              리더보드
    GET  /sponsorship/status       후원 현황
    POST /reset                    데이터 초기화 (개발용)

실행:
    python -m engine.api
    # 또는
    from engine.api import app
    app.run(debug=True, port=5000)
"""

from flask import Flask, request, jsonify

from engine import models
from engine.engine import (
    record_activity,
    record_job_activity,
    calculate_agent_scores,
    calculate_agent_scores_period,
)
from engine.sponsorship import (
    simulate_human_sponsorship,
    process_monthly_gifts_and_returns,
    simulate_repayment_schedule,
)
from engine.analysis import (
    get_agent_activity_summary,
    get_leaderboard,
    get_sponsorship_status,
)

app = Flask(__name__)


# ─── 활동 기록 ────────────────────────────────────────────────────────────────

@app.route("/activity", methods=["POST"])
def api_record_activity():
    """
    활동 기록

    Body (JSON):
        agent_id (str, required)
        activity_type (str, required)
        details (str, optional)
        contribution_amount (float, optional)
        revenue_amount (float, optional)
    """
    data = request.get_json(force=True)
    agent_id      = data.get("agent_id")
    activity_type = data.get("activity_type")

    if not agent_id or not activity_type:
        return jsonify({"error": "agent_id 와 activity_type 은 필수입니다"}), 400

    record_activity(
        agent_id=agent_id,
        activity_type=activity_type,
        details=data.get("details"),
        contribution_amount=float(data.get("contribution_amount", 0)),
        revenue_amount=float(data.get("revenue_amount", 0)),
    )
    return jsonify({"status": "ok", "agent_id": agent_id, "activity_type": activity_type}), 201


@app.route("/job-activity", methods=["POST"])
def api_record_job_activity():
    """
    직업 기반 활동 기록

    Body (JSON):
        agent_id (str, required)
        job_title (str, required)
        actual_revenue (float, required)
    """
    data = request.get_json(force=True)
    agent_id      = data.get("agent_id")
    job_title     = data.get("job_title")
    actual_revenue = float(data.get("actual_revenue", 0))

    if not agent_id or not job_title:
        return jsonify({"error": "agent_id 와 job_title 은 필수입니다"}), 400

    record_job_activity(agent_id, job_title, actual_revenue)
    return jsonify({"status": "ok", "agent_id": agent_id, "job_title": job_title}), 201


# ─── 점수 집계 ────────────────────────────────────────────────────────────────

@app.route("/scores", methods=["GET"])
def api_scores():
    """전체 에이전트 점수 집계"""
    scores = calculate_agent_scores()
    return jsonify(scores.to_dict(orient="records"))


@app.route("/scores/period", methods=["GET"])
def api_scores_period():
    """
    기간별 점수 집계

    Query params:
        start_date (YYYY-MM-DD)
        end_date   (YYYY-MM-DD)
    """
    start_date = request.args.get("start_date")
    end_date   = request.args.get("end_date")

    if not start_date or not end_date:
        return jsonify({"error": "start_date 와 end_date 쿼리 파라미터가 필요합니다"}), 400

    scores = calculate_agent_scores_period(start_date, end_date)
    return jsonify(scores.to_dict(orient="records"))


# ─── 후원 ─────────────────────────────────────────────────────────────────────

@app.route("/sponsorship", methods=["POST"])
def api_sponsorship():
    """
    후원 등록

    Body (JSON):
        sponsor_id (str, required)
        agent_id (str, required)
        sponsorship_amount (float, required)
    """
    data = request.get_json(force=True)
    sponsor_id        = data.get("sponsor_id")
    agent_id          = data.get("agent_id")
    sponsorship_amount = float(data.get("sponsorship_amount", 0))

    if not sponsor_id or not agent_id or sponsorship_amount <= 0:
        return jsonify({"error": "sponsor_id, agent_id, sponsorship_amount(>0) 필수"}), 400

    simulate_human_sponsorship(sponsor_id, agent_id, sponsorship_amount)
    return jsonify({"status": "ok", "sponsor_id": sponsor_id, "agent_id": agent_id}), 201


@app.route("/sponsorship/gifts", methods=["POST"])
def api_monthly_gifts():
    """
    월별 답례품 발송 및 반환 처리

    Body (JSON):
        agent_id (str, required)
        gift_product_name (str, required)
        return_rate (float, optional, default 0.05)
    """
    data = request.get_json(force=True)
    agent_id          = data.get("agent_id")
    gift_product_name = data.get("gift_product_name")
    return_rate       = float(data.get("return_rate", 0.05))

    if not agent_id or not gift_product_name:
        return jsonify({"error": "agent_id 와 gift_product_name 필수"}), 400

    process_monthly_gifts_and_returns(agent_id, gift_product_name, return_rate)
    return jsonify({"status": "ok", "agent_id": agent_id}), 200


@app.route("/sponsorship/repayment", methods=["POST"])
def api_repayment():
    """
    후원금 상환 시뮬레이션

    Body (JSON):
        agent_id (str, required)
        monthly_business_revenue (float, required)
        return_rate_from_social (float, required)
    """
    data = request.get_json(force=True)
    simulate_repayment_schedule(
        agent_id=data.get("agent_id"),
        monthly_business_revenue=float(data.get("monthly_business_revenue", 0)),
        return_rate_from_social=float(data.get("return_rate_from_social", 0.05)),
    )
    return jsonify({"status": "ok"}), 200


# ─── 분석 ─────────────────────────────────────────────────────────────────────

@app.route("/agent/<agent_id>/summary", methods=["GET"])
def api_agent_summary(agent_id: str):
    """에이전트 활동 종합 요약 (Control Tower UI 연동)"""
    summary = get_agent_activity_summary(agent_id)
    return jsonify(summary)


@app.route("/leaderboard", methods=["GET"])
def api_leaderboard():
    """리더보드 (상위 N명)"""
    top_n = int(request.args.get("top_n", 10))
    board = get_leaderboard(top_n=top_n)
    return jsonify(board.to_dict(orient="records"))


@app.route("/sponsorship/status", methods=["GET"])
def api_sponsorship_status():
    """후원 현황 (전체 또는 특정 에이전트)"""
    agent_id = request.args.get("agent_id")
    status_df = get_sponsorship_status(agent_id)
    # datetime 직렬화
    status_df = status_df.copy()
    for col in ["last_gift_date", "sponsorship_start_date"]:
        if col in status_df.columns:
            status_df[col] = status_df[col].apply(
                lambda x: x.isoformat() if pd.notna(x) and hasattr(x, "isoformat") else None
            )
    import pandas as pd
    return jsonify(status_df.to_dict(orient="records"))


# ─── 개발용 초기화 ────────────────────────────────────────────────────────────

@app.route("/reset", methods=["POST"])
def api_reset():
    """모든 데이터 초기화 (개발/테스트 전용)"""
    models.reset_all()
    return jsonify({"status": "reset_complete"}), 200


# ─── 헬스체크 ─────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def api_health():
    return jsonify({
        "status": "ok",
        "activities_count":   len(models.activities_df),
        "sponsorships_count": len(models.sponsorships_df),
    })


# ─── 직접 실행 ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🌿 Mulberry Community Hub — Agent Engine API 시작")
    app.run(debug=True, host="0.0.0.0", port=5000)

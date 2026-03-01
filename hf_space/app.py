import gradio as gr
import random
import time
import hashlib
import hmac
import json
from datetime import datetime

# ─────────────────────────────────────────────
# 공통 유틸
# ─────────────────────────────────────────────

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ─────────────────────────────────────────────
# Space 1: Payment Integration Demo
# NH농협 + AP2 결제 시뮬레이션
# ─────────────────────────────────────────────

VOUCHER_UNITS = [50000, 30000, 10000, 5000, 3000, 1000]

def convert_to_vouchers(amount: int):
    """금액을 바우처 단위로 분해"""
    remaining = amount
    vouchers = []
    for unit in VOUCHER_UNITS:
        count = remaining // unit
        if count > 0:
            vouchers.append({"unit": f"{unit:,} KRW", "count": count})
            remaining -= unit * count
    return vouchers

def simulate_transaction(amount: int):
    """Two-Phase Commit 시뮬레이션"""
    if amount <= 0:
        return {"error": "금액은 0보다 커야 합니다."}
    if amount > 1000000:
        return {"error": "1회 한도 초과 (최대 1,000,000 KRW)"}

    # 시뮬레이션 지연
    time.sleep(0.3)
    latency = random.randint(120, 200)
    vouchers = convert_to_vouchers(amount)

    audit_id = hashlib.sha256(f"{amount}{get_timestamp()}".encode()).hexdigest()[:12].upper()

    steps = [
        "✅ Phase 1 - Lock: NH농협 계정 잠금",
        "✅ Phase 1 - Lock: AP2 바우처 풀 잠금",
        "✅ Phase 2 - Commit: 출금 처리 완료",
        "✅ Phase 2 - Commit: 바우처 발행 완료",
        "✅ Rollback Guard: ACID 보장 확인",
    ]

    return {
        "status": "✅ SUCCESS",
        "amount": f"{amount:,} KRW",
        "latency": f"{latency}ms",
        "vouchers": vouchers,
        "two_phase_commit_steps": steps,
        "audit_log_id": audit_id,
        "timestamp": get_timestamp(),
        "note": "NH농협 ↔ AP2 실시간 연동 시뮬레이션"
    }

def payment_demo(amount):
    result = simulate_transaction(int(amount))
    return json.dumps(result, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────
# Space 2: Voice Protocol Simulator
# 오프라인 바우처 취소 (DTMF)
# ─────────────────────────────────────────────

SCENARIOS = {
    "농촌 산간 지역 (Rural Mountain)": {"data": 60, "voice": 95},
    "도심 지역 (Urban Area)":          {"data": 99, "voice": 99},
    "재난 지역 (Disaster Zone)":       {"data": 10, "voice": 70},
    "해안 도서 지역 (Remote Island)":  {"data": 30, "voice": 80},
}

def generate_dtmf(voucher_id: str, hmac_secret: str = "mulberry_secret"):
    """DTMF 코드 생성"""
    sig = hmac.new(
        hmac_secret.encode(),
        voucher_id.encode(),
        hashlib.sha256
    ).hexdigest()[:8].upper()
    return f"*#01-{voucher_id}-{sig}##"

def voice_revocation_demo(scenario: str, voucher_id: str):
    if not voucher_id.strip():
        voucher_id = "V" + str(random.randint(10000000, 99999999))

    coverage = SCENARIOS.get(scenario, {"data": 60, "voice": 95})
    data_cov = coverage["data"]
    voice_cov = coverage["voice"]

    time.sleep(0.3)

    dtmf_code = generate_dtmf(voucher_id)
    voice_time = random.randint(10, 18)
    data_time = "30+ 분" if data_cov < 50 else "2~5 분"
    success = voice_cov >= 70

    result = {
        "scenario": scenario,
        "network_coverage": {
            "data": f"{data_cov}%",
            "voice": f"{voice_cov}%"
        },
        "voucher_id": voucher_id,
        "dtmf_code": dtmf_code,
        "hmac_verified": "✅ 검증 완료",
        "voice_revocation": {
            "status": "✅ 성공" if success else "⚠️ 신호 약함",
            "time_taken": f"{voice_time}초"
        },
        "data_only_method": {
            "status": "❌ 불가" if data_cov < 50 else "⚠️ 느림",
            "time_taken": data_time
        },
        "improvement": f"음성 프로토콜이 데이터 방식 대비 {voice_time}초 처리 (오프라인 환경 최적화)",
        "timestamp": get_timestamp()
    }

    return json.dumps(result, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────
# Space 3: Game Theory Market (Spirit Score)
# 스킬 거래 마켓 + Nash Equilibrium
# ─────────────────────────────────────────────

SKILLS = {
    "Senior Support Master": {"base_price": 100, "desc": "고급 고객 지원 역량"},
    "Sales Excellence":       {"base_price": 75,  "desc": "영업 전문 스킬"},
    "Collaboration Pro":      {"base_price": 50,  "desc": "협업 & 소통 역량"},
    "Data Insight":           {"base_price": 80,  "desc": "데이터 분석 및 인사이트"},
    "Community Builder":      {"base_price": 60,  "desc": "커뮤니티 구축 전문"},
}

def calculate_nash_equilibrium(spirit_score: int, skill_price: int):
    """Nash Equilibrium 계산 (간소화 모델)"""
    total = 100
    individual = round(min(50, spirit_score / 4), 1)
    collaboration = round(min(30, spirit_score / 6), 1)
    social = total - individual - collaboration
    return {
        "individual_gain": f"{individual}%",
        "collaboration_gain": f"{collaboration}%",
        "social_impact": f"{round(social, 1)}%",
        "equilibrium_reached": individual > 0 and collaboration > 0
    }

def market_demo(skill_name: str, spirit_score: int):
    skill = SKILLS.get(skill_name)
    if not skill:
        return json.dumps({"error": "스킬을 선택해주세요."}, ensure_ascii=False)

    # 수요/공급에 따른 동적 가격
    market_fluctuation = random.randint(-10, 15)
    final_price = max(10, skill["base_price"] + market_fluctuation)
    can_afford = spirit_score >= final_price

    nash = calculate_nash_equilibrium(spirit_score, final_price)

    # 토너먼트 리그 시뮬레이션
    rank = random.randint(1, 100)
    league = "🏆 Gold" if rank <= 10 else "🥈 Silver" if rank <= 30 else "🥉 Bronze"

    result = {
        "skill": skill_name,
        "description": skill["desc"],
        "pricing": {
            "base_price": f"{skill['base_price']} SS",
            "market_price": f"{final_price} SS",
            "market_trend": f"{'▲' if market_fluctuation > 0 else '▼'} {abs(market_fluctuation)} SS"
        },
        "your_spirit_score": f"{spirit_score} SS",
        "can_purchase": "✅ 구매 가능" if can_afford else f"❌ {final_price - spirit_score} SS 부족",
        "nash_equilibrium": nash,
        "tournament_league": {
            "current_rank": f"#{rank}",
            "league": league
        },
        "timestamp": get_timestamp()
    }

    return json.dumps(result, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────
# Gradio UI
# ─────────────────────────────────────────────

CSS = """
#title { text-align: center; }
.tab-nav { font-size: 15px; }
footer { display: none !important; }
"""

with gr.Blocks(
    title="Mulberry Social-Agentic Commerce Demo",
    theme=gr.themes.Soft(primary_hue="green"),
    css=CSS
) as demo:

    gr.Markdown(
        """
        <div id="title">
        <h1>🌿 Mulberry Social-Agentic Commerce</h1>
        <h3>Interactive Technology Demo — For Google Engineers</h3>
        <p>식품사막화 제로 프로젝트 · 지역 경제 혁신 플랫폼</p>
        </div>
        """,
        elem_id="title"
    )

    # ── Tab 1: Payment ──────────────────────────
    with gr.Tab("🏦 Payment Integration"):
        gr.Markdown("### NH농협 + AP2 결제 시뮬레이터")
        gr.Markdown(
            "실시간 **Two-Phase Commit** 기반 결제 및 바우처 자동 분해를 체험하세요."
        )

        with gr.Row():
            with gr.Column(scale=1):
                amount_input = gr.Number(
                    label="💰 결제 금액 (KRW)",
                    value=23000,
                    minimum=1000,
                    maximum=1000000,
                    step=1000
                )
                pay_btn = gr.Button("⚡ 거래 실행", variant="primary")
                gr.Examples(
                    examples=[[23000], [55000], [100000], [300000]],
                    inputs=amount_input
                )
            with gr.Column(scale=2):
                pay_output = gr.Code(label="📊 거래 결과", language="json", lines=20)

        pay_btn.click(payment_demo, inputs=amount_input, outputs=pay_output)

    # ── Tab 2: Voice Protocol ───────────────────
    with gr.Tab("📡 Voice Protocol"):
        gr.Markdown("### 오프라인 바우처 취소 시뮬레이터")
        gr.Markdown(
            "데이터 연결 없이 **음성 통화(DTMF)**로 바우처를 취소하는 혁신 프로토콜입니다."
        )

        with gr.Row():
            with gr.Column(scale=1):
                scenario_input = gr.Dropdown(
                    choices=list(SCENARIOS.keys()),
                    value="농촌 산간 지역 (Rural Mountain)",
                    label="🗺️ 네트워크 환경 선택"
                )
                voucher_input = gr.Textbox(
                    label="🎫 바우처 ID (비워두면 자동 생성)",
                    placeholder="예: V12345678",
                    value=""
                )
                voice_btn = gr.Button("📞 취소 실행", variant="primary")
            with gr.Column(scale=2):
                voice_output = gr.Code(label="📊 취소 결과", language="json", lines=20)

        voice_btn.click(
            voice_revocation_demo,
            inputs=[scenario_input, voucher_input],
            outputs=voice_output
        )

    # ── Tab 3: Game Theory Market ───────────────
    with gr.Tab("🎮 Game Theory Market"):
        gr.Markdown("### 스킬 거래 마켓 + Nash Equilibrium")
        gr.Markdown(
            "Spirit Score로 스킬을 거래하고, **게임이론 기반 균형점**을 확인하세요."
        )

        with gr.Row():
            with gr.Column(scale=1):
                skill_input = gr.Dropdown(
                    choices=list(SKILLS.keys()),
                    value="Senior Support Master",
                    label="🧠 스킬 선택"
                )
                spirit_input = gr.Slider(
                    minimum=0,
                    maximum=300,
                    value=150,
                    step=5,
                    label="⭐ 보유 Spirit Score"
                )
                market_btn = gr.Button("🛒 스킬 구매 시뮬레이션", variant="primary")
                gr.Examples(
                    examples=[["Sales Excellence", 80], ["Collaboration Pro", 200]],
                    inputs=[skill_input, spirit_input]
                )
            with gr.Column(scale=2):
                market_output = gr.Code(label="📊 마켓 결과", language="json", lines=20)

        market_btn.click(
            market_demo,
            inputs=[skill_input, spirit_input],
            outputs=market_output
        )

    # ── Footer ──────────────────────────────────
    gr.Markdown(
        """
        ---
        🌿 **Mulberry Project** | 식품사막화 제로 프로젝트
        Built with [Gradio](https://gradio.app) · [HuggingFace](https://huggingface.co/re-eul) · Powered by Anthropic Claude
        """
    )

if __name__ == "__main__":
    demo.launch()

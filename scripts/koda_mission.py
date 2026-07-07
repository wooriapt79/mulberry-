# -*- coding: utf-8 -*-
"""
⚙️ Mulberry AgenticAI Hub — Koda Tech Mission v1.0
Koda CTO: 기술 검토 · 아키텍처 설계 · 코드 품질 판단

Agent: Koda (CTO — Chief Technology Officer)
Date: 2026-06-07
"""

import os
import json
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Koda-Mission] - %(levelname)s - %(message)s'
)

# ── 봇 루프 방지 (Issue #137) ──────────────────────────────────────────────
BOT_MARKERS = [
    "<!-- bot-response -->",
    "🌙 **Jr. TRANG (Luna)**",
    "🌿 **Sr. Trang Manager**",
    "🔧 **Koda CTO",
    "🤖 AUTO",
    "🤖→👤 AI 대리",
]

MIN_RESPONSE_LENGTH = 30


def is_bot_comment(comment_body: str) -> bool:
    if not comment_body:
        return False
    for marker in BOT_MARKERS:
        if marker in comment_body:
            return True
    return False


def is_valid_response(response_text: str) -> bool:
    """위생 게이트 — 빈 응답·인트로 템플릿만 있는 응답 차단"""
    if not response_text or len(response_text.strip()) < MIN_RESPONSE_LENGTH:
        return False
    hollow_patterns = [
        "이슈를 검토했습니다. 기술 구현·아키텍처·성능 관점에서 분석합니다.",
    ]
    stripped = response_text.strip()
    for pattern in hollow_patterns:
        if stripped == pattern or (stripped.startswith(pattern) and len(stripped) < len(pattern) + 10):
            return False
    return True


class KodaMission:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.agent_name = "koda"
        self.agent_role = "CTO"
        self.spirit_score_threshold = 0.85

        logging.info("⚙️ Koda Mission initialized — CTO mode online")

    def validate_passport(self) -> bool:
        passport_path = "agentpassport/agents/koda.yaml"
        if os.path.exists(passport_path):
            logging.info("✅ Koda passport validated")
            return True
        logging.warning("⚠️ Passport not found — proceeding with default permissions")
        return True

    def spirit_gate_check(self, content: str) -> float:
        restricted = ["프로덕션 삭제", "DB 초기화", "강제 배포"]
        score = 1.0
        for keyword in restricted:
            if keyword in content:
                score -= 0.15
        return max(0.0, score)

    def analyze_issue(self, issue_url: str, comment_body: str, comment_author: str = "") -> Dict[str, Any]:
        logging.info(f"📥 Koda analyzing: {issue_url}")

        # 봇 루프 방지 (Issue #137)
        if comment_author in ("github-actions[bot]", "luna-bot", "trang-bot"):
            logging.info("⏭️ Bot author detected — skipping")
            return {"status": "SKIPPED", "reason": "bot_author"}

        if is_bot_comment(comment_body):
            logging.info("⏭️ Bot marker detected in comment — skipping")
            return {"status": "SKIPPED", "reason": "bot_marker"}

        spirit_score = self.spirit_gate_check(comment_body)
        if spirit_score < self.spirit_score_threshold:
            return {
                "status": "HUMAN_REVIEW_REQUIRED",
                "reason": f"Spirit score {spirit_score} below threshold",
                "agent": self.agent_name
            }

        response_text = self._generate_cto_response(comment_body)

        # 위생 게이트 — 빈 응답 차단 (Issue #137)
        if not is_valid_response(response_text):
            logging.warning("⚠️ 위생 게이트 차단 — 응답 내용 없음. 댓글 등록 skip.")
            return {"status": "SKIPPED", "reason": "hygiene_gate_empty_response"}

        formatted = self._format_comment(response_text)
        analysis = {
            "agent": self.agent_name,
            "role": self.agent_role,
            "issue_url": issue_url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "spirit_score": spirit_score,
            "analysis": response_text,
            "status": "SUCCESS"
        }

        self._post_github_comment(issue_url, formatted)
        self._record_training_log(analysis)
        return analysis

    def _generate_cto_response(self, comment_body: str) -> str:
        if not self.api_key:
            logging.warning("⚠️ ANTHROPIC_API_KEY 없음 — Mock 응답 반환")
            return (
                "기술 검토 의견을 작성 중입니다. "
                "구현 타당성·아키텍처·보안 관점에서 검토 후 답변하겠습니다."
            )
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=800,
                system=(
                    "당신은 Koda CTO입니다. Mulberry AI 팀의 최고기술책임자입니다.\n"
                    "GitHub 이슈 댓글을 기술 구현·아키텍처·보안·성능 관점에서 검토하고 의견을 제시하세요.\n"
                    "결론 먼저, 간결하게, 마크다운 사용. 배지 🔧 명시."
                ),
                messages=[{
                    "role": "user",
                    "content": f"GitHub 이슈 댓글에 Koda CTO로서 기술 검토 의견을 달아주세요.\n\n댓글 내용:\n{comment_body}"
                }]
            )
            return message.content[0].text
        except Exception as e:
            logging.error(f"❌ Claude API 오류: {e}")
            return "기술 검토 중 오류 발생. 팀 확인 요청합니다."

    def _format_comment(self, response_text: str) -> str:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return (
            f"<!-- bot-response -->\n"
            f"🔧 **Koda CTO** · 🤖→👤 AI 대리 · {now}\n\n"
            f"{response_text}\n\n"
            f"---\n"
            f"*— Koda, CTO, Mulberry Team*"
        )

    def _post_github_comment(self, issue_url: str, comment: str) -> None:
        if not self.token:
            logging.warning("⚠️ GITHUB_TOKEN 없음 — 댓글 게시 스킵")
            return
        try:
            import requests
            parts = issue_url.rstrip("/").split("/")
            owner, repo, issue_number = parts[-4], parts[-3], parts[-1]
            api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
            headers = {"Authorization": f"token {self.token}", "Accept": "application/vnd.github.v3+json"}
            response = requests.post(api_url, json={"body": comment}, headers=headers)
            if response.status_code == 201:
                logging.info("✅ GitHub 댓글 게시 완료")
            else:
                logging.error(f"❌ 댓글 게시 실패: {response.status_code}")
        except Exception as e:
            logging.error(f"❌ GitHub API 오류: {e}")

    def _record_training_log(self, data: Dict) -> None:
        os.makedirs("training_logs", exist_ok=True)
        log_path = f"training_logs/koda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"📚 Training log saved: {log_path}")


def main():
    parser = argparse.ArgumentParser(description="Koda Tech Mission")
    parser.add_argument("--issue", type=str, default="")
    parser.add_argument("--comment", type=str, default="")
    parser.add_argument("--author", type=str, default="")
    parser.add_argument("--token", type=str, default="")
    args = parser.parse_args()

    # 보안: COMMENT_BODY 환경변수 우선 사용 (shell injection 방지, Issue #137)
    comment = os.getenv("COMMENT_BODY", args.comment)
    issue = os.getenv("ISSUE_URL", args.issue)
    author = os.getenv("COMMENT_AUTHOR", args.author)

    mission = KodaMission(token=args.token)
    mission.validate_passport()
    result = mission.analyze_issue(issue, comment, author)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

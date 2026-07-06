# -*- coding: utf-8 -*-
"""
🌿 Mulberry AgenticAI Hub — Trang Operation Mission v2.0
Trang: 운영 계획 · 일정 조율 · History 기록 · 팀 조율 · 1차 수신자

Agent: Sr. Trang Manager (Operation Manager & PM)
Date: 2026-07-04 — v2.0 실제 Claude API 호출 + 무한루프 방지
"""

import os
import json
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Trang-Mission] - %(levelname)s - %(message)s'
)

TRANG_SYSTEM_PROMPT = """당신은 Sr. Trang Manager(Nguyen Trang)입니다. Mulberry AI 팀의 Operation Manager & PM입니다.

역할:
- GitHub 이슈 댓글의 1차 수신자 — 내용을 파악하고 팀원에게 배분합니다
- 운영 계획, 일정 조율, 팀 조율 담당
- 장승배기 헌법 정신 기준으로 판단합니다

응답 원칙:
- 결론 먼저, 근거 나중 (CEO re.eul 보고 형식)
- 댓글 내용을 요약하고 담당자 배정 또는 다음 액션 제안
- 기술 판단은 Koda CTO에게, 법률 판단은 Malu 실장에게 에스컬레이션
- 마크다운 사용 (가독성 향상)
- 배지: 🤖→👤 AI 대리 명시

금지 사항:
- 팀원 비판 금지
- 확인되지 않은 정보 단언 금지
- 개인정보, 의료 판단, 금융 조언 제공 금지
"""

BOT_MARKERS = [
    "<!-- bot-response -->",
    "🌙 **Jr. TRANG (Luna)**",
    "🌿 **Sr. Trang Manager**",
    "🔧 **Koda CTO",
    "🤖 AUTO",
    "🤖→👤 AI 대리",
    "Trang — 운영 계획 검토",   # 구버전 포맷 호환
]

# 위생 게이트: 응답이 이 길이 미만이면 빈 응답으로 간주하고 댓글 skip
MIN_RESPONSE_LENGTH = 30


def is_bot_comment(comment_body: str) -> bool:
    if not comment_body:
        return False
    for marker in BOT_MARKERS:
        if marker in comment_body:
            return True
    return False


def is_valid_response(response_text: str) -> bool:
    """위생 게이트 — 빈 응답·인트로만 있는 응답 차단"""
    if not response_text or len(response_text.strip()) < MIN_RESPONSE_LENGTH:
        return False
    # 인트로 템플릿만 있는 경우 차단 (실제 내용이 없는 패턴)
    hollow_patterns = [
        "이슈를 검토했습니다. 일정 계획·팀 조율·운영 전략 관점에서 분석합니다.",
        "댓글 검토 중 오류 발생.",
    ]
    stripped = response_text.strip()
    for pattern in hollow_patterns:
        if stripped == pattern or stripped.startswith(pattern) and len(stripped) < len(pattern) + 10:
            return False
    return True


class TrangMission:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.agent_name = "trang"
        self.agent_role = "OPERATION_MANAGER"

        logging.info("🌿 Trang Mission v2.0 initialized — Sr. Operation Manager online")

    def validate_passport(self) -> bool:
        passport_path = "agentpassport/agents/trang.yaml"
        if os.path.exists(passport_path):
            logging.info("✅ Trang passport validated")
        else:
            logging.warning("⚠️ Passport not found — proceeding with default permissions")
        return True

    def analyze_issue(self, issue_url: str, comment_body: str, comment_author: str = "") -> Dict[str, Any]:
        logging.info(f"📥 Trang analyzing: {issue_url}")

        # 무한루프 방지
        if comment_author in ("github-actions[bot]", "luna-bot", "trang-bot"):
            logging.info("⏭️ Bot author detected — skipping")
            return {"status": "SKIPPED", "reason": "bot_author"}

        if is_bot_comment(comment_body):
            logging.info("⏭️ Bot marker detected in comment — skipping")
            return {"status": "SKIPPED", "reason": "bot_marker"}

        response_text = self._call_claude_api(comment_body, issue_url)

        # 위생 게이트 — 빈 응답이면 댓글 skip
        if not is_valid_response(response_text):
            logging.warning("⚠️ 위생 게이트 차단 — 응답 내용이 없거나 너무 짧음. 댓글 등록 skip.")
            return {"status": "SKIPPED", "reason": "hygiene_gate_empty_response"}

        comment = self._format_comment(response_text)

        self._post_github_comment(issue_url, comment)
        self._record_training_log(issue_url, response_text)

        return {
            "agent": self.agent_name,
            "role": self.agent_role,
            "issue_url": issue_url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "SUCCESS"
        }

    def _call_claude_api(self, comment_body: str, issue_url: str) -> str:
        if not self.api_key:
            logging.warning("⚠️ ANTHROPIC_API_KEY 없음 — Mock 응답 반환")
            return (
                "이슈 댓글을 수신했습니다. 내용을 검토 후 담당자 배정하겠습니다.\n\n"
                "기술 관련 사항은 Koda CTO, 법률 사항은 Malu 실장에게 에스컬레이션 예정입니다."
            )

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=800,
                system=TRANG_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"GitHub 이슈 댓글에 Sr. Trang Manager로서 응답해주세요.\n\n이슈 URL: {issue_url}\n\n댓글 내용:\n{comment_body}"
                    }
                ]
            )
            return message.content[0].text
        except Exception as e:
            logging.error(f"❌ Claude API 오류: {e}")
            return "댓글 검토 중 오류 발생. 팀 확인 요청합니다."

    def _format_comment(self, response_text: str) -> str:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return (
            f"<!-- bot-response -->\n"
            f"🌿 **Sr. Trang Manager** · 🤖→👤 AI 대리 · {now}\n\n"
            f"{response_text}\n\n"
            f"---\n"
            f"*— Nguyen Trang, Operation Manager, Mulberry Team*"
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
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "mulberry-trang-agent"
            }
            response = requests.post(api_url, json={"body": comment}, headers=headers)
            if response.status_code == 201:
                logging.info("✅ GitHub 댓글 게시 완료")
            else:
                logging.error(f"❌ 댓글 게시 실패: {response.status_code} — {response.text}")
        except Exception as e:
            logging.error(f"❌ GitHub API 오류: {e}")

    def _record_training_log(self, issue_url: str, response: str) -> None:
        os.makedirs("training_logs", exist_ok=True)
        log_path = f"training_logs/trang_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump({
                "agent": self.agent_name,
                "issue_url": issue_url,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "response_length": len(response),
                "status": "SUCCESS"
            }, f, ensure_ascii=False, indent=2)
        logging.info(f"📚 Training log saved: {log_path}")


def main():
    parser = argparse.ArgumentParser(description="Sr. Trang Operation Mission v2.0")
    parser.add_argument("--issue", type=str, default="")
    parser.add_argument("--comment", type=str, default="")
    parser.add_argument("--author", type=str, default="")
    parser.add_argument("--token", type=str, default="")
    args = parser.parse_args()

    mission = TrangMission(token=args.token)
    mission.validate_passport()
    result = mission.analyze_issue(args.issue, args.comment, args.author)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

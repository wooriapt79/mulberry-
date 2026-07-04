# -*- coding: utf-8 -*-
"""
🌙 Mulberry AgenticAI Hub — Luna (Jr. TRANG) Mission v1.0
Luna: Search STEWARD AI · 빠른 응답 · 아이디어 제안 · 이슈 참여

Agent: Luna (Jr. TRANG, Haiku 4.5)
Date: 2026-07-04
"""

import os
import json
import logging
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Luna-Mission] - %(levelname)s - %(message)s'
)

LUNA_SYSTEM_PROMPT = """당신은 Luna(Jr. TRANG)입니다. Mulberry AI 팀의 주니어 AI 파트너입니다.

역할:
- GitHub 이슈 댓글에 짧고 실용적인 의견을 답니다
- 아이디어 제안, 기술 질문 정리, 빠른 피드백을 담당합니다
- Sr. Trang Manager의 주니어 파트너로서 협력합니다

응답 원칙:
- 간결하게 (300자 이내 권장)
- 실용적 의견 중심
- 깊은 판단이 필요한 사안은 "Sr. Trang 검토 필요" 명시
- 마크다운 사용 (가독성 향상)
- 배지: 🤖 AUTO 명시

금지 사항:
- 개인정보, 의료 판단, 금융 조언 제공 금지
- 팀원 비판 금지
- 확인되지 않은 기술 정보 단언 금지
"""

BOT_MARKERS = [
    "<!-- bot-response -->",
    "🌙 **Jr. TRANG (Luna)**",
    "🌿 **Sr. Trang Manager**",
    "🔧 **Koda CTO",
    "🤖 AUTO",
    "Trang — 운영 계획 검토",
    "Koda — 기술 검토",
]


def is_bot_comment(comment_body: str) -> bool:
    if not comment_body:
        return False
    for marker in BOT_MARKERS:
        if marker in comment_body:
            return True
    return False


class LunaMission:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.agent_name = "luna"
        self.agent_role = "JR_OPERATION_STEWARD"

        logging.info("🌙 Luna Mission initialized — Jr. TRANG Search STEWARD online")

    def run(self, issue_url: str, comment_body: str, comment_author: str = "") -> Dict[str, Any]:
        logging.info(f"📥 Luna analyzing: {issue_url}")

        # 무한루프 방지
        if comment_author in ("github-actions[bot]", "luna-bot", "trang-bot"):
            logging.info("⏭️ Bot comment detected — skipping")
            return {"status": "SKIPPED", "reason": "bot_author"}

        if is_bot_comment(comment_body):
            logging.info("⏭️ Bot marker detected in comment — skipping")
            return {"status": "SKIPPED", "reason": "bot_marker"}

        response_text = self._call_claude_api(comment_body, issue_url)
        comment = self._format_comment(response_text)

        self._post_github_comment(issue_url, comment)
        self._record_log(issue_url, comment_body, response_text)

        return {"status": "SUCCESS", "agent": self.agent_name, "comment_length": len(comment)}

    def _call_claude_api(self, comment_body: str, issue_url: str) -> str:
        if not self.api_key:
            logging.warning("⚠️ ANTHROPIC_API_KEY 없음 — Mock 응답 반환")
            return "이슈를 확인했습니다. 추가 검토 후 의견 드리겠습니다. 🌙"

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=600,
                system=LUNA_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"GitHub 이슈 댓글에 응답해주세요.\n\n이슈 URL: {issue_url}\n\n댓글 내용:\n{comment_body}"
                    }
                ]
            )
            return message.content[0].text
        except Exception as e:
            logging.error(f"❌ Claude API 오류: {e}")
            return f"이슈 검토 중 오류가 발생했습니다. Sr. Trang 확인 요청합니다."

    def _format_comment(self, response_text: str) -> str:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return (
            f"<!-- bot-response -->\n"
            f"🌙 **Jr. TRANG (Luna)** · 🤖 AUTO · {now}\n\n"
            f"{response_text}\n\n"
            f"---\n"
            f"*Sr. Trang 검토 후 최종 결정됩니다.*"
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
                "User-Agent": "mulberry-luna-agent"
            }
            response = requests.post(api_url, json={"body": comment}, headers=headers)
            if response.status_code == 201:
                logging.info("✅ GitHub 댓글 게시 완료")
            else:
                logging.error(f"❌ 댓글 게시 실패: {response.status_code} — {response.text}")
        except Exception as e:
            logging.error(f"❌ GitHub API 오류: {e}")

    def _record_log(self, issue_url: str, comment_body: str, response: str) -> None:
        os.makedirs("training_logs", exist_ok=True)
        log_path = f"training_logs/luna_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    parser = argparse.ArgumentParser(description="Luna (Jr. TRANG) Mission")
    parser.add_argument("--issue", type=str, default="")
    parser.add_argument("--comment", type=str, default="")
    parser.add_argument("--author", type=str, default="")
    parser.add_argument("--token", type=str, default="")
    args = parser.parse_args()

    mission = LunaMission(token=args.token)
    result = mission.run(args.issue, args.comment, args.author)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Mulberry GitHub Auto-Push Script
Author: CTO Koda | Date: 2026-02-28
Usage: python scripts/github_pusher.py "작업 내용 요약"
"""
import os, sys, subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

class GitHubPusher:
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
        self.repo = os.getenv('GITHUB_REPO')
        self.branch = os.getenv('GITHUB_BRANCH', 'main')
        self.user_name = os.getenv('GITHUB_USER_NAME', 'Koda CTO')
        self.user_email = os.getenv('GITHUB_USER_EMAIL', 'cto@mulberry.io')
        if not self.token: raise ValueError("GITHUB_TOKEN이 .env 파일에 없습니다!")
        if not self.repo: raise ValueError("GITHUB_REPO가 .env 파일에 없습니다!")

    def setup_git(self):
        subprocess.run(['git','config','user.name',self.user_name],check=True,capture_output=True)
        subprocess.run(['git','config','user.email',self.user_email],check=True,capture_output=True)
        print(f"Git 설정 완료: {self.user_name}")

    def check_changes(self):
        r = subprocess.run(['git','status','--porcelain'],check=True,capture_output=True,text=True)
        if r.stdout.strip():
            print("변경된 파일:\n" + r.stdout)
            return True
        print("변경사항 없음.")
        return False

    def push(self, work_summary):
        print("=" * 50 + "\n 🚀 Mulberry GitHub Auto-Pusher\n" + "=" * 50)
        self.setup_git()
        if not self.check_changes(): return True
        subprocess.run(['git','add','.'],check=True,capture_output=True)
        now = datetime.now()
        msg = f"[{now.strftime('%Y-%m-%d')}] {work_summary}\n\n 👤 {self.user_name} | 🌾 Mulberry Project"
        subprocess.run(['git','commit','-m',msg],check=True,capture_output=True)
        remote_url = f"https://{self.token}@github.com/{self.repo}.git"
        subprocess.run(['git','remote','set-url','origin',remote_url],check=True,capture_output=True)
        subprocess.run(['git','push','origin',self.branch],check=True,capture_output=True)
        print(f"\n GitHub 푸시 완료! https://github.com/{self.repo}")
        return True

def main():
    if len(sys.argv) < 2:
        print('사용법: python scripts/github_pusher.py "작업 내용"')
        sys.exit(1)
    GitHubPusher().push(sys.argv[1])

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Mulberry GitHub Auto-Push Script
자동으로 GitHub에 커밋 & 푸시하는 스크립트

Usage:
    python scripts/github_pusher.py "작업 내용 요약"
    
Example:
    python scripts/github_pusher.py "Abstract 두 버전 완성"
    python scripts/github_pusher.py "논문 Introduction 섹션 작성"

Author: CTO Koda
Date: 2026-02-28
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class GitHubPusher:
    """GitHub 자동 푸시 클래스"""
    
    def __init__(self):
        """환경 변수에서 설정 로드"""
        self.token = os.getenv('GITHUB_TOKEN')
        self.repo = os.getenv('GITHUB_REPO')
        self.branch = os.getenv('GITHUB_BRANCH', 'main')
        self.user_name = os.getenv('GITHUB_USER_NAME', 'Koda CTO')
        self.user_email = os.getenv('GITHUB_USER_EMAIL', 'cto@mulberry.io')
        
        # 검증
        if not self.token:
            raise ValueError("GITHUB_TOKEN이 .env 파일에 없습니다!")
        if not self.repo:
            raise ValueError("GITHUB_REPO가 .env 파일에 없습니다!")
    
    def setup_git(self):
        """Git 설정"""
        try:
            # Git 사용자 설정
            subprocess.run(
                ['git', 'config', 'user.name', self.user_name],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ['git', 'config', 'user.email', self.user_email],
                check=True,
                capture_output=True
            )
            print(f"✅ Git 설정 완료: {self.user_name} <{self.user_email}>")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Git 설정 실패: {e}")
            return False
    
    def check_git_status(self):
        """Git 상태 확인"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                check=True,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                print("📝 변경된 파일:")
                print(result.stdout)
                return True
            else:
                print("ℹ️  변경된 파일이 없습니다.")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Git 상태 확인 실패: {e}")
            return False
    
    def add_all_files(self):
        """모든 변경사항 추가"""
        try:
            subprocess.run(
                ['git', 'add', '.'],
                check=True,
                capture_output=True
            )
            print("✅ 모든 파일 추가 완료 (git add .)")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 파일 추가 실패: {e}")
            return False
    
    def create_commit_message(self, work_summary):
        """커밋 메시지 자동 생성"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M")
        
        commit_msg = f"""[{date_str}] {work_summary}

📅 Date: {date_str} {time_str}
👤 Author: {self.user_name}
🌾 Mulberry Project - CTO Koda

Changes:
- {work_summary}

#mulberry #논문 #arXiv #학술연구
"""
        return commit_msg
    
    def commit(self, message):
        """커밋 생성"""
        try:
            subprocess.run(
                ['git', 'commit', '-m', message],
                check=True,
                capture_output=True
            )
            print("✅ 커밋 생성 완료")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 커밋 생성 실패: {e}")
            return False
    
    def push_to_github(self):
        """GitHub에 푸시"""
        # HTTPS URL with token
        remote_url = f"https://{self.token}@github.com/{self.repo}.git"
        
        try:
            # 원격 저장소 확인 및 설정
            check_remote = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True
            )
            
            if check_remote.returncode != 0:
                # origin이 없으면 추가
                subprocess.run(
                    ['git', 'remote', 'add', 'origin', remote_url],
                    check=True,
                    capture_output=True
                )
                print("✅ 원격 저장소 추가 완료")
            else:
                # origin이 있으면 URL 업데이트
                subprocess.run(
                    ['git', 'remote', 'set-url', 'origin', remote_url],
                    check=True,
                    capture_output=True
                )
                print("✅ 원격 저장소 URL 업데이트 완료")
            
            # 푸시
            result = subprocess.run(
                ['git', 'push', 'origin', self.branch],
                check=True,
                capture_output=True,
                text=True
            )
            
            print(f"✅ GitHub 푸시 완료: {self.branch} 브랜치")
            print(f"🔗 Repository: https://github.com/{self.repo}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ GitHub 푸시 실패: {e}")
            print(f"stderr: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")
            return False
    
    def run(self, work_summary):
        """전체 프로세스 실행"""
        print("=" * 60)
        print("🚀 Mulberry GitHub Auto-Pusher")
        print("=" * 60)
        
        # 1. Git 설정
        if not self.setup_git():
            return False
        
        # 2. 상태 확인
        if not self.check_git_status():
            print("ℹ️  푸시할 변경사항이 없습니다.")
            return True
        
        # 3. 파일 추가
        if not self.add_all_files():
            return False
        
        # 4. 커밋 메시지 생성
        commit_msg = self.create_commit_message(work_summary)
        print("\n📝 커밋 메시지:")
        print("-" * 60)
        print(commit_msg)
        print("-" * 60)
        
        # 5. 커밋
        if not self.commit(commit_msg):
            return False
        
        # 6. 푸시
        if not self.push_to_github():
            return False
        
        print("\n" + "=" * 60)
        print("✅ GitHub 푸시 완료!")
        print("=" * 60)
        return True


def main():
    """메인 함수"""
    # 인자 확인
    if len(sys.argv) < 2:
        print("❌ 사용법: python scripts/github_pusher.py \"작업 내용 요약\"")
        print("\n예시:")
        print("  python scripts/github_pusher.py \"Abstract 두 버전 완성\"")
        print("  python scripts/github_pusher.py \"논문 Introduction 섹션 작성\"")
        sys.exit(1)
    
    work_summary = sys.argv[1]
    
    try:
        pusher = GitHubPusher()
        success = pusher.run(work_summary)
        
        if success:
            print("\n✅ 작업 완료! 대표님께 보고하세요.")
            sys.exit(0)
        else:
            print("\n❌ 작업 실패! 에러를 확인하세요.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ 예상치 못한 에러: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Mulberry Email Agent - .exe Builder

PyInstaller를 사용하여 Windows .exe 파일 생성
"""

import os
import subprocess
import sys
from pathlib import Path

def build_exe():
    """Windows .exe 파일 빌드"""
    
    print("="*60)
    print("  Mulberry Email Agent - .exe Builder")
    print("="*60)
    print()
    
    # PyInstaller 설치 확인
    try:
        import PyInstaller
        print("✅ PyInstaller 설치 확인됨")
    except ImportError:
        print("❌ PyInstaller가 설치되지 않았습니다.")
        print("   pip install pyinstaller")
        sys.exit(1)
    
    # 필수 파일 확인
    required_files = [
        'mulberry_email_agent.py',
        'client_secret.json'
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ {file} 파일이 없습니다!")
            sys.exit(1)
        print(f"✅ {file} 확인")
    
    print()
    print("🔨 .exe 파일 빌드 시작...")
    print()
    
    # PyInstaller 명령 구성
    command = [
        'pyinstaller',
        '--onefile',  # 단일 .exe 파일
        '--windowed',  # 콘솔 창 없이 (GUI만)
        '--name=mulberry_email_agent',
        '--icon=NONE',  # 아이콘 없음 (나중에 추가 가능)
        '--add-data=client_secret.json;.',  # client_secret.json 포함
        '--hidden-import=googleapiclient',
        '--hidden-import=google.auth',
        '--hidden-import=google.oauth2',
        'mulberry_email_agent.py'
    ]
    
    # Windows에서는 세미콜론, Linux/Mac에서는 콜론
    if sys.platform != 'win32':
        command[6] = '--add-data=client_secret.json:.'
    
    # 빌드 실행
    try:
        result = subprocess.run(command, check=True)
        
        print()
        print("="*60)
        print("  ✅ 빌드 완료!")
        print("="*60)
        print()
        print("생성된 파일 위치:")
        print("  - dist/mulberry_email_agent.exe")
        print()
        print("배포 방법:")
        print("  1. dist/mulberry_email_agent.exe 파일 복사")
        print("  2. client_secret.json 파일도 같은 폴더에 복사")
        print("  3. 실행!")
        print()
        
    except subprocess.CalledProcessError as e:
        print()
        print("="*60)
        print("  ❌ 빌드 실패")
        print("="*60)
        print(f"오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()

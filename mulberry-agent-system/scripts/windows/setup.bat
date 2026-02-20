@echo off
REM Mulberry Agent System - Windows 설치 스크립트
REM CTO Koda

echo.
echo ====================================
echo    Mulberry Agent System 설치
echo ====================================
echo.

REM Python 버전 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python이 설치되어 있지 않습니다!
    echo https://www.python.org/downloads/ 에서 Python 3.10 이상을 설치하세요.
    pause
    exit /b 1
)

echo [INFO] Python 확인 완료
python --version

REM 가상 환경 생성
if not exist "venv" (
    echo [INFO] 가상 환경 생성 중...
    python -m venv venv
) else (
    echo [INFO] 가상 환경이 이미 존재합니다.
)

REM 가상 환경 활성화
echo [INFO] 가상 환경 활성화 중...
call venv\Scripts\activate.bat

REM 의존성 설치
echo [INFO] 의존성 설치 중...
pip install --upgrade pip
pip install -r requirements.txt

REM 설정 파일 생성
if not exist "config\config.json" (
    if exist "config\config.example.json" (
        echo [INFO] 설정 파일 생성 중...
        copy config\config.example.json config\config.json
        echo [INFO] config\config.json 파일을 수정하세요!
    )
)

REM 데이터 폴더 생성
if not exist "data" (
    echo [INFO] 데이터 폴더 생성 중...
    mkdir data
)

REM 로그 폴더 생성
if not exist "logs" (
    echo [INFO] 로그 폴더 생성 중...
    mkdir logs
)

echo.
echo ====================================
echo    설치 완료!
echo ====================================
echo.
echo 다음 명령으로 서버를 시작하세요:
echo   scripts\windows\start.bat
echo.
echo 또는:
echo   venv\Scripts\activate
echo   python main.py
echo.
pause

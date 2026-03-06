@echo off
REM Mulberry Agent System - Windows 시작 스크립트
REM CTO Koda

echo.
echo ====================================
echo    Mulberry Agent System
echo ====================================
echo.

REM 가상 환경 확인
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] 가상 환경이 없습니다!
    echo 먼저 setup.bat을 실행하세요.
    pause
    exit /b 1
)

REM 가상 환경 활성화
echo [INFO] 가상 환경 활성화 중...
call venv\Scripts\activate.bat

REM 서버 시작
echo [INFO] 서버 시작 중...
echo.
python main.py

pause

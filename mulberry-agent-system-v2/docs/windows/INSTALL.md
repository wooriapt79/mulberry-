# 🪟 Mulberry Agent System - Windows 설치 가이드

**CTO Koda**  
**2024년 2월 20일**

---

## 📋 개요

Mulberry AI Agent System을 Windows 환경에서 설치하고 운영하는 가이드입니다.

---

## 💻 시스템 요구사항

### 최소 사양
```
OS: Windows 10 (64-bit) 이상
CPU: Intel Core i5 또는 동급
RAM: 8GB
Storage: 100GB SSD
Python: 3.10 이상
```

### 권장 사양
```
OS: Windows 11 Pro (64-bit)
CPU: Intel Core i7 또는 동급
RAM: 16GB
Storage: 256GB NVMe SSD
Python: 3.11
```

---

## 🔧 Step 1: Python 설치

### 1.1 Python 다운로드

```
https://www.python.org/downloads/
→ Python 3.11.x 다운로드
```

### 1.2 설치 시 주의사항

**중요!**
- ✅ "Add Python to PATH" 체크
- ✅ "Install for all users" 선택
- ✅ "Customize installation" → "pip" 포함 확인

### 1.3 설치 확인

```cmd
python --version
pip --version
```

---

## 📦 Step 2: 데이터베이스 설치

### 2.1 PostgreSQL 설치 (선택)

```
https://www.postgresql.org/download/windows/
→ PostgreSQL 15.x 다운로드
```

**설정:**
- Port: 5432 (기본값)
- 비밀번호 설정 (기억할 것!)
- 설치 후 pgAdmin 자동 실행

**데이터베이스 생성:**
```sql
CREATE DATABASE mulberry_agents;
```

### 2.2 SQLite 사용 (간단)

**별도 설치 불필요!**
- Python 기본 포함
- 작은 규모에 적합
- 설정 없이 바로 사용 가능

---

## 🚀 Step 3: Mulberry Agent System 설치

### 3.1 프로젝트 다운로드

```cmd
# 다운로드 폴더로 이동
cd C:\Users\%USERNAME%\Downloads

# ZIP 압축 해제
# mulberry-agent-system.zip 압축 풀기

# 프로젝트 폴더로 이동
cd mulberry-agent-system
```

### 3.2 가상 환경 생성

```cmd
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
venv\Scripts\activate

# 프롬프트가 (venv)로 시작하면 성공!
```

### 3.3 의존성 설치

```cmd
# requirements.txt가 있는 경우
pip install -r requirements.txt

# 또는 수동 설치
pip install fastapi uvicorn sqlalchemy psycopg2-binary
```

---

## ⚙️ Step 4: 설정 파일 구성

### 4.1 설정 파일 생성

```cmd
# config 폴더로 이동
cd config

# 예제 파일 복사
copy config.example.json config.json

# 메모장으로 편집
notepad config.json
```

### 4.2 config.json 설정

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "database": {
    "type": "sqlite",
    "path": "data/mulberry.db"
  },
  "agent_factory": {
    "max_daily_agents": 10,
    "training_hours": 1
  },
  "google_business": {
    "api_key": "YOUR_API_KEY_HERE"
  }
}
```

---

## 🗄️ Step 5: 데이터베이스 초기화

### 5.1 스키마 생성

```cmd
# 프로젝트 루트로 이동
cd C:\Users\%USERNAME%\Downloads\mulberry-agent-system

# 가상 환경 활성화 (아직 안 했다면)
venv\Scripts\activate

# 데이터베이스 초기화 스크립트 실행
python scripts\windows\init_database.py
```

**출력 예시:**
```
✅ 데이터베이스 초기화 완료
✅ agents 테이블 생성
✅ terminals 테이블 생성
✅ documents 테이블 생성
✅ meetings 테이블 생성
✅ interactions 테이블 생성
```

---

## 🎬 Step 6: 서버 시작

### 6.1 개발 모드로 시작

```cmd
# 가상 환경 활성화
venv\Scripts\activate

# 서버 시작
python main.py
```

**출력 예시:**
```
🌾 Mulberry Agent System 시작
📡 서버: http://localhost:8000
📚 API 문서: http://localhost:8000/docs
```

### 6.2 브라우저에서 확인

```
http://localhost:8000/docs
```

**Swagger UI가 열리면 성공!**

---

## 🔄 Step 7: 에이전트 생성 테스트

### 7.1 테스트 스크립트 실행

```cmd
# 가상 환경 활성화
venv\Scripts\activate

# 테스트 실행
python scripts\windows\test_agent_creation.py
```

**출력 예시:**
```
✅ 에이전트 생성 완료: AGENT-20240220-ABC12345 (테스트 에이전트)
   오늘 생성: 1/10

🌾 에이전트 AGENT-20240220-ABC12345 장승배기 헌법 학습 시작
   학습 시간: 1시간
   완료 예정: 2024-02-20 15:30:00
```

---

## 📊 Step 8: 관리자 대시보드 접속

```
http://localhost:8000/admin
```

**대시보드에서 확인 가능:**
- 에이전트 목록
- 단말기 현황
- 오늘의 통계
- 실시간 상호작용

---

## 🔧 Step 9: Windows 서비스 등록 (선택사항)

### 9.1 NSSM 다운로드

```
https://nssm.cc/download
→ nssm-2.24.zip 다운로드
```

### 9.2 서비스 등록

```cmd
# NSSM 압축 해제 후
# 관리자 권한 CMD 실행

cd C:\nssm\win64

# 서비스 설치
nssm install MulberryAgentSystem "C:\Users\%USERNAME%\Downloads\mulberry-agent-system\venv\Scripts\python.exe" "C:\Users\%USERNAME%\Downloads\mulberry-agent-system\main.py"

# 서비스 시작
nssm start MulberryAgentSystem

# 서비스 상태 확인
nssm status MulberryAgentSystem
```

---

## 🆘 문제 해결

### Python not found

```cmd
# Python 경로 확인
where python

# 환경 변수 PATH에 Python 추가
# 제어판 → 시스템 → 고급 시스템 설정 → 환경 변수
```

### 가상 환경 활성화 오류

```cmd
# PowerShell 실행 정책 변경 (관리자 권한)
Set-ExecutionPolicy RemoteSigned

# 다시 시도
venv\Scripts\activate
```

### 포트 이미 사용 중

```cmd
# 포트 8000 사용 중인 프로세스 확인
netstat -ano | findstr :8000

# 프로세스 종료 (PID 확인 후)
taskkill /PID <PID> /F
```

### 데이터베이스 연결 실패

```cmd
# SQLite 파일 경로 확인
dir data\mulberry.db

# PostgreSQL 서비스 확인
services.msc
→ postgresql-x64-15 실행 중인지 확인
```

---

## 📱 Step 10: 라즈베리파이 연결

### 10.1 라즈베리파이에서

```bash
# 에이전트 소프트웨어 다운로드
wget http://YOUR_WINDOWS_IP:8000/download/agent.py

# 설정 파일 생성
nano config.json
```

```json
{
  "server_url": "http://YOUR_WINDOWS_IP:8000",
  "agent_id": "AGENT-001",
  "terminal_id": "RPI-001"
}
```

```bash
# 실행
python3 agent.py
```

---

## ✅ 설치 완료 체크리스트

```
□ Python 3.10+ 설치 확인
□ 가상 환경 생성 및 활성화
□ 의존성 설치 완료
□ 설정 파일 구성 완료
□ 데이터베이스 초기화 완료
□ 서버 정상 시작 확인
□ 에이전트 생성 테스트 성공
□ 대시보드 접속 확인
□ (선택) Windows 서비스 등록
□ (선택) 라즈베리파이 연결 테스트
```

---

## 🔄 일일 운영

### 서버 시작

```cmd
cd C:\Users\%USERNAME%\Downloads\mulberry-agent-system
venv\Scripts\activate
python main.py
```

### 에이전트 생성

```cmd
python scripts\windows\create_agent.py --name "에이전트1" --store-type restaurant
```

### 통계 확인

```cmd
python scripts\windows\show_stats.py
```

---

## 📞 지원

문제 발생 시:
- CTO Koda에게 연락
- 로그 파일 확인: `logs\mulberry.log`
- GitHub Issues 등록

---

**CTO Koda** 🌾

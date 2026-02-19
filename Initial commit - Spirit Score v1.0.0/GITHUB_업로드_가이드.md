# 🚀 GitHub 업로드 가이드

CTO Koda

---

## 📦 준비된 파일

**2개의 압축 파일이 준비되었습니다:**

### 1. `spirit-score-v1.0.0.tar.gz` (23KB)
- Linux/Mac 표준 포맷
- 더 작은 용량
- 권한 정보 보존

### 2. `spirit-score-v1.0.0.zip` (32KB)
- Windows 호환
- GUI 더블클릭 압축 해제 가능

---

## 🎯 GitHub 업로드 방법

### Option 1: GitHub 웹 인터페이스 (가장 쉬움)

#### 1단계: 새 저장소 생성

```
1. GitHub.com 로그인
2. 우측 상단 "+" → "New repository"
3. 저장소 이름: spirit-score
4. 설명: "Mulberry Spirit Score 자동화 시스템"
5. Private 선택 (내부 사용)
6. "Create repository" 클릭
```

#### 2단계: 압축 파일 업로드

```
1. 다운로드한 zip 파일 압축 해제
2. GitHub 저장소 페이지에서 "uploading an existing file" 클릭
3. 압축 해제된 폴더 내 모든 파일 드래그 앤 드롭
4. Commit message: "Initial commit - Spirit Score v1.0.0"
5. "Commit changes" 클릭
```

**⚠️ 주의**: 폴더가 아닌 **폴더 안의 파일들**을 업로드하세요!

---

### Option 2: Git CLI (추천 - 프로 방식)

#### 1단계: 압축 해제

```bash
# tar.gz 사용 (Linux/Mac)
tar -xzf spirit-score-v1.0.0.tar.gz
cd spirit-score

# 또는 zip 사용 (Windows)
unzip spirit-score-v1.0.0.zip
cd spirit-score
```

#### 2단계: GitHub 저장소 생성

```bash
# GitHub에서 저장소 생성 (웹에서)
# 또는 gh CLI 사용:
gh repo create mulberry-project/spirit-score --private
```

#### 3단계: Git 초기화 및 업로드

```bash
# Git 초기화
git init

# 원격 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/spirit-score.git

# 브랜치 이름 설정
git branch -M main

# 파일 추가
git add .

# 커밋
git commit -m "🎉 Initial commit - Spirit Score v1.0.0"

# 푸시
git push -u origin main
```

---

## ✅ 업로드 후 확인사항

### 1. 파일 구조 확인

GitHub에서 다음 구조가 보여야 합니다:

```
spirit-score/
├── .github/workflows/ci.yml
├── database/db_schema.sql
├── docs/INSTALL.md
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── activity_tracker.py
│   ├── spirit_score_engine.py
│   └── realtime_updates.py
├── tests/
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── README.md
└── requirements.txt
```

### 2. README 렌더링 확인

- GitHub 저장소 메인 페이지에서 README.md가 보기 좋게 렌더링되는지 확인
- 배지(badges)가 표시되는지 확인

### 3. GitHub Actions 확인

- "Actions" 탭 클릭
- CI/CD 파이프라인이 설정되어 있는지 확인

---

## 🔐 .env 파일 설정

**중요**: GitHub에 `.env` 파일을 업로드하면 안 됩니다!

```bash
# 로컬에서만 설정
cp .env.example .env

# .env 파일 편집
nano .env  # 또는 원하는 에디터

# Git이 무시하는지 확인
cat .gitignore | grep .env
```

`.gitignore`에 `.env`가 포함되어 있어 자동으로 무시됩니다.

---

## 🚀 팀원 초대

### 1. 저장소 설정

```
Settings → Collaborators → Add people
```

### 2. 권한 설정

- **Admin**: 대표님, PM
- **Write**: CTO Koda, Malu 수석
- **Read**: 기타 팀원

---

## 📱 클론 및 실행 (팀원용)

팀원들이 사용할 수 있는 명령어:

```bash
# 1. 저장소 클론
git clone https://github.com/YOUR_USERNAME/spirit-score.git
cd spirit-score

# 2. 환경 설정
cp .env.example .env
# .env 파일 편집

# 3. Docker로 실행
docker-compose up -d

# 4. API 확인
open http://localhost:8000/docs
```

---

## 🎨 GitHub 저장소 꾸미기

### About 섹션 설정

```
Settings → About

Description: 장승배기 정신을 코드로 구현한 Spirit Score 자동화 시스템
Website: http://mulberry.team
Topics: python, fastapi, postgresql, redis, automation
```

### README 배지 추가

이미 README.md에 포함되어 있습니다:
- Python 버전
- 라이선스
- 코드 스타일
- 테스트 상태

---

## 📊 GitHub Features 활용

### 1. Issues 활성화
```
Settings → Features → Issues ✅
```

### 2. Projects 활성화
```
Settings → Features → Projects ✅
```

### 3. Wiki 활성화 (선택사항)
```
Settings → Features → Wiki ✅
```

---

## 🔄 지속적인 업데이트

### 새로운 기능 추가 시

```bash
# 브랜치 생성
git checkout -b feature/new-feature

# 작업 후 커밋
git add .
git commit -m "feat: Add new feature"

# 푸시
git push origin feature/new-feature

# GitHub에서 Pull Request 생성
```

### 버전 태그

```bash
# 태그 생성
git tag -a v1.0.1 -m "Release v1.0.1"

# 태그 푸시
git push origin v1.0.1
```

---

## ⚠️ 주의사항

### 업로드하면 안 되는 것

- ❌ `.env` 파일 (비밀번호, API 키 포함)
- ❌ `__pycache__/` 폴더
- ❌ `.pyc` 파일
- ❌ 로그 파일
- ❌ 데이터베이스 파일

이미 `.gitignore`에 설정되어 있어 자동으로 무시됩니다!

---

## 💡 Tips

### 빠른 확인

```bash
# 어떤 파일이 커밋될지 확인
git status

# 무시되는 파일 확인
git status --ignored
```

### 실수로 업로드한 경우

```bash
# 파일 삭제 (Git에서만)
git rm --cached .env

# 커밋 및 푸시
git commit -m "Remove .env file"
git push
```

---

## 🎉 완료!

GitHub 저장소가 준비되었습니다!

**다음 단계:**
1. ✅ 팀원 초대
2. ✅ README 확인
3. ✅ CI/CD 설정 확인
4. ✅ 첫 이슈 생성
5. ✅ 개발 시작!

---

**CTO Koda** 🌾

**P.S.** 문제가 있으면 언제든 말씀하세요!

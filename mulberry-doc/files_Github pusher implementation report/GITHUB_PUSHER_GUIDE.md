# GitHub Auto-Pusher 사용 가이드

## 📋 개요

작업 완료 후 GitHub에 자동으로 커밋 & 푸시하는 스크립트입니다.

---

## 🚀 설치

### 1. 의존성 설치

```bash
pip install -r requirements.txt --break-system-packages
```

### 2. .env 파일 설정 확인

`.env` 파일이 프로젝트 루트에 있어야 합니다:

```env
GITHUB_TOKEN=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
GITHUB_REPO=wooriapt79/mulberry-
GITHUB_BRANCH=main
GITHUB_USER_NAME=Koda CTO
GITHUB_USER_EMAIL=cto@mulberry.io
```

**⚠️ 중요:** `.env` 파일은 절대 GitHub에 커밋하지 마세요!  
→ `.gitignore`에 이미 추가되어 있습니다.

---

## 💻 사용법

### 기본 사용

```bash
python scripts/github_pusher.py "작업 내용 요약"
```

### 예시

```bash
# Abstract 완성 후
python scripts/github_pusher.py "Abstract 두 버전 완성 (arXiv + Google)"

# 논문 섹션 작성 후
python scripts/github_pusher.py "Introduction 섹션 초안 작성"

# 코드 수정 후
python scripts/github_pusher.py "GitHub pusher 스크립트 구현"

# 데이터 시각화 후
python scripts/github_pusher.py "Figure 2-5 생성 완료"
```

---

## 📊 실행 프로세스

스크립트는 다음 순서로 실행됩니다:

```
1. Git 설정 (user.name, user.email)
   ↓
2. 변경사항 확인 (git status)
   ↓
3. 모든 파일 추가 (git add .)
   ↓
4. 커밋 메시지 자동 생성
   ↓
5. 커밋 (git commit)
   ↓
6. GitHub 푸시 (git push)
   ↓
7. 완료 메시지
```

---

## 📝 커밋 메시지 형식

자동으로 다음 형식의 커밋 메시지가 생성됩니다:

```
[2026-02-28] Abstract 두 버전 완성

📅 Date: 2026-02-28 15:30
👤 Author: Koda CTO
🌾 Mulberry Project - CTO Koda

Changes:
- Abstract 두 버전 완성

#mulberry #논문 #arXiv #학술연구
```

---

## ✅ 성공 확인

### 터미널 출력

```
============================================================
🚀 Mulberry GitHub Auto-Pusher
============================================================
✅ Git 설정 완료: Koda CTO <cto@mulberry.io>
📝 변경된 파일:
M  scripts/github_pusher.py
A  requirements.txt

✅ 모든 파일 추가 완료 (git add .)

📝 커밋 메시지:
------------------------------------------------------------
[2026-02-28] 테스트 커밋
...
------------------------------------------------------------
✅ 커밋 생성 완료
✅ GitHub 푸시 완료: main 브랜치
🔗 Repository: https://github.com/wooriapt79/mulberry-

============================================================
✅ GitHub 푸시 완료!
============================================================

✅ 작업 완료! 대표님께 보고하세요.
```

### GitHub에서 확인

1. https://github.com/wooriapt79/mulberry- 접속
2. 최신 커밋 확인
3. 커밋 메시지 및 변경사항 확인

---

## ⚠️ 문제 해결

### 1. "GITHUB_TOKEN이 .env 파일에 없습니다!"

**해결:**
- `.env` 파일이 프로젝트 루트에 있는지 확인
- `GITHUB_TOKEN` 값이 올바른지 확인

### 2. "Permission denied"

**해결:**
```bash
chmod +x scripts/github_pusher.py
```

### 3. "git push 실패"

**해결:**
- GitHub 토큰이 유효한지 확인
- 리포지토리 권한이 있는지 확인
- 브랜치 이름이 올바른지 확인

### 4. "python-dotenv 모듈 없음"

**해결:**
```bash
pip install python-dotenv --break-system-packages
```

---

## 🔒 보안 주의사항

### ❌ 절대 하지 말 것

1. `.env` 파일을 GitHub에 커밋
2. 토큰을 코드에 직접 작성
3. 토큰을 채팅/이메일로 공유
4. 스크린샷에 토큰 노출

### ✅ 반드시 할 것

1. `.gitignore`에 `.env` 추가 (이미 되어 있음)
2. 토큰은 `.env`에만 저장
3. 정기적으로 토큰 갱신
4. 토큰 유출 시 즉시 revoke

---

## 📁 파일 구조

```
mulberry-/
├── .env                    # GitHub 토큰 (보안!)
├── .gitignore             # .env 제외
├── requirements.txt       # 의존성
├── scripts/
│   └── github_pusher.py  # 메인 스크립트
└── GITHUB_PUSHER_GUIDE.md # 이 파일
```

---

## 🎯 워크플로우 예시

### 일반적인 작업 흐름

```bash
# 1. 작업 수행
vim paper_introduction.md

# 2. 테스트
python test_introduction.py

# 3. GitHub 푸시
python scripts/github_pusher.py "Introduction 섹션 초안 작성"

# 4. 대표님께 보고
# Slack/이메일로 완료 보고
```

---

## 🆘 도움이 필요하면

### 스크립트 도움말

```bash
python scripts/github_pusher.py
# → 사용법 출력
```

### 문의

- CTO Koda
- GitHub Issues: https://github.com/wooriapt79/mulberry-/issues

---

## 📚 참고 자료

- GitHub PAT 문서: https://docs.github.com/en/authentication
- python-dotenv: https://pypi.org/project/python-dotenv/
- Git 기본 사용법: https://git-scm.com/docs

---

**Happy Pushing! 🚀**

**CTO Koda 🌾**

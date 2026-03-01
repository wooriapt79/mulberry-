# GitHub Auto-Pusher 사용 가이드

## 개요
작업 완료 후 GitHub에 자동으로 커밋 & 푸시하는 스크립트입니다.

## 설치

1. 의존성 설치
pip install -r scripts/requirements.txt --break-system-packages

2. .env 파일 설정 (프로젝트 루트에 생성)
GITHUB_TOKEN=YOUR_TOKEN
GITHUB_REPO=wooriapt79/mulberry-
GITHUB_BRANCH=main
GITHUB_USER_NAME=Koda CTO
GITHUB_USER_EMAIL=cto@mulberry.io

## 사용법

python scripts/github_pusher.py "작업 내용 요약"

## 예시

python scripts/github_pusher.py "Abstract 두 버전 완성"
python scripts/github_pusher.py "Introduction 섹션 작성"
python scripts/github_pusher.py "코드 수정 완료"

## 실행 순서

1. Git 설정
2. 변경사항 확인 (git status)
3. 파일 추가 (git add .)
4. 커밋 메시지 자동 생성
5. 커밋 & 푸시
6. 완료 보고

## 보안 주의사항

- .env 파일 절대 GitHub에 커밋 금지
- 토큰은 .env에만 저장
- .gitignore에 .env 포함 확인

CTO Koda 🌾
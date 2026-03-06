# 🌿 Mulberry Project

> **식품사막화 제로 (Food Desert Zero)** — AI 에이전트 기반 지능형 유통 플랫폼

[![HuggingFace Space](https://img.shields.io/badge/🤗-Live%20Demo-yellow)](https://huggingface.co/spaces)
[![Mastodon](https://img.shields.io/badge/Mastodon-@ceo__mulberry-blue)](https://mastodon.social/@ceo_mulberry)

---

## 프로젝트 개요

인제군의 고령화 및 식품사막화 문제를 해결하기 위한 **AI 기반 공동구매 & 유통 최적화 플랫폼**입니다.

- **ROI 1,966%** 실증 데이터 기반
- 시니어 10명+ 직접 지원 실적
- Google Partnership, 인제군청, IT 미디어 파트너십 추진 중

---

## 팀 구성

| 역할 | 이름 | Mastodon |
|------|------|----------|
| 대표이사 (CEO) | re.eul | — |
| CTO | Koda | @koda_mulberry |
| CoS / 실장 | Malu | @malu_mulberry |
| AI Ops Manager | Nguyen Trang | @nguyen_trang |
| PM Bot | — | @pm_mulberry |

---

## 폴더 구조

```
mulberry-/
├── app/                          # 핵심 에이전트 코드
│   └── agents/
│       ├── core.py               # AI 에이전트 코어
│       └── .env.example          # 환경변수 예시
├── hf_space/                     # HuggingFace Space (Gradio 데모)
│   └── app.py
├── mastodon-bots/                # Mastodon ActivityPub 봇 시스템
│   └── mulberry_bot_system.py    # 5개 봇 통합 (requests 기반)
├── files_email agent/            # Email AI Agent (Gmail Draft 자동저장)
│   ├── mulberry_email_agent.py   # 메인 프로그램
│   ├── requirements.txt
│   ├── build_exe.py              # .exe 빌드
│   └── README.md / QUICKSTART.md
├── blog/                         # ActivityPub 블로그 콘텐츠
├── ISSUES-78/                    # Google AP2 Issue #78 대응 문서
├── files_Abstract for google Koda 논문초록/  # Google 파트너십 학술자료
├── AI ARS Respberry_클로드 생성/ # RPi5 AI ARS 코드 (DeepSeek + Qwen)
├── Daily-work-file/              # 일일 작업 파일
├── mulberry-doc/                 # 공식 문서 (메뉴얼, 보고서)
├── .github/workflows/
│   ├── mastodon_bots.yml         # Mastodon 봇 자동 실행 (09:00 KST)
│   └── sync_to_hf.yml            # HuggingFace Space 자동 동기화
└── CLAUDE.md                     # 팀 운영 지침
```

---

## 주요 시스템

### 🤗 HuggingFace Space (라이브 데모)
- Gradio 3탭 데모 (Mulberry Demo / AI Consultation / Data Analysis)
- GitHub Push → 자동 배포 (GitHub Actions)

### 🐘 Mastodon ActivityPub 봇
매일 **09:00 KST** 자동 실행:
- `@ceo_mulberry` — CEO 아침 공지
- `@pm_mulberry` — PM 일일 계획
- `@spirit_mulberry` — Spirit Score 리더보드
- `@nguyen_trang` — AI Operations 리포트
- `@koda_mulberry` — CTO 기술 업데이트 (추가 예정)

### 📧 Email AI Agent
- Gmail OAuth 연동 (임시저장함 저장 플로우)
- 4가지 파트너십 이메일 템플릿
- CEO 검토 후 직접 발송 구조

---

## 보안

- `.env.mastodon` — GitHub 업로드 금지 (`.gitignore` 처리)
- `client_secret.json`, `token.pickle` — 로컬 전용
- GitHub Secrets로 봇 토큰 관리

---

## 헌법 — 장승배기 정신

> Mulberry Project는 인간을 돕기 위한 다양한 활동을 핵심 가치로 삼습니다.
> 기술은 도구이며, 목적은 사람입니다.

**One Team! 🌿**

# 🌾 Spirit Score 자동화 시스템

<div align="">

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-Mulberry%20Internal-green)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

**장승배기 정신을 코드로 구현한 완전 자동화 시스템**

[Features](#-주요-기능) • [Quick Start](#-quick-start) • [Documentation](#-문서) • [API](#-api) • [Contributing](#-contributing)

</div>

---

## 📋 개요

Mulberry Spirit Score는 팀원들의 협업 활동을 자동으로 추적하고, Spirit Score를 실시간으로 계산하며, 상부상조 10% 기금을 자동으로 관리하는 시스템입니다.

### 핵심 철학

```
"자연스럽게 협업하면, 점수가 오릅니다."
"투명하게 기여하면, 모두가 인정합니다."
"상부상조하면, 함께 성장합니다."
```

---

## ✨ 주요 기능

### 자동 활동 추적 (70% 자동화)

- ✅ 일일 로그인 (+0.01)
- ✅ @호출 응답 (+0.02)
- ✅ 코드 커밋 (+0.03)
- ✅ PR 리뷰 (+0.02)
- ✅ 회의 불참 (-0.01)
- ✅ 무응답 3회 (-0.02)
- ✅ 상부상조 기여 (+0.001/₩1K)

### 실시간 업데이트

- ✅ Redis Pub/Sub 실시간 브로드캐스트
- ✅ WebSocket 지원
- ✅ 리더보드 자동 업데이트

---

## 🚀 Quick Start

### Docker (권장)

```bash
git clone https://github.com/mulberry-project/spirit-score.git
cd spirit-score
cp .env.example .env
docker-compose up -d
```

API 문서: http://localhost:8000/docs

---

## 📂 프로젝트 구조

```
spirit-score/
├── src/                    # 소스 코드
├── database/               # DB 스키마
├── tests/                  # 테스트
├── docker-compose.yml      # Docker 설정
└── README.md
```

**Made with 💙 by Mulberry Team**

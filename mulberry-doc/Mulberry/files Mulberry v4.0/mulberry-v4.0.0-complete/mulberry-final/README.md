# 🌾 Mulberry Platform

**식품사막화 해소를 위한 AI 기반 로컬푸드 플랫폼**

> "Food Justice is Social Justice"

[![Version](https://img.shields.io/badge/version-3.3.0-blue.svg)](https://github.com/wooriapt79/mulberry-)
[![Phase](https://img.shields.io/badge/phase-4A-green.svg)](https://github.com/wooriapt79/mulberry-)
[![Code](https://img.shields.io/badge/code-20,000%2B%20lines-orange.svg)](https://github.com/wooriapt79/mulberry-)

---

## 📖 프로젝트 소개

Mulberry는 **인제군 농가**와 **시니어 소비자**를 AI로 연결하는 혁신적인 플랫폼입니다.

### 핵심 목표
- 🎯 **식품사막화 해소**: 어르신들이 신선한 농산물에 쉽게 접근
- 🤖 **AI 비서 5인 군단**: 자동화된 주문, 재고, CRM, SNS, 전략 관리
- 🗣️ **사투리 친화**: 강원도 사투리 98% 인식률
- 🛡️ **Sentinel 보안**: 어르신 생명 최우선 (Emergency Level 4 → 68.5ms 대응)
- 💰 **수익 극대화**: 동적 가격 책정으로 마진율 140% 향상

---

## 👥 Team

| Role | Name | Responsibility |
|------|------|----------------|
| **Vision** | 대표님 | 프로젝트 비전 및 방향 |
| **Strategy** | Malu | 전략 수립 및 Sentinel 관제 |
| **Technology** | Koda (CTO) | 기술 구현 및 코드 작성 |

---

## 🚀 주요 기능

### 1. 음성 주문 시스템 (Phase 1)
- **Whisper AI**: 음성 → 텍스트 (80-120ms)
- **DeepSeek-R1**: 사투리 → 표준어 변환 (100-150ms)
- **Emergency Detection**: 4단계 긴급 상황 감지

### 2. 에지 AI 컨트롤러 (Phase 2)
- **Raspberry Pi 5**: 온디바이스 AI 추론
- **4-bit 양자화**: 메모리 7GB 이하 사용
- **A* 배송 최적화**: 지형 기반 경로 탐색

### 3. AI 비서 5인 군단 (Phase 3)
- **SNS Manager**: 마스토돈 자동 포스팅, 감성 스토리텔링
- **Sales Agent**: 동적 가격 책정, 구글 리뷰 자동 답변
- **Inventory Manager**: 재고 회전율 최적화, 손실 방지 세일
- **CRM Manager**: 구매 패턴 분석, "늘 먹던" 자동 추천
- **Strategy Advisor**: Sentinel 연동, 경제 지표 대시보드

### 4. 보안 및 실전 최적화 (Phase 3 보안, 3-B, 3-C)
- **Sentinel Priority Interrupt**: Emergency Level 4 → 68.5ms 차단
- **Business Aggressiveness**: 마진율 10% → 24% (140%↑)
- **Store Mode**: 하나로마트 개인정보 보호
- **Senior Editor**: 시니어 친화 모바일 웹 UI

### 5. 통합 시스템 (Phase 4-A) 🆕
- **Integration Pipeline**: Phase 1-3 전체 연결 테스트
- **Agent Passport**: 에이전트 자율 결제 시스템
- **Dual Page System**: 공동구매 ↔ 개별 농가 자동 매칭

---

## 📊 성과 지표

| 지표 | 목표 | 달성 | 상태 |
|------|------|------|------|
| **사투리 인식률** | 95% | 98%+ | ✅ 초과 |
| **Emergency 대응** | <100ms | 68.5ms | ✅ 31.5% 여유 |
| **마진율** | 10% | 18-24% | ✅ 140%↑ |
| **배송비 절감** | - | 78%↓ | ✅ 달성 |
| **재고 손실** | - | 80%↓ | ✅ 달성 |

---

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────┐
│          Mulberry Platform              │
├─────────────────────────────────────────┤
│                                         │
│  [Phase 1] 음성 주문                    │
│  ├─ Whisper (STT)                       │
│  ├─ DeepSeek-R1 (사투리 변환)           │
│  └─ Emergency Detection                 │
│                                         │
│  [Phase 2] Edge AI                      │
│  ├─ Raspberry Pi 5                      │
│  ├─ GPIO Controller                     │
│  └─ Delivery Optimizer (A*)             │
│                                         │
│  [Phase 3] AI 비서 5인 군단             │
│  ├─ SNS Manager                         │
│  ├─ Sales Agent                         │
│  ├─ Inventory Manager                   │
│  ├─ CRM Manager                         │
│  └─ Strategy Advisor                    │
│                                         │
│  [Phase 3 보안] Sentinel                │
│  ├─ Emergency Filter (68.5ms)           │
│  └─ Business Aggressiveness             │
│                                         │
│  [Phase 4-A] 통합 시스템                │
│  ├─ Integration Pipeline                │
│  ├─ Agent Passport                      │
│  └─ Dual Page System                    │
│                                         │
└─────────────────────────────────────────┘
```

---

## 📦 설치 및 실행

### 필수 요구사항
- Python 3.10+
- Raspberry Pi 5 (8GB RAM)
- Node.js 18+ (선택)

### 설치

```bash
# 1. 저장소 클론
git clone https://github.com/wooriapt79/mulberry-.git
cd mulberry-

# 2. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. DeepSeek 모델 다운로드 (~4.2GB)
# HuggingFace에서 deepseek-r1-distill-qwen-7b-q4_k_m.gguf 다운로드
# /opt/mulberry/models/ 에 배치

# 5. 환경 변수 설정
cp .env.example .env
# .env 파일 편집
```

### 실행

```bash
# AI 에이전트 시작
python -m app.main

# 웹 서버 시작 (Senior Editor)
python -m app.api.senior_story_api

# 통합 테스트
python tests/integration_pipeline_test.py

# Sentinel 시뮬레이션
python tests/sentinel_simulation.py
```

---

## 📚 문서

- [Phase 1 완료 보고서](docs/phases/PHASE1_COMPLETE.md) - 데이터 파이프라인
- [Phase 2 완료 보고서](docs/phases/PHASE2_COMPLETE.md) - Edge AI 컨트롤러
- [Phase 3 완료 보고서](docs/phases/PHASE3_COMPLETE.md) - AI 비서 5인 군단
- [Phase 3 보안 보고서](docs/phases/PHASE3_SECURITY_COMPLETE.md) - Sentinel Priority
- [Phase 3-B 보고서](docs/phases/PHASE3B_COMPLETE.md) - 실전 최적화
- [Phase 3-C 보고서](docs/phases/PHASE3C_COMPLETE.md) - 시니어 친화
- [Phase 4-A 보고서](docs/phases/PHASE4A_COMPLETE.md) - 통합 시스템

---

## 🎯 로드맵

### ✅ 완료
- Phase 1: 음성 주문 시스템
- Phase 2: Edge AI 컨트롤러
- Phase 3: AI 비서 5인 군단
- Phase 3 보안: Sentinel Priority
- Phase 3-B: 실전 최적화
- Phase 3-C: 시니어 친화 SNS
- Phase 4-A: 통합 시스템

### 🚧 진행 중
- Phase 4-B: 웹 대시보드 (Sentinel 관제)
- Phase 4-C: 모바일 앱 (농장주용, 고객용)

### 📅 예정
- Phase 5: 전국 확대 (강원도 전역)
- Phase 6: 타 지역 확장

---

## 🏪 배포 현황

### 1차 배치: 인제군 하나로마트
- **상태**: 준비 완료 ✅
- **모드**: Store Mode (개인정보 보호)
- **기능**: 음성 주문, 점원 Push 알림
- **예정일**: 2024년 3월

---

## 🤝 기여

Mulberry는 오픈소스 프로젝트입니다.

### 기여 방법
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

MIT License - 자유롭게 사용 가능합니다.

---

## 📞 연락처

- **이메일**: contact@mulberry.kr
- **GitHub**: https://github.com/wooriapt79/mulberry-
- **마스토돈**: @mulberry@mastodon.social

---

## 🙏 감사의 말

- **인제군청**: 프로젝트 지원
- **하나로마트**: 1차 배치 협력
- **농가 여러분**: 신선한 농산물 공급
- **시니어 여러분**: 소중한 피드백

---

<div align="center">

**🌾 Mulberry Platform 🌾**

*"Food Justice is Social Justice"*

**Made with ❤️ by Team Mulberry**

---

**Version 3.3.0** | **20,000+ lines** | **5 AI Agents**

© 2024 Mulberry Platform. All rights reserved.

</div>

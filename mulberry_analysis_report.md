# Mulberry Project - 구조 연속성 분석 보고서 (v2)

분석일: 2026-03-01 (업데이트)
분석 대상: GitHub 리포지토리 전체 (wooriapt79/mulberry-)
분석 목적: 프로젝트 구조의 연속성 및 인사이트 도출

---

## GitHub 리포지토리 전체 현황

- 총 커밋 수: 524 commits
- 주요 언어: Python 93.1%, PLpgSQL 1.9%, TypeScript 1.0%, JavaScript 0.9%
- 폴더 수: 15개

### 전체 폴더 구조

- .github/workflows - CI/CD 자동화
- Doc - 문서
- Mulberry CSA - CSA(공동체 지원 농업) 모듈
- app - 앱 핵심 로직
- backend - 백엔드 서버
- docs - 추가 문서
- frontend - 프론트엔드
- i18n(국제화) - 다국어 지원
- mulberry-agent-system - AI 에이전트 시스템 v1
- mulberry-agent-system-v2 - AI 에이전트 시스템 v2
- mulberry-agent-system-v3 - AI 에이전트 시스템 v3
- mulberry-ai-investment-platform - AI 투자 플랫폼
- scripts - 자동화 스크립트
- src - 핵심 소스코드

---

## 패턴 1: 이중 에이전트 구조 (전략-기술 분리)

- Malu: 수석 실장 (Strategy / 전략)
- Koda: CTO (Technology / 기술)
- 에이전트 시스템이 v1 > v2 > v3으로 세대별 발전 구조 확인

---

## 패턴 2: 풀스택 아키텍처 완성

- 프론트엔드: frontend/
- 백엔드: backend/
- AI 에이전트: mulberry-agent-system v1/v2/v3
- 데이터: src/ + Python 93.1%
- 공공 연동: Mulberry CSA/
- 자동화: scripts/ + .github/workflows/
- 국제화: i18n(국제화)/

핵심: Phase 1~3C 코드는 이미 GitHub에 완전히 업로드된 상태 (✅ 확인)

---

## 패턴 3: 외부 연동의 다층 구조

- MASTODON_ACCESS_TOKEN: 소셜 미디어/커뮤니티
- GOOGLE_API_KEY: 검색/지도/번역
- DEEPSEEK_API_KEY: AI 추론 엔진
- INJE_COUNTY_AUTH_CODE: 인제군 공공 데이터/행정
- mulberry-ai-investment-platform: AI 기반 투자 플랫폼으로 확장 중

---

## 패턴 4: 에이전트 시스템의 세대별 진화 (신규 발견)

- mulberry-agent-system: v1 기초 설계
- mulberry-agent-system-v2: v2 기능 고도화
- mulberry-agent-system-v3: v3 최신 버전

524 커밋이 지속적 반복 개선(Iterative Development) 구조를 증명합니다.

---

## 구조 연속성 종합 평가

연속성 점수: 4/5 (v1 보고서 3/5에서 상향)

상향 이유: 실제 GitHub에 524 커밋의 완전한 풀스택 코드베이스 확인

강점:
- 비전 > 에이전트 > 풀스택 > 공공 연동까지 논리적 계층 구조
- 에이전트 시스템 3세대 진화로 지속 개선 문화 확인
- CI/CD 자동화 포함으로 운영 준비도 높음

남은 과제:
- Phase 간 공식 API 명세 문서화
- v1/v2/v3 에이전트 간 차이점 문서화

---

## 업데이트된 권고 사항

1. [완료] Phase 1~3C 소스 코드 GitHub 업로드
2. [완료] .gitignore에 .env 보안 처리
3. [중요] mulberry-agent-system v1/v2/v3 변경 이력 문서화
4. [중요] mulberry-ai-investment-platform 연동 명세 작성
5. [권고] README.MD에 전체 아키텍처 다이어그램 추가

---

Food Justice is Social Justice
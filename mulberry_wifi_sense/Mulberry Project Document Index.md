# 📑 Mulberry Project Document Index

이 노트북에 작성된 주요 기술 문서 및 가이드라인 인덱스입니다. 각 항목을 클릭하면 해당 섹션으로 이동합니다.

---

## 1. 프로젝트 개요 및 아키텍처

* [🏗️ WiFi Sensing & mHC 통합 아키텍처 설계](#integrated_architecture_design): 계층별 구조 및 DeepSeek V4 기반 mHC 연동 로직 설명
* [📋 프로젝트 요약 및 핵심 기능](#readme_markdown_final): 전체 시스템 구성 및 모듈별 역할 정의

## 2. 연동 가이드 및 데이터 규격

* [📜 WiFi Sensing 통합 연동 가이드](#unified_integration_guide): mHC 시스템과의 데이터 규격(JSON) 및 보안 정책 통합 안내
* [🔗 실제 mHC API 연동 전략](#actual_mhc_api_strategy): Mock API에서 실제 서버로 전환하기 위한 상세 전략

## 3. 설치 및 운영 가이드

* [🏠 댁 내 라즈베리 파이 설치 가이드](#rpi_home_installation_guide): 시니어 댁내 하드웨어 설치 및 Nexmon 패치 절차
* [🐳 GCP 배포 및 DevOps 전략](#guide_book_markdown): Docker 컨테이너화 및 Cloud Run 배포 자동화 방안

## 4. 모니터링 및 보안

* [📊 통합 모니터링 대시보드](#dashboard_implementation_section): Dash/Plotly 기반 실시간 지표 시각화 및 최근 이벤트 로그
* [🔐 보안 강화 및 민감 데이터 관리](#security_enhancement_details): API Key 보안 주입 및 생체 정보 비식별화(Hashing) 처리

---

*참고: 각 섹션의 제목(Header)을 클릭하면 다시 이 인덱스로 돌아올 수 있도록 링크를 설정할 수 있습니다.*

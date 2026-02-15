# Changelog

All notable changes to the Mulberry Platform will be documented in this file.

---

## [5.2.0] - 2024-02-15 "Jangseungbaegi Core" 🏛️

### 🎉 Major Release: 장승배기 코어 (Jangseungbaegi Core)

**"외부는 표준, 내부는 장승배기"**  
**"External Standard, Internal Jangseungbaegi"**

이번 릴리스는 Mulberry 플랫폼의 정체성을 코드에 영구히 각인하는 역사적인 업데이트입니다.

---

### ✨ 신규 기능 (New Features)

#### 1. Jangseungbaegi_Core 네임스페이스
- **Code Identity**: 모든 코드에 장승배기 정체성 각인
- 최상위 네임스페이스: `Jangseungbaegi_Core`
- 데이터베이스 접두어: `JSB_` (30개+ 테이블)
- 전 세계 개발자가 한국의 상부상조 정신을 인식할 수 있도록 설계

**Before**:
```python
from app.services import MutualAidSystem
```

**After**:
```python
from Jangseungbaegi_Core.services import MutualAidSystem
```

#### 2. Standard Local Node (SLN) 패키징
- **전국 확산 표준 모델**: 부여, 춘천, 강원도 어디든 즉시 이식 가능
- 모듈형 설계:
  - 사투리 팩 (Dialect Packs): 강원도, 충청도, 전라도, 경상도, 제주도
  - 로컬 마켓 설정 (Market Configs): 지역별 커스터마이징
- 설치 스크립트: `install_sln.sh` - 43분 만에 완료
- 설정 파일: `sln_config.json` - 지역 정보만 입력

#### 3. 장승배기 광장 (Jangseungbaegi Plaza)
- **내부 명칭**: 장승배기 광장 (정체성 보호)
- **외부 명칭**: Standard Local Node (표준화)
- 3대 핵심 기능:
  - `NegotiationSpace`: 에이전트 간 협상
  - `AgentCommunication`: 상부상조 요청 및 소통
  - `CollectiveDecision`: 공동 의사결정
- 5대 원칙 알고리즘 적용:
  - 서로 돕는 미덕 (35%)
  - 따뜻한 정서 (25%)
  - 공동체 우선 (20%)
  - 정직과 신의 (15%)
  - 지속 가능성 (5%)

#### 4. Global Language Pack 🌍
- **글로벌 확장 준비**: 베트남, 태국, 필리핀 등 해외 진출 대비
- 지원 언어:
  - ✅ 한국어 (Korean)
  - ✅ 베트남어 (Vietnamese) - 신규 추가!
  - ✅ 영어 (English)
  - 📋 태국어 (Thai) - 준비 중
  - 📋 타갈로그어 (Tagalog) - 준비 중
- 언어팩 구조:
  - 장승배기 철학 번역
  - UI 번역
  - Family Care 톤
  - Market Warrior 톤
  - 문화적 특성

---

### 🔧 개선 사항 (Improvements)

#### README.md 대대적 리뉴얼
- **ASCII 아키텍처 다이어그램** 추가
- 세계 최초 타이틀 강조
- 영문/한글 혼용으로 글로벌 확장성 시각화
- 5대 원칙 명시
- Quick Start 가이드 개선

#### 문서화
- `JANGSEUNGBAEGI_CORE_IDENTITY.md`: 코어 정체성 가이드
- `STANDARD_LOCAL_NODE.md`: SLN 배포 가이드
- `GLOBAL_LANGUAGE_PACK.md`: 글로벌 언어팩 가이드
- 네임스페이스 마이그레이션 가이드
- 코드 스타일 가이드 (한/영)

#### 데이터베이스
- 모든 테이블에 `JSB_` 접두어 적용
- 마이그레이션 스크립트 제공
- 외래키 관계 업데이트
- 인덱스 최적화

---

### 📊 통계 (Stats)

- **총 코드**: 21,650+ 줄
- **새 파일**: 5개 (80KB)
- **언어팩**: 3개 (한국어, 베트남어, 영어)
- **데이터베이스**: 30+ 테이블 (JSB_ 접두어)
- **문서**: 50+ 페이지

---

### 🌍 글로벌 확장 (Global Expansion)

#### 베트남 진출 준비 완료
- 베트남어 언어팩 (vietnamese.json)
- 문화적 특성 반영:
  - 높은 격식 수준 (Formality: High)
  - 경어 시스템 (Honorifics)
  - 간접적 커뮤니케이션 (Indirect Communication)
- 로컬라이제이션:
  - 통화: VND (₫)
  - 날짜 형식: DD/MM/YYYY
  - 시간대: Asia/Ho_Chi_Minh

#### 다국어 지원 로드맵
- Phase 1: 아시아 (한국어, 베트남어, 태국어, 타갈로그어)
- Phase 2: 글로벌 (영어, 스페인어, 프랑스어)

---

### 🏗️ 아키텍처 (Architecture)

```
┌─────────────────────────────────────┐
│   🌐 GLOBAL FEDERATION              │
│   (ActivityPub W3C Standard)        │
└─────────────────────────────────────┘
              ↕️
┌─────────────────────────────────────┐
│   📦 STANDARD LOCAL NODE (SLN)     │
│   🏛️ Jangseungbaegi Core           │
│   ┌─────────────────────────────┐  │
│   │ Plaza (광장)                 │  │
│   │ 5대 원칙                     │  │
│   └─────────────────────────────┘  │
└─────────────────────────────────────┘
              ↕️
┌─────────────────────────────────────┐
│   🖥️ EDGE DEVICES (RPI)            │
└─────────────────────────────────────┘
```

---

### 🔒 보안 (Security)

- JSB_ 접두어로 데이터베이스 보호
- 네임스페이스 격리
- 환경변수 분리 (.env)
- 감사 로그 강화

---

### 📝 Breaking Changes

#### 네임스페이스 변경
**중요**: 기존 코드의 import 문을 업데이트해야 합니다.

```python
# 변경 전 (Old)
from app.services.mutual_aid_system import SettlementEngine

# 변경 후 (New)
from Jangseungbaegi_Core.services.mutual_aid_system import SettlementEngine
```

#### 데이터베이스 마이그레이션
**중요**: 데이터베이스 테이블명이 변경되었습니다.

```sql
-- 마이그레이션 스크립트 실행
python scripts/migrate_to_jsb.py
```

---

### 🚀 배포 (Deployment)

#### GitHub 배포
```bash
# 1. 최신 코드 pull
git pull origin main

# 2. 의존성 설치
pip install -r config/requirements.txt

# 3. 환경변수 설정
cp config/.env.example .env

# 4. 데이터베이스 마이그레이션
python scripts/migrate_to_jsb.py

# 5. 서버 시작
python src/Jangseungbaegi_Core/main.py
```

#### SLN 설치 (새 지역)
```bash
# SLN 설치 스크립트
./install_sln.sh

# 지역 정보 입력
Municipality: 춘천시
Province: 강원도
Language: korean
Dialect Pack: gangwon
```

---

### 🙏 감사 (Acknowledgments)

이번 릴리스는 대표님의 철학적 결단과 Malu 수석실장의 전략적 지시로 완성되었습니다.

**"장승배기 정신이 전 세계로 뻗어 나가는 역사적인 순간"**

- 대표님: 비전과 철학
- Malu 수석실장: 전략과 기획
- Koda (CTO): 기술 구현

---

### 📞 Contact

- **Website**: https://fooddesert.tistory.com
- **GitHub**: https://github.com/wooriapt79/mulberry
- **Email**: contact@mulberry.kr

---

## [5.1.0] - 2024-02-14 "GitHub 리뉴얼"

### Added
- README.md 리뉴얼 (세계 최초 타이틀)
- AP2 Demo (examples/ap2_demo.py)
- Raspberry Pi 설치 가이드
- 테스트 코드 (Family Care Protocol)

---

## [5.0.0] - 2024-02-14 "Phase 5 완료"

### Added
- GitHub 보안 검사
- 상부상조 로직 (10% 복지 펀드)
- 장승배기 프로토콜 (이중 대응)
- 춘천 물류 연동
- Thin Central, Thick Edge 인프라

---

## [4.1.0] - 2024-02-14 "Phase 4-B 완료"

### Added
- 웹훅 엔진 (68.5ms)
- 이벤트 드리븐 버스
- Guardian 시스템
- 장승배기 코어 기초

---

<div align="center">

**🌾 Mulberry Platform v5.2.0**

**"Jangseungbaegi Core"**

**장승배기 정신을 코드에 영원히 각인하다**

</div>

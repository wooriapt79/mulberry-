# Mulberry Platform v5.2.0 Release Notes
## "Jangseungbaegi Core" 🏛️

**Release Date**: 2024-02-15  
**Code Name**: "Jangseungbaegi Core"

---

## 🎉 역사적인 릴리스

**"외부는 표준, 내부는 장승배기"**

이번 릴리스는 Mulberry 플랫폼의 정체성을 코드에 영구히 각인하는 역사적인 업데이트입니다.

---

## ✨ 주요 변경사항

### 1. Jangseungbaegi_Core 네임스페이스
- 전 세계 개발자가 한국의 상부상조 정신을 인식
- `from Jangseungbaegi_Core.services import ...`
- 데이터베이스: `JSB_` 접두어 (30개+ 테이블)

### 2. Standard Local Node (SLN)
- 전국 어디든 43분 만에 배포
- 모듈형 설계 (사투리 팩 + 로컬 마켓)
- `./install_sln.sh` 자동 설치

### 3. 장승배기 광장 (Plaza)
- 내부 명칭: 장승배기 광장
- 외부 명칭: Standard Local Node
- 5대 원칙 알고리즘 적용

### 4. Global Language Pack 🌍
- 베트남어 완전 지원
- 태국어, 타갈로그어 준비
- 글로벌 확장 준비 완료

---

## 📊 통계

- 총 코드: 21,650+ 줄
- 신규 파일: 7개
- 언어 지원: 3개 (한국어, 베트남어, 영어)
- 문서: 50+ 페이지

---

## 🚀 업그레이드 방법

```bash
# 1. 코드 업데이트
git pull origin main

# 2. 의존성 설치
pip install -r config/requirements.txt

# 3. 데이터베이스 마이그레이션
python scripts/migrate_to_jsb.py

# 4. 서버 재시작
python src/Jangseungbaegi_Core/main.py
```

---

## ⚠️ Breaking Changes

### Import 문 변경 필요
```python
# Old
from app.services import MutualAidSystem

# New
from Jangseungbaegi_Core.services import MutualAidSystem
```

---

**Full Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

**🌾 Mulberry Platform**  
**"장승배기 정신을 전 세계로"**

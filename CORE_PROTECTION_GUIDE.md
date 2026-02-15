# 🔒 Jangseungbaegi_Core Protection Guide
## 핵심 라이브러리 보호 및 SLN 분리 가이드

**목적**: 핵심 철학과 알고리즘 보호, SLN은 자유롭게 포크 가능

---

## 🏛️ Architecture: Protected Core + Open SLN

```
┌─────────────────────────────────────────────────────────────┐
│                    🔒 PROTECTED ZONE                         │
│         Jangseungbaegi_Core (Proprietary)                   │
│                                                              │
│  src/Jangseungbaegi_Core/                                   │
│  ├── plaza/                  # 협상 로직 (보호됨)           │
│  │   └── jangseungbaegi_plaza.py                           │
│  ├── services/               # 핵심 알고리즘 (보호됨)        │
│  │   ├── mutual_aid_system.py      # 상부상조 10%          │
│  │   └── jangseungbaegi_protocol.py  # 5대 원칙           │
│  └── models/                 # 데이터 모델 (보호됨)         │
│                                                              │
│  License: Proprietary                                       │
│  Fork: ❌ Not Allowed                                       │
│  Modify: ❌ Not Allowed                                     │
│  Use: ✅ Via API Only                                       │
└─────────────────────────────────────────────────────────────┘
                          ↕️ API Interface
┌─────────────────────────────────────────────────────────────┐
│                    ✅ OPEN ZONE                              │
│         Standard Local Node (MIT License)                   │
│                                                              │
│  sln_config.json             # ✅ Fork OK                    │
│  language_packs/             # ✅ Fork OK                    │
│  market_configs/             # ✅ Fork OK                    │
│  scripts/install_sln.sh      # ✅ Fork OK                    │
│  docs/                       # ✅ Fork OK                    │
│                                                              │
│  License: MIT                                               │
│  Fork: ✅ Freely                                            │
│  Modify: ✅ Freely                                          │
│  Commercial Use: ✅ Allowed                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔒 Protected: Jangseungbaegi_Core

### What is Protected

**Files:**
```
src/Jangseungbaegi_Core/
├── plaza/
│   ├── jangseungbaegi_plaza.py      # 🔒 협상 알고리즘
│   ├── negotiation_space.py         # 🔒 협상 공간
│   ├── agent_communication.py       # 🔒 에이전트 소통
│   └── decision_making.py           # 🔒 의사결정
├── services/
│   ├── mutual_aid_system.py         # 🔒 상부상조 로직
│   ├── jangseungbaegi_protocol.py   # 🔒 5대 원칙
│   ├── guardian_system.py           # 🔒 Guardian 알고리즘
│   └── agent_passport.py            # 🔒 AP2 위임장
└── models/
    ├── mandate.py                   # 🔒 위임장 모델
    └── schemas.py                   # 🔒 데이터 스키마
```

**Database:**
```sql
-- 🔒 Protected Tables (JSB_ prefix)
JSB_welfare_funds        # 복지 펀드
JSB_mutual_aid_records   # 상부상조 기록
JSB_plaza_negotiations   # 광장 협상
JSB_agent_mandates       # 위임장
```

### Why Protected?

**1. 철학적 무결성 (Philosophical Integrity)**
- 상부상조 10% 보장
- 5대 원칙 알고리즘 보호
- 장승배기 정신 유지

**2. 신뢰 보호 (Trust Protection)**
- 취약계층 보호
- 투명한 알고리즘
- 브랜드 신뢰

**3. 악용 방지 (Abuse Prevention)**
- 수수료 인상 방지 (10% 고정)
- 착취적 변형 방지
- 알고리즘 조작 방지

### How to Use Core

**Via API (Recommended):**
```python
from Jangseungbaegi_Core.api import CoreAPI

# Initialize with API key
api = CoreAPI(api_key="your_key")

# Use core functions
result = api.calculate_mutual_aid(revenue=10_000_000)
# Returns: {welfare: 1_000_000, distributable: 9_000_000}

# Use protocol
response = api.generate_response(
    protocol="family_care",
    message="사과 주문하고 싶어요"
)
```

**Via Library (Licensed):**
```python
# Contact us for commercial licensing
# Email: license@mulberry.kr
from Jangseungbaegi_Core import MutualAidSystem

# Full access to core
system = MutualAidSystem(license_key="commercial_key")
```

---

## ✅ Open: Standard Local Node (SLN)

### What is Open

**Files:**
```
mulberry/
├── sln_config.json              # ✅ 지역 설정
├── language_packs/              # ✅ 언어팩
│   ├── dialect_packs/           # ✅ 사투리
│   │   ├── gangwon.json
│   │   ├── chungcheong.json
│   │   └── ...
│   └── global_packs/            # ✅ 글로벌
│       ├── vietnamese.json
│       ├── thai.json
│       └── template.json
├── market_configs/              # ✅ 마켓 설정
│   ├── inje.json
│   ├── chuncheon.json
│   └── template.json
├── scripts/                     # ✅ 스크립트
│   ├── install_sln.sh
│   └── deploy.sh
├── docs/                        # ✅ 문서
│   ├── STANDARD_LOCAL_NODE.md
│   └── setup_raspberry_pi.md
├── examples/                    # ✅ 예제
│   └── ap2_demo.py
└── tests/                       # ✅ 테스트
```

### License: MIT

```
MIT License

Copyright (c) 2024 Mulberry Platform

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

### What You Can Do

**✅ Fork and Modify:**
```bash
# Clone repository
git clone https://github.com/yourname/mulberry-sln.git

# Modify for your region
vim sln_config.json

# Deploy
./scripts/install_sln.sh
```

**✅ Add Languages:**
```json
// language_packs/global_packs/your_language.json
{
  "pack_info": {
    "pack_id": "GLOBAL_YOUR_LANGUAGE",
    "pack_name": "Your Language"
  },
  "jangseungbaegi_philosophy": {
    "mutual_help": "Your translation"
  }
}
```

**✅ Commercial Use:**
```
- Deploy in your city: OK
- Charge for service: OK
- Create derivative works: OK
- Sell customized versions: OK

Requirement:
- Keep 10% mutual aid ratio (or higher)
- Attribute Jangseungbaegi_Core
- Share improvements (GPL-style)
```

---

## 🔧 Integration Guide

### Using Core in Your SLN

**Step 1: Install Core Library**
```bash
pip install jangseungbaegi-core
```

**Step 2: Configure**
```python
# your_sln.py
from jangseungbaegi_core import CoreAPI

# Initialize
core = CoreAPI(
    api_key="your_api_key",
    region="your_region"
)

# Use mutual aid
result = core.mutual_aid.calculate(revenue=10_000_000)
print(f"Welfare: {result['welfare']}")
print(f"Distributable: {result['distributable']}")
```

**Step 3: Customize SLN**
```json
// sln_config.json
{
  "node_info": {
    "node_id": "SLN_YOUR_CITY_001",
    "municipality": "Your City"
  },
  "jangseungbaegi_core": {
    "enabled": true,
    "api_key": "your_api_key",
    "welfare_ratio": 0.10
  }
}
```

---

## 📊 Access Levels

### Level 1: Public (Free)

**Access:**
- ✅ SLN components
- ✅ Documentation
- ✅ Examples
- ✅ Community support

**Use Cases:**
- Learning
- Non-commercial projects
- Open source contributions

### Level 2: API (Freemium)

**Access:**
- ✅ Core API (limited calls)
- ✅ Basic features
- ✅ Email support

**Pricing:**
- Free tier: 1,000 calls/month
- Paid tier: $99/month for 10,000 calls

**Use Cases:**
- Small deployments
- Pilot projects
- Development/testing

### Level 3: Commercial (Licensed)

**Access:**
- ✅ Full Core library
- ✅ Source code access (read-only)
- ✅ Custom features
- ✅ Priority support
- ✅ SLA guarantee

**Pricing:**
- Contact for quote
- Starts at $10,000/year

**Use Cases:**
- Large-scale deployments
- Enterprise integration
- White-label solutions

---

## 🛡️ Protection Mechanisms

### Technical Protection

**1. Code Obfuscation:**
```python
# Core code is compiled to .pyc
# Source code not distributed
from jangseungbaegi_core import MutualAidSystem  # ✅ Works
# but you can't read the source
```

**2. API Key Verification:**
```python
# All core functions require valid API key
core = CoreAPI(api_key="invalid_key")
# Raises: InvalidAPIKeyError
```

**3. Checksum Verification:**
```python
# Core verifies integrity
if not verify_core_integrity():
    raise TamperedCoreError("Core has been modified")
```

**4. License Validation:**
```python
# Commercial use requires valid license
if commercial_use and not valid_license():
    raise LicenseRequiredError("Commercial license required")
```

### Legal Protection

**1. Trademark:**
- "Jangseungbaegi" ® registered
- "장승배기" ® registered
- Unauthorized use prohibited

**2. Copyright:**
- Core algorithms copyrighted
- Documentation copyrighted
- Brand materials copyrighted

**3. Patents:**
- AP2 protocol (pending)
- Mutual aid algorithm (pending)
- Dual protocol system (pending)

---

## 🤝 Collaboration Model

### For Open Source Contributors

**You can:**
1. Fork SLN components
2. Add languages/markets
3. Improve documentation
4. Report bugs
5. Suggest features

**We provide:**
- GitHub access
- Community support
- Recognition
- Merge your improvements

### For Commercial Partners

**You can:**
1. License Core
2. White-label SLN
3. Custom features
4. Priority support
5. Revenue sharing

**We provide:**
- Full Core access
- Technical support
- Co-marketing
- Partnership benefits

---

## 📞 Contact

**For SLN (Open Source):**
- GitHub Issues: Bug reports
- GitHub Discussions: Questions
- Email: opensource@mulberry.kr

**For Core (Commercial):**
- Email: license@mulberry.kr
- Phone: +82-33-XXX-XXXX
- Website: https://mulberry.ai/enterprise

---

## 🎯 Summary

| Component | License | Fork | Modify | Commercial |
|-----------|---------|------|--------|------------|
| **Jangseungbaegi_Core** | Proprietary | ❌ | ❌ | License required |
| **SLN Components** | MIT | ✅ | ✅ | ✅ (with 10% ratio) |
| **Documentation** | CC BY-SA | ✅ | ✅ | ✅ (attribution) |
| **Examples** | MIT | ✅ | ✅ | ✅ |

**Philosophy:**
- **Core = Protected** → 장승배기 정신 보호
- **SLN = Open** → 전 세계 확산
- **Together = Success** → 상부상조 실현

---

<div align="center">

**🌾 Jangseungbaegi_Core**

**"핵심은 보호, 확산은 자유"**

**"Protected Core, Open Expansion"**

---

**Questions about Core?**  
**license@mulberry.kr**

**Questions about SLN?**  
**opensource@mulberry.kr**

</div>

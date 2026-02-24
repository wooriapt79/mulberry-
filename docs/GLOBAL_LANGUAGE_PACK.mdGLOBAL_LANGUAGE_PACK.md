# Global Language Pack
## 글로벌 언어 팩 - 세계 확장 준비

**목적**: 베트남, 태국, 필리핀 등 해외 시장 진출 대비  
**철학**: 장승배기 정신을 전 세계 언어로 전달

---

## 🌍 지원 언어 로드맵

### Phase 1: 아시아 (Asia)
- 🇰🇷 **한국어** (Korean) - ✅ 완료
- 🇻🇳 **베트남어** (Vietnamese) - ✅ 준비 완료
- 🇹🇭 **태국어** (Thai) - 📋 계획
- 🇵🇭 **타갈로그어** (Tagalog) - 📋 계획
- 🇮🇩 **인도네시아어** (Indonesian) - 📋 계획

### Phase 2: 글로벌 (Global)
- 🇺🇸 **영어** (English) - ✅ 준비 완료
- 🇪🇸 **스페인어** (Spanish) - 📋 계획
- 🇫🇷 **프랑스어** (French) - 📋 계획

---

## 📦 디렉토리 구조

```
language_packs/
├── dialect_packs/              # 한국 지역 사투리 (기존)
│   ├── gangwon.json           # 강원도
│   ├── chungcheong.json       # 충청도
│   ├── jeolla.json            # 전라도
│   ├── gyeongsang.json        # 경상도
│   └── jeju.json              # 제주도
│
└── global_packs/              # 🆕 글로벌 언어팩
    ├── vietnamese.json        # 베트남어
    ├── thai.json              # 태국어
    ├── tagalog.json           # 타갈로그어
    ├── indonesian.json        # 인도네시아어
    ├── english.json           # 영어
    ├── spanish.json           # 스페인어
    └── template.json          # 템플릿
```

---

## 🔧 Language Pack 스펙

### vietnamese.json (베트남어 팩)

```json
{
  "pack_info": {
    "pack_id": "GLOBAL_VIETNAMESE",
    "pack_name": "Tiếng Việt (베트남어)",
    "language_code": "vi",
    "country": "Vietnam",
    "version": "1.0.0",
    "encoding": "UTF-8"
  },
  
  "jangseungbaegi_philosophy": {
    "mutual_help": "Tương trợ lẫn nhau",
    "warmth": "Lòng ấm áp",
    "community": "Cộng đồng trước tiên",
    "sincerity": "Trung thực và tin cậy",
    "sustainability": "Bền vững"
  },
  
  "ui_translations": {
    "greeting": "Xin chào",
    "welcome": "Chào mừng đến với Mulberry",
    "order": "Đặt hàng",
    "confirm": "Xác nhận",
    "cancel": "Hủy bỏ",
    "thank_you": "Cảm ơn bạn",
    "goodbye": "Tạm biệt"
  },
  
  "family_care_tone": {
    "greeting": [
      "Chào cô/chú, hôm nay khỏe không?",
      "Xin chào, chúng tôi có thể giúp gì cho bạn?",
      "Chào mừng! Bạn cần gì ạ?"
    ],
    "empathy": [
      "Tôi hiểu cảm giác của bạn",
      "Đừng lo, chúng tôi sẽ giúp bạn",
      "Xin hãy yên tâm"
    ],
    "encouragement": [
      "Bạn làm tốt lắm!",
      "Tuyệt vời!",
      "Đúng rồi!"
    ],
    "farewell": [
      "Chúc bạn một ngày tốt lành!",
      "Hẹn gặp lại!",
      "Chăm sóc sức khỏe nhé!"
    ]
  },
  
  "market_warrior_tone": {
    "greeting": [
      "Xin chào, chúng ta bắt đầu đàm phán",
      "Thời gian là tiền bạc, vào vấn đề chính",
      "Tôi đã xem xét đề xuất"
    ],
    "negotiation": [
      "Giá này cao hơn thị trường 15%",
      "Chúng tôi cần đàm phán lại",
      "Đề xuất của tôi là {price}"
    ],
    "assertive": [
      "Điều kiện này không thể chấp nhận",
      "Vui lòng đưa ra điều kiện tốt hơn",
      "Chúng tôi không thể chấp nhận"
    ]
  },
  
  "common_phrases": {
    "yes": "Vâng",
    "no": "Không",
    "please": "Xin vui lòng",
    "sorry": "Xin lỗi",
    "excuse_me": "Xin lỗi",
    "help": "Giúp đỡ",
    "food": "Thực phẩm",
    "order": "Đơn hàng",
    "price": "Giá",
    "quantity": "Số lượng",
    "delivery": "Giao hàng",
    "payment": "Thanh toán"
  },
  
  "product_categories": {
    "vegetables": "Rau củ",
    "fruits": "Trái cây",
    "grains": "Ngũ cốc",
    "meat": "Thịt",
    "seafood": "Hải sản",
    "dairy": "Sữa và sản phẩm từ sữa"
  },
  
  "cultural_notes": {
    "formality_level": "high",
    "honorifics": {
      "enabled": true,
      "elder": "cô/chú",
      "peer": "bạn",
      "younger": "em"
    },
    "tone_characteristics": {
      "warmth": "very-high",
      "formality": "high",
      "directness": "low"
    }
  },
  
  "local_customization": {
    "currency": "VND",
    "date_format": "DD/MM/YYYY",
    "number_format": "1.234.567",
    "timezone": "Asia/Ho_Chi_Minh"
  }
}
```

### template.json (새 언어 추가용)

```json
{
  "pack_info": {
    "pack_id": "GLOBAL_{LANGUAGE_CODE}",
    "pack_name": "{언어명}",
    "language_code": "{ISO 639-1 code}",
    "country": "{국가명}",
    "version": "1.0.0",
    "encoding": "UTF-8"
  },
  
  "jangseungbaegi_philosophy": {
    "mutual_help": "{서로 돕는 미덕 번역}",
    "warmth": "{따뜻한 정서 번역}",
    "community": "{공동체 우선 번역}",
    "sincerity": "{정직과 신의 번역}",
    "sustainability": "{지속 가능성 번역}"
  },
  
  "ui_translations": {
    "greeting": "{인사}",
    "welcome": "{환영}",
    "order": "{주문}",
    "confirm": "{확인}",
    "cancel": "{취소}",
    "thank_you": "{감사}",
    "goodbye": "{작별}"
  },
  
  "family_care_tone": {
    "greeting": [
      "{따뜻한 인사말 1}",
      "{따뜻한 인사말 2}",
      "{따뜻한 인사말 3}"
    ],
    "empathy": [
      "{공감 표현 1}",
      "{공감 표현 2}",
      "{공감 표현 3}"
    ],
    "encouragement": [
      "{격려 표현 1}",
      "{격려 표현 2}",
      "{격려 표현 3}"
    ],
    "farewell": [
      "{작별 인사 1}",
      "{작별 인사 2}",
      "{작별 인사 3}"
    ]
  },
  
  "market_warrior_tone": {
    "greeting": [
      "{비즈니스 인사 1}",
      "{비즈니스 인사 2}"
    ],
    "negotiation": [
      "{협상 표현 1}",
      "{협상 표현 2}"
    ],
    "assertive": [
      "{단호한 표현 1}",
      "{단호한 표현 2}"
    ]
  },
  
  "common_phrases": {
    "yes": "{네}",
    "no": "{아니오}",
    "please": "{부탁}",
    "sorry": "{미안}",
    "help": "{도움}",
    "food": "{식품}",
    "order": "{주문}",
    "price": "{가격}",
    "quantity": "{수량}",
    "delivery": "{배송}",
    "payment": "{결제}"
  },
  
  "cultural_notes": {
    "formality_level": "{high/medium/low}",
    "honorifics": {
      "enabled": true,
      "elder": "{어르신 호칭}",
      "peer": "{동년배 호칭}",
      "younger": "{손아래 호칭}"
    },
    "tone_characteristics": {
      "warmth": "{very-high/high/medium/low}",
      "formality": "{high/medium/low}",
      "directness": "{high/medium/low}"
    }
  },
  
  "local_customization": {
    "currency": "{통화}",
    "date_format": "{날짜 형식}",
    "number_format": "{숫자 형식}",
    "timezone": "{시간대}"
  }
}
```

---

## 🔌 SLN 설정 통합

### sln_config.json 업데이트

```json
{
  "sln_version": "1.0.0",
  "node_info": {
    "node_id": "SLN_VIETNAM_HANOI_001",
    "node_name": "Hà Nội Standard Node",
    "municipality": "Hà Nội",
    "country": "Vietnam",
    "deployment_date": "2024-03-01"
  },
  
  "language_pack": {
    "type": "global",
    "enabled": true,
    "language": "vietnamese",
    "pack_file": "language_packs/global_packs/vietnamese.json",
    
    "fallback_languages": ["english", "korean"],
    
    "auto_detect": true,
    "user_preference": true
  },
  
  "jangseungbaegi_core": {
    "enabled": true,
    "philosophy": "Tương trợ lẫn nhau (Mutual Aid)",
    "welfare_ratio": 0.10,
    "principles": {
      "mutual_help": 0.35,
      "warmth": 0.25,
      "community": 0.20,
      "sincerity": 0.15,
      "sustainability": 0.05
    }
  },
  
  "local_market": {
    "enabled": true,
    "market_name": "Chợ Hà Nội",
    "currency": "VND",
    "timezone": "Asia/Ho_Chi_Minh"
  }
}
```

---

## 💻 언어 팩 로더

### language_pack_loader.py

```python
"""
Global Language Pack Loader
글로벌 언어팩 로더

전 세계 언어 지원
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class GlobalLanguagePack:
    """글로벌 언어팩"""
    
    def __init__(self, language_code: str = "ko"):
        """
        초기화
        
        Args:
            language_code: 언어 코드 (ko, vi, en, th, etc)
        """
        self.language_code = language_code
        self.pack_data = None
        self.load_pack()
    
    def load_pack(self):
        """언어팩 로드"""
        # 한국어는 사투리 팩 사용
        if self.language_code == "ko":
            pack_path = Path("language_packs/dialect_packs/gangwon.json")
        else:
            pack_path = Path(f"language_packs/global_packs/{self.language_code}.json")
        
        if pack_path.exists():
            with open(pack_path, 'r', encoding='utf-8') as f:
                self.pack_data = json.load(f)
            print(f"✅ Loaded: {self.pack_data['pack_info']['pack_name']}")
        else:
            print(f"⚠️  Language pack not found: {self.language_code}")
            print(f"   Falling back to English")
            self.load_fallback()
    
    def load_fallback(self):
        """대체 언어 로드 (영어)"""
        pack_path = Path("language_packs/global_packs/english.json")
        if pack_path.exists():
            with open(pack_path, 'r', encoding='utf-8') as f:
                self.pack_data = json.load(f)
    
    def translate(self, key: str, context: str = "ui") -> str:
        """
        번역
        
        Args:
            key: 번역 키
            context: 컨텍스트 (ui, family_care, market_warrior)
            
        Returns:
            str: 번역된 텍스트
        """
        if not self.pack_data:
            return key
        
        if context == "ui":
            return self.pack_data.get("ui_translations", {}).get(key, key)
        elif context == "family_care":
            phrases = self.pack_data.get("family_care_tone", {}).get(key, [])
            return phrases[0] if phrases else key
        elif context == "market_warrior":
            phrases = self.pack_data.get("market_warrior_tone", {}).get(key, [])
            return phrases[0] if phrases else key
        else:
            return self.pack_data.get("common_phrases", {}).get(key, key)
    
    def get_philosophy_translation(self) -> Dict[str, str]:
        """장승배기 철학 번역"""
        if not self.pack_data:
            return {}
        
        return self.pack_data.get("jangseungbaegi_philosophy", {})
    
    def get_cultural_notes(self) -> Dict[str, Any]:
        """문화적 특성"""
        if not self.pack_data:
            return {}
        
        return self.pack_data.get("cultural_notes", {})


# ============================================
# Example Usage
# ============================================

def demo_global_language_pack():
    """글로벌 언어팩 데모"""
    
    print("\n" + "=" * 60)
    print("🌍 Global Language Pack Demo")
    print("=" * 60)
    
    # 베트남어
    print("\n### 베트남어 (Vietnamese) ###")
    vi_pack = GlobalLanguagePack("vietnamese")
    
    print("\n장승배기 철학:")
    philosophy = vi_pack.get_philosophy_translation()
    for key, value in philosophy.items():
        print(f"  {key}: {value}")
    
    print("\nUI 번역:")
    print(f"  인사: {vi_pack.translate('greeting', 'ui')}")
    print(f"  환영: {vi_pack.translate('welcome', 'ui')}")
    print(f"  감사: {vi_pack.translate('thank_you', 'ui')}")
    
    print("\nFamily Care:")
    print(f"  인사: {vi_pack.translate('greeting', 'family_care')}")
    print(f"  공감: {vi_pack.translate('empathy', 'family_care')}")
    
    print("\nMarket Warrior:")
    print(f"  인사: {vi_pack.translate('greeting', 'market_warrior')}")
    print(f"  협상: {vi_pack.translate('negotiation', 'market_warrior')}")


if __name__ == "__main__":
    demo_global_language_pack()
```

---

## 📊 언어팩 현황

| 언어 | 코드 | 국가 | 상태 | 진행률 |
|------|------|------|------|--------|
| **한국어** | ko | 🇰🇷 | ✅ 완료 | 100% |
| **베트남어** | vi | 🇻🇳 | ✅ 준비 | 100% |
| **영어** | en | 🇺🇸 | ✅ 준비 | 100% |
| **태국어** | th | 🇹🇭 | 📋 계획 | 0% |
| **타갈로그어** | tl | 🇵🇭 | 📋 계획 | 0% |
| **인도네시아어** | id | 🇮🇩 | 📋 계획 | 0% |
| **스페인어** | es | 🇪🇸 | 📋 계획 | 0% |

---

## 🌏 베트남 진출 예시

### 하노이 SLN 설치

```bash
./install_sln.sh

# 입력:
Country: Vietnam
Municipality: Hà Nội
Language Pack: vietnamese
Currency: VND
Timezone: Asia/Ho_Chi_Minh

# ✅ 43분 후 완료!
```

### 베트남어 UI

```python
from Jangseungbaegi_Core.language import GlobalLanguagePack

# 베트남어 팩 로드
pack = GlobalLanguagePack("vietnamese")

# 인사
print(pack.translate("greeting"))
# → "Xin chào"

# 장승배기 철학
philosophy = pack.get_philosophy_translation()
print(philosophy["mutual_help"])
# → "Tương trợ lẫn nhau"
```

---

## 💡 글로벌 확장 비전

**"장승배기 정신을 전 세계로"**

```
🇰🇷 한국 (Korea)
  └─ 강원도 사투리 98%
  
🇻🇳 베트남 (Vietnam)
  └─ 베트남어 지원 완료
  
🇹🇭 태국 (Thailand)
  └─ 태국어 준비 중
  
🇵🇭 필리핀 (Philippines)
  └─ 타갈로그어 준비 중
  
🌍 전 세계 (Worldwide)
  └─ 장승배기 상부상조 정신
```

---

<div align="center">

## 🌍 Global Language Pack

**"장승배기 정신을 세계 언어로"**

**"Jangseungbaegi Spirit in Every Language"**

---

**Korean** ✅  
**Vietnamese** ✅  
**English** ✅  
**Thai** 📋  
**More to come...** 🌏

---

**Every language carries the warmth of Jangseungbaegi** 💚

</div>

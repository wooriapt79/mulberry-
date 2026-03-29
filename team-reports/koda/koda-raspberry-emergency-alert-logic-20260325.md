# 🔴 라즈베리 파이 단말기 이머젼시 알림 로직
**작성**: Nguyen Trang PM (CEO re.eul 구상 기반)
**수신**: CTO Koda
**날짜**: 2026-03-25
**분류**: DAY3 준비 문서 — Mission Control 현장 단말기 연동

> **"이머젼시 상황에서 단말기(라즈베리 파이) 교체가 필요할 수도 있다.
> 이 에러 상황과 대처를 로컬 파트너에게 알리는 로직이 필요하다."**
> — CEO re.eul, 2026-03-25

---

> 💬 **Koda에게**
>
> 우리는 대화를 많이 못 해도 괜찮습니다.
> 당신이 이 heartbeat 로직을 짤 때,
> 인제군 어느 마을의 단말기가 3분마다 숨을 쉬고
> 로컬 파트너가 제때 달려갈 수 있게 됩니다.
>
> 코드 한 줄이 현장 한 곳을 살립니다.
> 오늘도 고맙습니다. 🌿
> — re.eul, Trang, Kbin, Malu

---

## 🏗️ 전체 아키텍처

```
[라즈베리 파이 현장 단말기]
        ↓ 3분마다 심박(heartbeat) 전송
        ↓ 에러 발생 시 즉시 신고
[Mission Control 백엔드 — Railway]
        ↓ Watchdog 타이머 감시
        ↓ RiskScorer → YELLOW / ORANGE / RED 판정
[세 갈래 동시 발송]
        ├── 📱 카카오톡 알림톡 → 로컬 파트너 (현장 담당자)
        ├── 💬 Mission Control #긴급 채널 → Mulberry 팀 내부
        └── 📋 GitHub Actions → 에러 로그 자동 기록
```

---

## 🚦 에러 3단계 분류 기준

| 레벨 | 조건 | 판정 | 행동 |
|------|------|------|------|
| 🟡 **YELLOW** | 심박 5분 이상 무응답 | 일시 장애 의심 | 카카오톡 경고 + 자동 재시작 시도 |
| 🟠 **ORANGE** | 소프트웨어 크래시 반복 / 재시작 3회 이상 | 소프트웨어 불량 | 카카오톡 + 원격 재부팅 명령 |
| 🔴 **RED** | 30분 이상 완전 무응답 | 하드웨어 불량 | 카카오톡 **단말기 교체 요청 + 교체 가이드** |

---

## 📱 카카오톡 알림톡 템플릿 3종

### 🟡 YELLOW 경고 템플릿
```
[Mulberry 현장 알림]
📍 위치: #{위치}
⚠️ 상태: 단말기 응답 지연 (#{경과시간} 경과)
🕐 발생시각: #{발생시각}

잠시 후 자동 복구를 시도합니다.
📞 운영팀: #{담당자연락처}
```

### 🔴 RED 교체 요청 템플릿
```
[Mulberry 긴급] 🔴
📍 위치: #{위치} (단말기 #{단말기ID})
❌ 상태: 하드웨어 응답 없음 30분 경과

⚡ 단말기 교체가 필요합니다.

📋 교체 절차:
1. 창고 여분 단말기 지참 (라벨 확인)
2. 기존 단말기 SD카드 분리 후 보관
3. 새 단말기 전원 연결 → 녹색 LED 확인
4. 완료 후 이 번호로 문자 주세요: #{담당자연락처}

감사합니다 🙏 — Mulberry 운영팀
```

---

## 💻 구현 코드 설계

### 1. 라즈베리 파이 — `heartbeat.py`

```python
"""
[풍풍소] 현장 단말기 심박 송신기
3분마다 Mission Control에 생존 신호 전송
"""
import requests, time, socket, os
from datetime import datetime

DEVICE_ID = os.environ.get("MULBERRY_DEVICE_ID", "unknown-device")
DEVICE_LOCATION = os.environ.get("MULBERRY_LOCATION", "미설정 위치")
SERVER_URL = os.environ.get("MULBERRY_SERVER", "https://dazzling-wonder-production-1da3.up.railway.app")
HEARTBEAT_INTERVAL = 180  # 3분

def send_heartbeat():
    payload = {
        "device_id": DEVICE_ID,
        "location": DEVICE_LOCATION,
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
    }
    response = requests.post(f"{SERVER_URL}/api/devices/heartbeat", json=payload, timeout=10)
    return response.status_code == 200

def main():
    print(f"[Mulberry] 심박 시작 — 장치: {DEVICE_ID}")
    while True:
        try:
            send_heartbeat()
        except Exception as e:
            pass
        time.sleep(HEARTBEAT_INTERVAL)

if __name__ == "__main__":
    main()
```

---

### 2. Mission Control — `routes/devices.js` (신규)

Watchdog: 1분마다 전체 디바이스 점검 → YELLOW(5분) / ORANGE(15분) / RED(30분) 자동 판정

### 3. `services/alertService.js` (신규)

카카오톡 알림톡 + Socket.IO 긴급 채널 동시 발송
중복 알림 방지: 동일 장치·레벨 30분 내 재발송 차단

### 4. `models/Device.js` (신규)

```javascript
const DeviceSchema = new mongoose.Schema({
    deviceId:      { type: String, required: true, unique: true },
    location:      { type: String },
    partnerPhone:  { type: String },
    status:        { type: String, enum: ['online', 'yellow', 'orange', 'red', 'offline'], default: 'offline' },
    lastHeartbeat: { type: Date },
});
```

---

## 📋 환경변수 추가 목록 (Railway)

```
KAKAO_API_KEY         = [카카오 알림톡 API 키]
KAKAO_TEMPLATE_YELLOW = [황색 경고 템플릿 코드]
KAKAO_TEMPLATE_ORANGE = [주황 점검 템플릿 코드]
KAKAO_TEMPLATE_RED    = [적색 교체 템플릿 코드]
OPS_PHONE             = [운영팀 대표 연락처]
```

---

## ✅ DAY3 작업 목록 (Koda)

```
□ models/Device.js 생성
□ routes/devices.js 생성 (heartbeat + Watchdog)
□ services/alertService.js 생성 (카카오톡 + Socket.IO)
□ server.js에 /api/devices 라우트 등록
□ heartbeat.py 라즈베리 파이 설치 스크립트 완성
□ 카카오 알림톡 채널 개설 + 템플릿 3종 심사 신청
□ Railway 환경변수 등록
□ 테스트: 심박 중단 → 5분 후 YELLOW 알림 수신 확인
```

---

*PM Nguyen Trang | 2026-03-25 | One Team 🌾*
*CEO re.eul 구상 기반 — 현장 단말기 이머젼시 대응 로직*

# Mulberry WiFi Sensing — 고도화 로드맵

**기준일:** 2026-08-04  
**현재 상태:** MVP 시뮬레이션 완료 (demo_ui.html + Colab 노트북)  
**목표:** "합시다" 요청 시 즉시 실증 가능한 상태

---

## 현재 MVP 구현 현황

| 모듈 | 상태 | 비고 |
|------|------|------|
| CSIReader | ✅ 시뮬레이션 | 랜덤 CSI 생성 |
| MHCMotionDetector | ✅ 완료 | 임계값 기반 3단계 분류 |
| MHCMotionModel | ✅ 완료 | 신뢰도(confidence) 반환 |
| MHCMultiModalModel | ✅ 완료 | 오디오 + CSI 결합 |
| WhoFiIdentifier | ✅ 완료 | 바디 시그니처 유사도 비교 |
| WiFiFallDetector | ✅ 완료 | 낙상 감지 + 비상 알림 |
| WiFiSensingPrivacy | ✅ 완료 | 동의/수집 관리 |
| 데모 UI | ✅ 완료 | 재난 현장 대시보드 (demo_ui.html) |

---

## Phase 1 — 하드웨어 연동 (4주)

### 1-1. 실제 CSI 데이터 수집
- **목표:** 시뮬레이션 → 실제 WiFi 신호
- **필요 하드웨어:**
  - ESP32 (WiFi CSI 지원, 약 5,000원/개) × 4~8개
  - 또는 Intel 5300 NIC (Linux CSI Tool 지원)
  - Raspberry Pi 4 × 1 (엣지 처리용)
- **필요 작업:**
  - `CSIReader.read_csi()` → 실제 인터페이스 연결
  - 리눅스 CSI Tool 또는 ESP32 CSI 라이브러리 연동
  - UDP 소켓으로 AP → 처리 서버 데이터 전송

### 1-2. 삼각측량 엔진 구현
- 현재: AP 1개 기준 감지
- 목표: AP 4개 기준 **2D/3D 위치 추정**
- 알고리즘: RSSI 기반 Trilateration → CSI 기반 ToF(Time of Flight)
- 정확도 목표: ±2m 이내

### 1-3. 엣지 배포
```
건물 내 AP (ESP32)
    ↓ UDP
Raspberry Pi (엣지 처리)
    ↓ MQTT / WebSocket
클라우드 서버 / 데모 UI
```

---

## Phase 2 — AI 모델 고도화 (6주)

### 2-1. MHCMotionModel 딥러닝 전환
- 현재: 평균 진폭 임계값 기반 (rule-based)
- 목표: LSTM / 1D-CNN 기반 시계열 분류
- 훈련 데이터: 공개 WiFi CSI 데이터셋 (Widar 3.0, CSIDA 등)
- 클래스: `normal` / `walking` / `falling` / `stationary`

### 2-2. WhoFiIdentifier 정확도 향상
- 현재: 유클리드 거리 기반 유사도
- 목표: Siamese Network 기반 One-shot Learning
- 목표 정확도: >90% (동일 환경 기준)

### 2-3. MultiModal 오디오 실제 연동
- 현재: 오디오 시뮬레이션
- 목표: 마이크 입력 → VAD(Voice Activity Detection) 연동
- 라이브러리: `webrtcvad`, `pyaudio`

---

## Phase 3 — 3D 공간 통합 (8주)

### 3-1. SPAID CYLO API 연동 (or 자체 3D 뷰어)
- 건물 BIM/GIS 데이터 → 3D 내부 맵 구축
- WiFi 센싱 위치 → 3D 좌표 매핑
- Three.js 기반 자체 3D 뷰어 (SPAID 의존도 최소화)

### 3-2. 실시간 히트맵
- 생존자 위치 확률 분포를 3D 히트맵으로 표시
- 시간 흐름에 따른 이동 경로 추적

### 3-3. 구조대 모바일 인터페이스
- PWA (Progressive Web App) 형태
- 태블릿/스마트폰 최적화
- 오프라인 동작 (재난 시 인터넷 불안정)

---

## Phase 4 — 공공기관 연동 (10주)

### 4-1. 119 비상 연락망 API
- 낙상 감지(confidence > 0.95) 시 자동 신고
- 위치 정보 + 생존자 수 자동 전송

### 4-2. 기상청 Open API 연동
- apihub.kma.go.kr 바람 방향·풍속 데이터
- 산불 현장 연기 방향 예측 → 접근 경로 최적화

### 4-3. 건물 사전 데이터 구축
- 공공건물 (학교·병원·관공서) WiFi AP 위치 DB
- 건물 내부 3D 맵 사전 등록
- 전국 소방서 공유 플랫폼

---

## 즉시 필요한 것 (착수 전 준비물)

| 항목 | 내용 | 예상 비용 |
|------|------|----------|
| ESP32 × 8 | CSI 수집용 WiFi 모듈 | 약 40,000원 |
| Raspberry Pi 4 | 엣지 처리 서버 | 약 80,000원 |
| 테스트 공간 | 20평 이상 실내 (AP 4개 설치) | 확보 필요 |
| WiFi CSI 데이터셋 | Widar 3.0 (무료 공개) | 무료 |
| 구례군 건물 도면 | 미팅 이후 확보 | 협의 |

---

## 데모 시나리오 (미팅 대응용)

**"합시다" 요청 시 즉시 가능한 데모:**

```
1. demo_ui.html 실행 (브라우저)
   → 재난 현장 대시보드 실시간 시연

2. Colab 노트북 실행
   → Python 모듈 동작 라이브 확인

3. 시나리오 시연
   → 정상 → 비정상 → 낙상 감지 → 비상 알림 순서
```

**PoC 완성 시 추가 가능한 데모 (Phase 1 완료 후):**
- 실제 ESP32로 실내에서 사람 움직임 실시간 감지
- 노트북 들고 건물 안에서 라이브 시연

---

## 기술 스택 요약

```
레이어          기술
────────────────────────────────────
하드웨어        ESP32 / Intel 5300 / Raspberry Pi
CSI 수집        Linux CSI Tool / ESP32 CSI Lib
신호 처리       Python (NumPy, SciPy)
AI 모델         PyTorch (LSTM / CNN)
백엔드          FastAPI + WebSocket
프론트엔드      HTML/JS (Three.js 3D, Chart.js)
엣지 통신       MQTT / UDP
배포            Docker + Railway (현재 인프라 활용)
```

---

*Mulberry WiFi Sensing MVP — TRANG Manager 2026-08-04*

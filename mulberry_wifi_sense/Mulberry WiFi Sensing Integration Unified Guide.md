# 📑 Mulberry WiFi Sensing Integration Unified Guide

이 문서는 WiFi 센싱 모듈과 mHC 시스템 연동 프로젝트의 설계 구조, 핵심 기능 및 배포 프로세스를 통합한 전체 안내서입니다.

---

## 1. 프로젝트 개요 및 구조

WiFi CSI 데이터를 활용하여 사용자의 움직임을 실시간 감지하고 mHC 시스템과 연동하는 MVP 모델입니다.

### 시스템 아키텍처 (Core Modules)

* **Sensing Engine**: `CSIReader`(수집), `MHCMotionDetector`(판별), `MHCMultiModalSensor`(복합 분석 및 전송).
* **Identification**: `WhoFiIdentifier`를 통한 고유 바디 시그니처 기반 사용자 식별.
* **Communication**: `MHCClient`를 통한 보안 REST API 통신 및 자동 재시도 로직.
* **Monitoring**: Dash/Plotly 기반 실시간 통합 대시보드.

---

## 2. 핵심 기능 및 데이터 규격

### 🚀 주요 기능

1. **낙상 및 비정상 움직임 감지**: WiFi 신호 변화를 분석하여 즉각적인 알림 및 mHC 전송.
2. **멀티모달 분석**: 오디오 스트림을 결합하여 상황 판단 정확도 향상 및 TTS 상호작용.
3. **보안 기반 개인 식별**: SHA-256 해싱을 통한 비식별화된 사용자 정보 등록 및 업데이트.

### 📊 데이터 송수신 규격 (JSON)

| 이벤트 종류     | 엔드포인트                       | 핵심 필드                                                   |
|:---------- |:--------------------------- |:------------------------------------------------------- |
| **낙상 알림**  | `/events/fall-detection`    | `eventType`, `confidence`, `location`, `alertTriggered` |
| **비정상 행동** | `/events/abnormal-movement` | `eventType`, `durationSeconds`, `personId`              |
| **개인 식별**  | `/users/identification`     | `personId`, `hashedBiometricSignature`, `deviceName`    |

---

## 3. 보안 정책

* **인증**: 모든 요청은 Header에 `Bearer {MHC_API_KEY}`를 포함해야 합니다.
* **개인정보 보호**: 원본 생체 데이터는 전송하지 않으며, 클라이언트 사이드 해싱을 필수 적용합니다.
* **환경 설정**: API Key는 환경 변수 또는 Secret Manager를 통해 관리하며 코드 내 하드코딩을 금지합니다.

---

## 4. Google Cloud Platform (GCP) 배포 가이드

### Step 1: 컨테이너화 및 이미지 푸시

```dockerfile
# Dockerfile 예시
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install dash pandas requests plotly
CMD ["python", "app.py"]
```

### Step 2: Cloud Run 배포 명령어

```bash
gcloud run deploy wifi-sensing-service \
  --image [IMAGE_URL] \
  --region asia-northeast3 \
  --set-env-vars MHC_API_BASE_URL=https://api.mhcsystem.com/v1 \
  --set-secrets MHC_API_KEY=MHC_API_KEY:latest
```

---

## 5. 장애 대응 및 유지보수

* **오류 처리**: `MHCApiError` 발생 시 지수 백오프 기반 최대 3회 재시도.
* **모니터링**: 대시보드를 통해 API 호출 성공률, 응답 시간 분포, 최근 이벤트 로그 실시간 추적.
* **알림**: 치명적 오류 발생 시 Slack/PagerDuty 연동 알림 트리거.

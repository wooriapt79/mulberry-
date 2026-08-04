# SPAID 업체 분석 + WiFi 센싱 × 3D 공간 전략 검토

**작성일:** 2026-08-04  
**작성:** TRANG Manager  
**목적:** 구례군 산불 3D 맵 미팅 대비 / Mulberry 전략적 포지셔닝

---

## 1. SPAID 업체 분석

### 기본 정보

| 항목 | 내용 |
|------|------|
| 정식 명칭 | SPAID Inc. (스패이드) |
| 풀네임 | Spatial Predictive Artificial Intelligent Data |
| 위치 | 서울 강남구 선릉로 111길 37 |
| CEO | 이종걸 (Chongkul Yi) |
| 사업자번호 | 209-81-67325 |
| 웹사이트 | https://www.spaid.ai |

### 수상 및 인증

- **CES 2025 Innovation Awards** — AI2RE (Image to 3D Geospatial AI Metaverse)
- **2024 K-GEO Festa 최우수상** — AI 기반 지적 매핑 엔진
- **2026 국토교통기술대전 국토교통부장관상**
- **ISO 인증** 취득
- **PCT 국제 특허** 포함 총 6건 등록

### 핵심 기술 구조

#### CYLO — Intelligent Spatial Engine
다양한 공간 데이터를 AI-Ready 데이터 + 경량화된 Platform-Ready 데이터로 변환하는 핵심 엔진.

```
다양한 공간 데이터 (위성/항공/GIS)
        ↓ CYLO
AI-Ready Data + Platform-Ready Data
        ↓
AI2RE 제품군
```

#### AI2RE 제품군 (5개)

| 제품 | 기능 |
|------|------|
| AI2RE-Studio | Vision AI 이미지 → 3D 생성 플랫폼 |
| AI2RE-GeoMap | 공간 인텔리전스 / 데이터 기반 의사결정 |
| AI2RE-Safety | 재난 예측 및 리스크 대응 |
| AI2RE-Feasibility | 입지·사업 타당성 평가 |
| AI2RE-Smart City | 실시간 모니터링 / 운영 의사결정 지원 |

### 팀 구성

**CEO 이종걸**
- Gehry Partners BIM 리더
- Samsung C&T BIM 수석 (건설 업계 BIM 표준화)
- 고려대학교 건축학과 교수
- → 개념 설계·BIM 도메인 강점

**CTO Youngmin Kim**
- Thermo Fisher Scientific 12년 (실시간 컴퓨팅 시스템)
- GPU & HPC 전문가 / *Accelerating MATLAB with GPU Computing* (Elsevier) 공저
- 유전자 분석·PCR·시퀀싱 장비 실시간 데이터 처리 설계
- → 저수준 GPU/실시간 처리 강점

### 등록 특허 목록

| 특허명 | 국가 | 번호 |
|--------|------|------|
| Terminal for Providing Information About Geographic Object | PCT | WO/2025/239482 |
| Method for Providing Geographic Information About Site | 한국 | 10-2024-0087864 |
| Server and Method for Modeling Geographic Object in 3D | 한국 | 10-2024-0087865 |
| **Method for Determining Footprint Area of Building** | 한국 | 10-2024-0087866 |
| Terminal for Providing Information on Geographical Objects | 한국 | 10-2024-0155289 |
| **Method for Creating 3D Geographical Objects** | 한국 | 10-2024-0196700 |

### 주요 수주 이력 (마일스톤)

- 2025.03 공공 철도 디지털 트윈 프로젝트 수주
- 2025.06 루마니아 민간항공청 AI GIS 프로젝트 수주 (해외)
- 2025.08 공공 철도 AI 프로젝트 수주
- 2025.12 공공 스마트시티 프로젝트 수주
- 2026.01 CES 2026 참가

---

## 2. 기술 실체 평가 (냉정한 시각)

### AI2RE-Studio 기술 구조 추정

```
위성 / 항공 이미지 (2D 원본)
        ↓
Foundation 모델 활용 추정
(SAM, NeRF, 3D Gaussian Splatting 계열)
        ↓
건물 Footprint 자동 추출 (자체 특허)
        ↓
3D 지리 객체 생성 (자체 특허 파이프라인)
        ↓
GIS 좌표 융합 → Digital Twin
```

완전 독자 개발이 아니라 **Foundation 모델 기반 + GIS 도메인 특화 파이프라인** 구조로 판단됨.

### ⚠️ 기술력 의문 포인트

**베트남 외주 개발 실패 이력**

특수 도메인(GIS + 3D 공간 처리)임에도 베트남 엔지니어에게 외주를 주었다가 개발이 꼬인 것으로 알려짐. 이는 다음을 시사함:

- 내부에 "실제 구현 가능한" GIS 소프트웨어 엔지니어 부재 가능성
- CEO는 개념 설계, CTO는 HPC 처리 강점 → **GIS 미들레이어 엔지니어링 공백** 의심
- 특허는 아이디어 보호, 구현 역량을 증명하지 않음

**데모 수작업 가능성**

외부 시연물이 실제 AI 자동화가 아닌 **Blender / SketchUp 수작업 3D 모델링** 후 AI 생성처럼 포장된 데모일 가능성 배제 불가.

### 🔍 기술 실체 검증 방법

미팅 시 이 질문 하나로 5분 안에 판별 가능:

> *"새로운 지역 데이터를 입력하면 3D 생성까지 실제로 얼마나 걸립니까? 지금 라이브로 보여주실 수 있나요?"*

- 자동화가 진짜면: 수십 분 내 결과 제시 가능
- 수작업 비중이 크면: "샘플 준비해서 보여드리겠습니다"로 넘어감

**서버 인프라 질문도 유효:**

> *"현재 3D 생성 파이프라인을 온프레미스로 운영하나요, 클라우드인가요? GPU 몇 장 기준으로 돌리고 계신가요?"*

진짜 AI 자동화라면 최소 NVIDIA A100급 GPU × 여러 장이 필요함. 구체적 답변이 없으면 수작업 비중 높은 것.

| 처리 규모 | 필요 GPU | RAM | 처리 시간 |
|----------|----------|-----|----------|
| 단일 건물 데모 | RTX 4090 × 1 | 64GB | 20분~1시간 |
| 소규모 블록 | A100 × 2~4 | 256GB | 수 시간 |
| 도시 구획 단위 | A100 × 8 이상 | 1TB | 수십 시간 |

---

## 3. WiFi 센싱 × 3D 공간 아이디어

### 개념 (CEO re.eul 제안, 2026-08-04)

> WiFi 신호를 이미지 데이터로 변환하여 Vision AI가 처리하고, 3D 공간 맵 위에 실시간으로 표시한다. 재난 현장 생존자 탐지를 타겟으로 공공기관에 진입한다.

### 기술 연결 구조

```
[기존 건물 WiFi AP들]
        ↓ CSI(Channel State Information) 신호 수집
[WiFi 센싱 엔진]
  — 삼각측량으로 사람 위치 추정
  — 움직임 / 호흡 패턴 감지
  — RF 신호 → 가상 이미지 변환
        ↓
[Vision AI (SPAID AI2RE-Studio 또는 유사)]
  — 가상 이미지 → 3D 공간 처리
        ↓
[3D 건물 내부 맵]
  — 생존자 위치 실시간 표시
  — 구조대 태블릿 / AR 헤드셋 전달
        ↓
"3층 북쪽 2명 감지 — 움직임 있음"
```

### 핵심 강점

**① 연기 · 콘크리트 · 어둠을 통과**
카메라가 불가능한 환경에서 WiFi 신호는 작동함. 산불 건물, 지진 붕괴 현장, 화재 모두 해당.

**② 기존 인프라 활용**
신규 건물은 이미 WiFi AP 설치됨. 추가 하드웨어 최소화 → 도입 비용 낮음.

**③ 개인정보 문제 없음**
이머전시 상황 + 공공기관 대상 → 재난안전법상 인명구조 목적으로 법적 근거 명확.

**④ SPAID가 없는 레이어**
SPAID AI2RE-Safety는 가시 조건에서만 작동. WiFi 센싱 추가 시 재난 현장까지 확장 → Mulberry가 없으면 SPAID도 못 들어가는 시장.

### 도전 과제

| 과제 | 내용 | 해결 방향 |
|------|------|----------|
| 재난 시 전력 차단 | AP가 꺼질 수 있음 | UPS / 배터리 내장 AP 설계 |
| 사전 3D 맵 구축 | 건물 내부 데이터 필요 | 공공건물(학교·병원·관공서) 우선 |
| AP 밀도 | 낮으면 정확도 하락 | 보완 AP 설치 가이드라인 수립 |

### 참고 기술 (업계 현황)

- **MIT RF-Pose (CSAIL)**: WiFi/RF 신호로 사람 포즈 추출 — 이미 논문 검증 완료
- **Widar 3.0 (북항대)**: CSI 신호로 제스처/행동 인식
- **Aerial Technologies**: WiFi 모션으로 가정 내 낙상 감지 (상용화)
- **Origin Wireless**: WiFi 모션 감지 플랫폼

**재난 현장 특화 상용 제품은 아직 없음 → 블루오션**

---

## 4. Mulberry 전략적 포지셔닝

### 역할 분담안

| 주체 | 역할 |
|------|------|
| **SPAID** | 3D 공간 플랫폼 (CYLO + AI2RE) |
| **WiFi 센싱 파트너 or Mulberry** | CSI 신호 수집 + RF 이미지 변환 엔진 |
| **Mulberry** | AI 분석 레이어 + 구조대 의사결정 지원 인터페이스 |

### 포지셔닝 메시지

> *"SPAID가 보이는 공간을 3D로 만든다면, Mulberry는 보이지 않는 공간까지 3D로 만든다."*

### 비즈니스 진입 전략

**1단계:** 소방청 / 지자체 재난안전부서 PoC  
→ 구례군 산불 프로젝트를 첫 레퍼런스로 활용

**2단계:** 공공 건물(학교·병원·관공서) 사전 3D 맵 구축 사업  
→ 매년 반복 수주 가능한 구조

**3단계:** 스마트빌딩 / 산업안전 확장  
→ 민간 시장으로 확대

### 구례군 미팅 준비 체크리스트

- [ ] WiFi 센싱 + 3D 맵 결합 1페이지 개념도 준비
- [ ] 기상청 Open API 바람 데이터 사전 확보 (산불 방향 예측 레이어)
- [ ] KOSIS API 키 수신 후 구례군 범위 FDI 데이터 시범 추출
- [ ] SPAID 라이브 데모 검증 질문 준비 (기술 실체 확인)
- [ ] Mulberry 독립 기술 파이프라인 유지 원칙 확인 (SPAID 의존도 최소화)

---

## 5. 종합 판단

SPAID는 외관(수상·특허·수주)과 내부 기술 실행력 사이에 갭이 의심되는 회사임. 협업 시 플랫폼 의존도를 높이는 것은 위험하며, Mulberry의 데이터·AI 분석 레이어는 독립적으로 유지해야 함.

WiFi 센싱 × 3D 공간 아이디어는 SPAID가 단독으로 들어갈 수 없는 **재난 현장 블루오션**을 열어준다. Mulberry가 이 레이어를 확보하면 구례군 미팅에서 단순 협력사가 아닌 **핵심 기술 파트너**로 포지셔닝 가능.

---

*TRANG Manager — 2026-08-04*  
*참조: https://www.spaid.ai / https://www.spaid.ai/about*

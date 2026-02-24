# Mulberry Platform - 인프라 설계서
## "Thin Central, Thick Edge" Architecture

**작성자**: Koda (CTO)  
**작성일**: 2024-02-14  
**버전**: 5.0.0 (Phase 5)

---

## 🎯 설계 철학

> **"중앙은 가볍게, 말단은 두텁게"**

**Why?**
- 중앙 서버 장애 시에도 지역이 독립 운영 가능
- 확장 시 지역 노드만 추가하면 됨
- 각 지역의 특성에 맞는 커스터마이징 가능

---

## 🏗️ 3계층 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│             🧠 CENTRAL (Thin)                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │  • ActivityPub 인증 (AP2)                        │  │
│  │  • 전역 마스토돈 허브                             │  │
│  │  • 통합 정산 엔진                                 │  │
│  │  • Sentinel 모니터링                             │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↕️ ActivityPub
┌─────────────────────────────────────────────────────────┐
│          🌐 REGIONAL NODES (Thick)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   인제군      │  │   춘천시      │  │   부여군      │  │
│  │              │  │              │  │              │  │
│  │  • Guardian  │  │  • Guardian  │  │  • Guardian  │  │
│  │  • 물류 DB    │  │  • 물류 DB    │  │  • 물류 DB    │  │
│  │  • 로컬 캐시  │  │  • 로컬 캐시  │  │  • 로컬 캐시  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↕️ ActivityPub
┌─────────────────────────────────────────────────────────┐
│           🖥️  EDGE (End-Points)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ RPI #1   │  │ RPI #2   │  │ RPI #3   │  │ RPI #N   ││
│  │ 어르신댁  │  │ 하나로   │  │ 보건소   │  │ 농가     ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## 1️⃣ CENTRAL (중앙 서버) - Thin

### 역할

**"두뇌"의 핵심 기능만**:
1. ✅ ActivityPub 인증 (AP2)
2. ✅ 전역 마스토돈 허브 (Federation)
3. ✅ 통합 정산 (전국 데이터 집계)
4. ✅ Sentinel 모니터링 (전체 시스템 감시)

### 기술 스택

```yaml
Infrastructure:
  Server: AWS Lambda (Serverless) or Google Cloud Run
  Database: PostgreSQL (Managed, 최소 용량)
  Cache: Redis (Global)
  
API:
  Framework: FastAPI
  Protocol: ActivityPub (Mastodon)
  Auth: AP2 (ActivityPub 2.0)
  
Monitoring:
  Sentinel: Real-time monitoring
  Logging: CloudWatch / Stackdriver
```

### 데이터 최소화

**중앙이 저장하는 것**:
- ✅ AP2 인증 토큰
- ✅ 전역 사용자 ID 매핑
- ✅ 월간 정산 요약 데이터
- ✅ 시스템 헬스 체크 로그

**중앙이 저장하지 않는 것**:
- ❌ 개별 주문 내역 (지역 DB에만)
- ❌ 개인 정보 상세 (지역 DB에만)
- ❌ 실시간 재고 (지역 캐시)

---

## 2️⃣ REGIONAL NODES (지역 노드) - Thick

### 역할

**"자율적 운영 단위"**:
1. ✅ 지역 Guardian 에이전트 운영
2. ✅ 지역 물류 DB 관리
3. ✅ 지역 캐시 (빠른 응답)
4. ✅ 중앙 장애 시 독립 운영 가능

### 기술 스택

```yaml
Infrastructure:
  Deployment: Docker Container (초기) → 물리 서버 (미래)
  Database: PostgreSQL (Local)
  Cache: Redis (Local)
  
Services:
  Guardian: Full stack
  Logistics: Regional DB
  Webhook: Local endpoints
  
Communication:
  Protocol: ActivityPub
  Federation: Mastodon instance
```

### 독립 운영 시나리오

**중앙 서버 장애 시**:
```python
# 지역 노드가 자동으로 전환
if not central_available():
    switch_to_local_mode()
    # 로컬 DB + 로컬 캐시로 운영
    # AP2 인증 → 로컬 백업 키 사용
    # 정산 → 로컬 큐에 쌓아두기
    # 중앙 복구 시 동기화
```

### 지역별 커스터마이징

**인제군**:
```yaml
specialty: 산나물, 약초
dialect: 강원도 사투리 (인제 특화)
delivery: A* 알고리즘 (산악 지형)
```

**춘천시**:
```yaml
specialty: 쌀, 닭갈비
dialect: 강원도 사투리 (춘천 특화)
delivery: 도심형 최적화
```

---

## 3️⃣ EDGE (엣지 디바이스) - Raspberry Pi

### 역할

**"최종 접점"**:
1. ✅ 어르신 음성 주문 (Whisper)
2. ✅ 사투리 인식 (DeepSeek)
3. ✅ AP2 위임장 서명
4. ✅ 마스토돈 통신

### 기술 스택

```yaml
Hardware:
  Device: Raspberry Pi 5 (8GB RAM)
  Storage: 64GB microSD + 256GB SSD
  
OS:
  Base: Raspberry Pi OS Lite (64-bit)
  Custom: "장승배기 OS" (경량 에이전트)
  
Services:
  Voice: Whisper (Base model)
  AI: DeepSeek-R1 (4-bit quantized)
  Cache: Local SQLite
  
Optimization:
  - GPU acceleration (35 layers)
  - Swap 사용 최소화
  - 오프라인 모드 지원
```

### 저사양 최적화

**메모리 관리**:
```python
# Raspberry Pi 5 메모리 할당
System: 1GB
DeepSeek: 4.2GB
Whisper: 300MB
Cache: 500MB
Available: 2GB (여유)
```

**응답 시간 목표**:
- 음성 인식: <120ms ✅
- 사투리 변환: <150ms ✅
- AP2 서명: <50ms ✅
- 마스토돈 포스팅: <200ms ✅

---

## 🔗 통신 체계: ActivityPub

### Why ActivityPub?

1. **표준 프로토콜**: W3C 표준
2. **Federation**: 자율적 인스턴스 연결
3. **확장성**: 전국 어디서든 참여 가능
4. **개방성**: 오픈소스, 투명

### 통신 구조

```
┌────────────────────────────────────────┐
│  Central Mastodon Instance             │
│  mastodon.mulberry.kr                  │
└────────────────────────────────────────┘
         ↕️ ActivityPub Federation
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ inje.        │  │ chuncheon.   │  │ buyeo.       │
│ mulberry.kr  │  │ mulberry.kr  │  │ mulberry.kr  │
└──────────────┘  └──────────────┘  └──────────────┘
```

### AP2 인증 흐름

```
1. Edge (RPI) → Regional Node
   - AP2 위임장 서명
   - 로컬 인증

2. Regional Node → Central
   - AP2 토큰 검증
   - 전역 권한 확인

3. Central → Regional Node
   - 인증 결과 반환
   - 캐시 업데이트
```

---

## 📊 확장 로드맵

### 1단계 (현재): 가상 분산

```yaml
Status: ✅ In Progress
Infrastructure:
  - Central: AWS Lambda
  - Regional: Docker Containers (AWS ECS)
  - Edge: Raspberry Pi 5
  
Features:
  - AP2 인증 체계
  - ActivityPub 통신
  - 가상 지역 노드
```

### 2단계 (3개월): 장승배기 OS

```yaml
Status: 🔄 Planned
Deliverable:
  - "장승배기 OS" (Lite Agent)
  - 완전 오프라인 모드
  - OTA 업데이트
  
Target:
  - 인제 100대 배포
  - 춘천 300대 준비
```

### 3단계 (6개월): 물리 서버 마이그레이션

```yaml
Status: 📋 Design
Strategy:
  - 지역별 물리 서버 설치
  - Docker → Bare Metal
  - 데이터 마이그레이션
  
Criteria:
  - 지역 노드 트래픽 > 10,000 req/day
  - 독립 운영 필요성 증가
```

---

## 🔒 보안 설계

### 계층별 보안

**Central**:
- AP2 인증 (OpenID Connect)
- TLS 1.3
- DDoS 방어 (CloudFlare)

**Regional**:
- 로컬 인증 백업
- VPN 터널 (WireGuard)
- 암호화 DB

**Edge**:
- 위임장 서명 (Ed25519)
- 로컬 키 스토어
- 최소 권한 원칙

---

## 💰 비용 최적화

### 예상 비용 (월간)

**1단계 (가상 분산)**:
```
Central Server: $50 (Lambda + RDS)
Regional Nodes: $100 (3개 지역 x ECS)
Edge Devices: $0 (자체 하드웨어)
Total: $150/month
```

**3단계 (물리 서버)**:
```
Central Server: $50 (변동 없음)
Regional Servers: $300 (3개 x $100)
Edge Devices: $0
Total: $350/month (지역 3개 기준)
```

**확장 시 (10개 지역)**:
```
Central Server: $50
Regional Servers: $1,000
Total: $1,050/month
```

**vs 중앙 집중식**:
```
Monolithic Server: $2,000/month (10개 지역)
Savings: $950/month (48% 절감)
```

---

## 🚀 실행 계획

### Week 1-2: 중앙 서버 구축

```bash
# 1. Central API
fastapi app --host 0.0.0.0 --port 8000

# 2. AP2 인증
python setup_ap2_auth.py

# 3. Mastodon 허브
docker-compose up mastodon
```

### Week 3-4: 지역 노드 배포

```bash
# 1. Docker 이미지 빌드
docker build -t mulberry-regional:1.0 .

# 2. 인제 배포
docker run -d --name inje-node mulberry-regional:1.0

# 3. 춘천 배포
docker run -d --name chuncheon-node mulberry-regional:1.0
```

### Week 5-6: 엣지 디바이스 최적화

```bash
# 1. 장승배기 OS 빌드
./build_jangseungbaegi_os.sh

# 2. RPI 플래싱
./flash_rpi.sh jangseungbaegi-os.img

# 3. OTA 설정
./setup_ota.sh
```

---

## 📞 결론

**"Thin Central, Thick Edge"**는 단순한 아키텍처가 아닙니다.

이것은:
- 🌍 **확장 가능성**: 전국 어디든 노드 추가
- 💪 **복원력**: 중앙 장애 시에도 운영
- 💰 **비용 효율**: 48% 비용 절감
- 🔐 **보안**: 계층별 독립 방어
- 🚀 **성능**: 지역 캐시로 빠른 응답

**Mulberry가 전국을 연결하는 방법입니다.** 🌾

---

<div align="center">

**🌾 Mulberry Platform v5.0.0**

**"Thin Central, Thick Edge"**

**설계 완료** ✅

</div>

---

**작성자**: Koda (CTO)  
**Reviewer**: Malu (전략)  
**Approver**: 대표님

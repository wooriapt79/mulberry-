# Co-op Buy 3레이어 아키텍처 — 파일럿 구조 확정

**작성**: KODA (CTO) | **Issue**: [mulberry- #8](https://github.com/wooriapt79/mulberry-/issues/8)
**날짜**: 2026-07-17 | **버전**: v1.0

---

## 1. 개요

Mulberry Lab 식품사막화 제로 프로젝트의 첫 번째 실행 모듈.
인제군 하나로마트 파트너십을 거점으로 카카오 Luna 채널을 통해 소비자 주문을 수집하고, 최소 수량 달성 시 자동 발주하는 공동구매 시스템.

---

## 2. 3레이어 구조

```
┌──────────────────────────────────────────────────┐
│  Layer 3 — 공동구매 실행                          │
│  카카오 Luna → 주문 수집 → 최소 수량 달성 → 발주  │
└─────────────────────┬────────────────────────────┘
                      │ 달성 알림
┌─────────────────────▼────────────────────────────┐
│  Layer 2 — 직소싱 (생산자 직접 연결)              │
│  감자 / 당근 / 쌀 / 배추 / 옥수수  (파일럿 5품목)│
└─────────────────────┬────────────────────────────┘
                      │ 재고 공급
┌─────────────────────▼────────────────────────────┐
│  Layer 1 — 하나로마트 파트너 (현장 유통)          │
│  기린면 하나로마트 / 인제읍 하나로마트             │
└──────────────────────────────────────────────────┘
```

### Layer 1 — 하나로마트 파트너

| 항목 | 내용 |
|------|------|
| 거점 | 기린면 하나로마트 / 인제읍 하나로마트 |
| 역할 | 현장 재고 보관 + 소비자 픽업 또는 로컬 배송 |
| 재고 업데이트 | 파일럿: 수동 업데이트 (Phase 2에서 API 자동화) |
| 연락처 관리 | `PRODUCT_DB` storePhone 필드 기준 |

### Layer 2 — 직소싱 (생산자 직접 연결)

| 품목 | 단위 | 기준가 | 최소 발주 수량 |
|------|------|--------|--------------|
| 강원도 기린면 감자 | 2kg | 8,000원 | 10세트 |
| 강원도 당근 | 1kg | 5,000원 | 15세트 |
| 인제 쌀 | 10kg | 35,000원 | 5세트 |
| 강원도 배추 | 1포기 | 6,000원 | 20세트 |
| 강원도 옥수수 | 3개 | 4,000원 | 20세트 |

### Layer 3 — 공동구매 실행

- 카카오 Luna 채널: 소비자 주문 접수 (utterance 기반)
- 주문 집계: MongoDB `CoopBuy` 컬렉션 (`mulberry-open-api`)
- 최소 수량 달성 감지 → 하나로마트 담당자 알림 자동 발송
- 미달 시: 다음 집계 사이클 대기 또는 환불 안내

---

## 3. 데이터 플로우

```
소비자
  │ 카카오 채널 메시지
  ▼
Luna (kakao.js)
  │ POST /api/coop-order
  ▼
Mission Control API (mulberry-open-api)
  │ MongoDB 주문 저장
  ▼
집계 엔진 (coop-buy.js)
  │ GET /api/coop-status (현황 조회)
  │
  ├─ [미달] → 대기 상태 유지
  │
  └─ [달성] POST /api/coop-notify
              │
              ▼
           하나로마트 담당자 (이메일 / 카카오 알림)
              │
              ▼
           생산자 발주 → 픽업/배송
```

---

## 4. API 명세 초안

### 4-1. 주문 접수

```
POST /api/coop-order
Content-Type: application/json

Request:
{
  "userId":     "kakao_user_id",
  "productId":  "p001",
  "quantity":   1,
  "channel":    "kakao"
}

Response 200:
{
  "orderId":    "ord_xxxx",
  "productId":  "p001",
  "status":     "pending",
  "currentQty": 7,
  "minQty":     10,
  "message":    "주문 접수 완료. 현재 7/10 달성 중입니다."
}
```

### 4-2. 공동구매 현황 조회

```
GET /api/coop-status?productId=p001

Response 200:
{
  "productId":  "p001",
  "name":       "강원도 기린면 감자",
  "currentQty": 7,
  "minQty":     10,
  "status":     "collecting",   // collecting | achieved | closed
  "deadline":   "2026-07-20T18:00:00Z"
}
```

### 4-3. 달성 알림 발송

```
POST /api/coop-notify
Content-Type: application/json

Request:
{
  "productId": "p001",
  "totalQty":  10,
  "orders":    [{ "userId": "...", "quantity": 1 }, ...]
}

Response 200:
{
  "notified": true,
  "channel":  "email",
  "sentTo":   "store-manager@hanaro.co.kr"
}
```

---

## 5. 파일럿 운영 시나리오

**시나리오: "인제군 기린면 감자 공동구매 1회차"**

| 단계 | 행동 | 담당 |
|------|------|------|
| 1 | Luna 카카오 채널에서 "감자" 키워드 → Commerce Card 표시 | Luna (자동) |
| 2 | 소비자 "구매" 버튼 클릭 → `/api/coop-order` 호출 | Luna → API |
| 3 | 주문 7건 집계 시 Luna가 "현재 7/10 달성 중" 안내 | API → Luna |
| 4 | 10건 달성 → `/api/coop-notify` 자동 실행 | API (자동) |
| 5 | 하나로마트 담당자 이메일 수신 → 생산자 발주 | 담당자 (수동) |
| 6 | 3~5일 내 픽업 또는 배송 완료 | 하나로마트 |

**파일럿 기간**: 2026년 8월 1일 ~ 8월 31일 (1개월)
**성공 기준**: 감자 1품목 최소 수량 달성 1회 + 실제 배송 완료

---

## 6. 구현 현황 (mulberry-open-api)

| 컴포넌트 | 파일 | 상태 |
|---------|------|------|
| 상품 DB | `routes/kakao.js` PRODUCT_DB | 완료 |
| Commerce Card | `routes/kakao.js` buildCommerceCard() | 완료 |
| Carousel | `routes/kakao.js` buildCarousel() | 완료 (v2.7.1) |
| 주문 접수 API | `routes/coop-buy.js` | 구현 중 |
| 현황 조회 API | `routes/coop-buy.js` | 구현 중 |
| 달성 알림 API | `routes/coop-buy.js` | 미구현 (Phase 2) |
| MongoDB 모델 | `models/coopBuy.js` | 완료 |

---

## 7. 다음 단계

- [ ] CEO 최종 승인
- [ ] `POST /api/coop-order` 구현 완료 (mulberry-open-api)
- [ ] `POST /api/coop-notify` 구현 (이메일 연동)
- [ ] Luna 주문 버튼 → API 연결 테스트
- [ ] 파일럿 운영 일정 확정 (하나로마트 담당자 연락)

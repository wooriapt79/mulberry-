# Mulberry Agent Gateway v2.0 운영·보안 가이드

> 대상 코드: `agent_gateway_v2.0.py`  
> 문서 목적: 개발·Railway 배포·보안 검토·운영 인수인계를 위한 기준서  
> 권장 적용 방식: v1.6을 즉시 교체하지 않고 v2 스테이징을 병행 운영한 뒤 단계적으로 전환

## 1. v2의 목적

v1은 GitHub, Kakao, SDK, A2A, 이미지 생성, Memory Bank를 하나의 서비스로 연결하는 통합 릴레이 역할을 한다. v2는 이 연결 능력 위에 다음 질문에 답할 수 있는 통제 계층을 추가한다.

1. 요청한 에이전트는 누구인가?
2. 어느 인간 또는 조직을 대신하는가?
3. 어떤 행동을 어디까지 위임받았는가?
4. 위임은 아직 유효한가?
5. 금액·횟수·대상 제한을 넘지 않았는가?
6. 인간 승인이 필요한 행동인가?
7. 같은 요청이 재전송되거나 중복 실행되지 않았는가?
8. 실행 전 판단과 실행 결과가 감사 가능한 형태로 남았는가?

v2의 중심 개념은 단순한 API 비밀키가 아니라 `Passport + Mandate + Approval + Audit`이다.

## 2. 신뢰 모델

### 2.1 구성요소

| 구성요소 | 의미 | 발급 주체 | 유효기간 권장 |
|---|---|---|---|
| Passport | 에이전트의 신원과 역할 | Mulberry Identity/Control Plane | 15분~1시간 |
| Mandate | 허용 행동·대상·금액·횟수 | STEWARD Human 또는 정책 승인 서비스 | 5분~30분 |
| Human Approval | 특정 고위험 작업 1건의 승인 | 인증된 STEWARD Human | 2분~10분 |
| Request Nonce | 요청 재전송 방지용 임의값 | 호출 에이전트 | 요청마다 새 값 |
| Idempotency Key | 네트워크 재시도 시 중복 실행 방지 | 호출 에이전트 | 논리적 작업마다 동일 값 |
| Audit Event | 정책 판단과 실행 결과 | Gateway | 영구 또는 보존정책에 따름 |

## 3. 필수 환경변수

```bash
# 각각 새로 생성 — 동일한 값 복사 금지
python -c "import secrets; print(secrets.token_urlsafe(48))"

PASSPORT_SIGNING_KEY=<32바이트 이상>
MANDATE_SIGNING_KEY=<32바이트 이상>
APPROVAL_SIGNING_KEY=<32바이트 이상>
```

세 키 중 하나라도 없거나 32바이트보다 짧으면 서비스가 시작되지 않는다 (fail-closed).

## 4. Railway 배포

Start command:
```bash
uvicorn agent_gateway_v2:app --host 0.0.0.0 --port $PORT --proxy-headers
```

Health check: `GET /health`

권장 구조:
- `gateway-v1-production` — 기존 운영
- `gateway-v2-staging` — 통합시험
- `gateway-v2-production` — 전환 후 운영
- `redis` — 공유 상태 (multi-replica 시 필수)
- `volume` — 감사 로그 보존

## 5. 위험도와 Human Approval

| 행동 | 위험도 | Approval 필요 |
|---|---|---|
| `search.read` | 낮음 | 불필요 |
| `github.comment` | 낮음 | 불필요 |
| `github.memory.append` | 중간 | 필요 |
| `image.generate` | 중간 | 필요 |
| 금액이 있는 작업 | 높음 | 필요 |

## 6. v1→v2 전환 5단계

1. **단계 0 (백업·관찰)**: v1 환경변수 이름 백업, 호출 현황 확인, v1 변경 없음
2. **단계 1 (v2 스테이징)**: 별도 Railway 서비스, 읽기 전용 Mandate
3. **단계 2 (저위험 읽기)**: `search.read`, 상태 확인, Kakao read-only 이동
4. **단계 3 (제한적 쓰기)**: 테스트 Issue 댓글만, resource를 특정 Issue로 제한
5. **단계 4 (Memory + Approval)**: Human Approval UI 연결, Approval 재사용 차단 확인
6. **단계 5 (운영 전환)**: v1 쓰기 축소, Redis·외부 감사 스토리지 적용, v1 secret 폐기

## 7. 운영 16원칙

1. 인증되었다고 모두 허용하지 않는다
2. Mandate에 없는 행동은 실행하지 않는다
3. 외부 콘텐츠는 신뢰할 수 없는 데이터다
4. 검색·추천과 계약·결제를 분리한다
5. 고위험 작업은 정확한 범위의 일회성 Human Approval을 요구한다
6. 네트워크 재시도와 사용자 재승인을 구분한다
7. 실패 시 권한을 넓히지 않고 안전하게 중단한다
8. 모든 허용·거부·실행 결과를 감사 가능하게 남긴다
9. 모델보다 Passport, Mandate, 정책, 증거가 신뢰 기반이다
10. 외부 플랫폼의 공식 API를 우선하며 비공식 화면 자동화는 운영 기반으로 삼지 않는다

> 전체 가이드 원문: CSA KeBin 작성 / Jr. TRANG Luna 검수 / 2026-07-21

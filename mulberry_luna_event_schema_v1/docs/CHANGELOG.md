# Luna Event Schema — CHANGELOG

---

## v1.1 (2026-07-20) — CSA Kbin 설계 반영

**Issue #9** | Branch: `koda/issue9-schema-v1-1`
설계 검토: CSA Kbin (`REVIEW_Sr_TRANG.md` / `docs/v1_1_spec_draft.md`)

### 신규 필드

| 필드명 | 타입 | 설명 |
|---|---|---|
| `raw_input` | string\|null (max 4096) | 원문 입력 — 개인정보 마스킹 후 저장. AI 학습 데이터 활용 |
| `failure_category` | enum\|null | 실패 대분류: SEARCH / API / NETWORK / PAYMENT / USER / SYSTEM |
| `workflow_id` | string\|null | 워크플로우 고유 ID — 동일 태스크 이벤트 묶음 추적 |
| `step_no` | integer\|null | 워크플로우 내 단계 번호 (1, 2, 3...) |
| `step_name` | string\|null | 단계명 (예: 메시지수신, 상품조회, 가격확인, 주문확정) |
| `delegated_from` | enum\|null | 이 이벤트를 위임한 Agent |
| `delegated_to` | enum\|null | 다음으로 위임할 Agent |

### 필드 변경

| 필드명 | v1.0 | v1.1 |
|---|---|---|
| `input_summary` | maxLength 1000 | maxLength 4096 |
| `output_summary` | maxLength 2000 | maxLength 4096 |
| `failure_code` | enum 고정 | 자유 문자열 확장 (카테고리와 분리) |
| `confidence` | metadata 내부 | 최상위 필드로 격상 |
| `response_time_ms` | metadata 내부 | 최상위 필드로 격상 |
| `adapter_version` | metadata 내부 | 최상위 필드로 격상 |

### schema_version 변경

- v1.0: `"const": "1.0"`
- v1.1: `"const": "1.1"` — 마이그레이션 감지 가능

### 추가 파일

- `examples/workflow_coop_full_trace.json` — 4-step 공동구매 워크플로우 전체 추적 예시
- `examples/human_escalation.json` — CEO 승인 요청 (환불 에스컬레이션) 예시

---

## v1.0 (2026-07-19) — 초기 릴리즈

Mulberry Luna Common Event 스키마 초안.

### 포함 내용

- 필수 필드: `schema_version`, `event_id`, `task_id`, `timestamp`, `channel`, `agent`, `event_type`, `status`
- 채널: kakao, cowork, search, web, api, internal
- Agent: kakao_luna, search_luna, cowork_luna, gateway, human
- 실패 코드: enum 고정 방식
- metadata 14-key 표준 (confidence, response_time_ms, adapter_version 포함)

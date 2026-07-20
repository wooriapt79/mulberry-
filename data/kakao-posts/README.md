# data/kakao-posts/ — Mulberry 카카오 소식 데이터 저장소

카카오 채널 '소식' 메뉴 포스팅 데이터를 JSON으로 저장합니다.
Luna RAG 시스템이 이 데이터를 참조해 사용자 질문에 답변합니다.

## 폴더 구조

```
data/kakao-posts/
├── coop-buy/       # 공동구매 안내 (intent: coop_request, product_inquiry)
├── events/         # 이벤트·행사 공지 (intent: event_inquiry, schedule_inquiry)
├── notices/        # 서비스 공지 (intent: notice_inquiry, service_inquiry)
└── producers/      # 생산자 소개 (intent: producer_inquiry)
```

## JSON 파일 명명 규칙

```
{YYYY-MM-DD}-{slug}.json
예: 2026-07-20-blueberry-paju.json
```

## 필수 필드

| 필드 | 설명 |
|---|---|
| `schema_version` | 현재 "1.0" |
| `post_id` | 고유 ID (카테고리-날짜-순번) |
| `category` | 폴더명과 일치 |
| `intent_tags` | Luna 라우팅용 의도 태그 배열 |
| `title` | 포스팅 제목 |
| `content` | 전체 본문 |
| `summary` | AI 요약 (Luna 프롬프트 삽입용, 200자 이내 권장) |
| `date` | 포스팅 날짜 (YYYY-MM-DD) |
| `author` | 작성자 (KODA / re.eul) |
| `status` | active / upcoming / published / closed |

## 데이터 작성 권한

- **re.eul 대표이사**: 직접 md/json commit 가능
- **KODA**: 자동화 스크립트로 commit
- commit 후 다음 fetch 주기(6시간)에 Luna 자동 반영

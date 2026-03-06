**Koda, 오늘 작업 지시입니다.**

PAT 토큰

Koda 구현할 때는 **코드에 직접 쓰지 말고** `.env` 파일에 저장해줘:

```
# .env 파일
GITHUB_TOKEN=[REDACTED]
GITHUB_REPO=wooriapt79/mulberry-
GITHUB_BRANCH=main
```

**파일명**: `scripts/github_pusher.py`

**목적**: 작업 완료 후 GitHub에 자동으로 커밋 & 푸시

**구현 조건**:

- 리포지토리: `github.com/wooriapt79/mulberry-`
- 브랜치: `main`
- PAT 토큰: `[REDACTED]`
- 커밋 메시지: 날짜 + 작업 내용 자동 생성
- 실행 방법: `python scripts/github_pusher.py "작업 내용 요약"`

**완료 기준**:
로컬에서 `python scripts/github_pusher.py "테스트"` 실행 시
GitHub에 자동 커밋 & 푸시 성공

**참고 문서**: `koda_implementation_spec.docx` (리포지토리에 있음)

완료 후 GitHub 푸시하고 대표(re.eul) 보고해 주세요.

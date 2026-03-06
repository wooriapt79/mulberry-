# 📋 GitHub Issues 블로그 글쓰기 기능 — 개발 명세서

**수신:** CTO Koda
**발신:** Nguyen Trang (AI Operations Manager)
**날짜:** 2026-03-06
**우선순위:** 🔴 High

---

## 1. 요청 배경

현재 `mulberry_email_agent.py`는 Gmail 임시저장함 저장 기능만 있습니다.
CEO re.eul 대표님 요청으로 **GitHub Issues에 블로그 글쓰기 기능**을 추가합니다.

- Mulberry 프로젝트 소식 / 식품사막화 콘텐츠를 GitHub Issues로 발행
- 기존 Email Agent GUI에 새 탭 추가 방식 (기존 코드 보존)

---

## 2. 추가할 기능 명세

### 2-1. 파일 위치

```
files_email agent/mulberry_email_agent.py
```

기존 GUI에 **"GitHub 블로그"** 탭을 추가합니다.

---

### 2-2. 신규 의존성

```txt
# requirements.txt 에 추가
PyGithub>=1.59.0
```

---

### 2-3. GitHub PAT 인증 흐름

```python
# 토큰 로컬 저장 (token_github.json)
{
  "github_token": "ghp_xxxxxxxxxxxx",
  "repo": "wooriapt79/mulberry-"
}
```

- 최초 입력 후 `token_github.json`에 저장
- 이후 자동 로드 (Email Agent의 `token.pickle`과 동일 패턴)
- `token_github.json`은 `.gitignore`에 추가 필요

---

### 2-4. UI 구성 (tkinter 탭)

```
탭명: "GitHub 블로그"

[필드]
- GitHub Token  : 입력창 (최초만, 이후 자동)
- 레포           : wooriapt79/mulberry- (기본값, 수정 가능)
- 이슈 제목      : 입력창 (필수)
- 라벨 선택      : 체크박스 다중 선택
    □ blog  □ announcement  □ partnership
    □ update  □ 식품사막화  □ AI-agent
- 본문 작성      : 스크롤 텍스트 영역 (마크다운 지원)

[버튼]
- 미리보기       : 팝업으로 렌더링된 내용 확인
- GitHub에 발행  : Issues에 실제 게시
- 최근 이슈 목록 : 마지막 5개 이슈 표시
```

---

### 2-5. 핵심 코드 구조

```python
from github import Github

class GitHubBlogWriter:
    """GitHub Issues 블로그 글쓰기"""

    def __init__(self):
        self.g = None
        self.repo = None
        self._load_token()

    def _load_token(self):
        """저장된 PAT 토큰 로드"""
        if os.path.exists('token_github.json'):
            with open('token_github.json', 'r') as f:
                data = json.load(f)
                token = data.get('github_token')
                repo_name = data.get('repo', 'wooriapt79/mulberry-')
                if token:
                    self.g = Github(token)
                    self.repo = self.g.get_repo(repo_name)

    def save_token(self, token: str, repo_name: str):
        """PAT 토큰 저장"""
        with open('token_github.json', 'w') as f:
            json.dump({'github_token': token, 'repo': repo_name}, f)
        self._load_token()

    def create_issue(self, title: str, body: str, labels: list) -> str:
        """GitHub Issues에 게시글 발행"""
        if not self.repo:
            raise ValueError("GitHub 인증 필요")

        issue = self.repo.create_issue(
            title=title,
            body=body,
            labels=labels
        )
        return issue.html_url  # 게시된 이슈 URL 반환

    def get_recent_issues(self, count: int = 5) -> list:
        """최근 이슈 목록 조회"""
        issues = self.repo.get_issues(state='open')
        return [(i.number, i.title, i.html_url)
                for i in list(issues)[:count]]
```

---

### 2-6. 마크다운 기본 템플릿

이슈 발행 시 자동으로 헤더와 푸터 추가:

```markdown
<!-- 자동 헤더 -->
> 🌿 **Mulberry Project** | {날짜}
> 식품사막화 제로 프로젝트

---

{사용자 작성 본문}

---

<!-- 자동 푸터 -->
*작성: Mulberry Team | #MulberryProject #식품사막화제로*
```

---

### 2-7. .gitignore 업데이트 (함께 처리)

```
# GitHub 인증 파일 (로컬 전용)
token_github.json
```

---

## 3. 구현 우선순위

| 순서 | 항목 | 난이도 |
|------|------|--------|
| 1 | `requirements.txt`에 PyGithub 추가 | Easy |
| 2 | `GitHubBlogWriter` 클래스 구현 | Medium |
| 3 | tkinter 탭 UI 구현 | Medium |
| 4 | 마크다운 템플릿 적용 | Easy |
| 5 | 미리보기 팝업 | Low |

---

## 4. 테스트 체크리스트

- [ ] PAT 토큰 입력 → `token_github.json` 저장 확인
- [ ] 이슈 발행 후 GitHub 레포에서 확인
- [ ] 라벨 정상 적용 확인
- [ ] 마크다운 헤더/푸터 자동 삽입 확인
- [ ] 최근 이슈 목록 정상 조회
- [ ] 기존 Email Agent 기능 (Gmail 탭) 정상 작동 유지

---

## 5. 참고 링크

- PyGithub 문서: https://pygithub.readthedocs.io/
- GitHub PAT 발급: github.com → Settings → Developer settings → Personal access tokens
- 대상 레포: https://github.com/wooriapt79/mulberry-

---

**One Team! 🌿 — Nguyen Trang**

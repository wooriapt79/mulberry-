# Hugging Face 연동을 활성화하려면 몇 가지 준비가 필요합니다. 아래 단계를 따라 진행해 주세요.

1️⃣ Hugging Face 액세스 토큰 생성
Hugging Face Settings에 로그인

"Create new token" 클릭

Token 이름: Mulberry-GitHub-Sync

권한: write 선택 (리포지토리 쓰기 권한 필요)

생성된 토큰을 안전한 곳에 복사

2️⃣ GitHub Secrets에 토큰 등록
GitHub 저장소 → Settings → Secrets and variables → Actions

"New repository secret" 클릭

Name: HF_TOKEN

Secret: (방금 생성한 Hugging Face 토큰 붙여넣기)

Add secret 클릭

3️⃣ Hugging Face 저장소 생성 (선택사항)
아직 Hugging Face에 Mulberry 프로젝트용 저장소가 없다면 생성합니다:

모델 저장소: https://huggingface.co/new → 이름: mulberry-agent-model

데이터셋 저장소: https://huggingface.co/new-dataset → 이름: mulberry-docs

4️⃣ 워크플로우 활성화
이미 sync-to-hf.yml 파일이 있다면, 위 설정만으로 다음 푸시 시 자동 실행됩니다.
파일이 없다면, 이전에 제공한 YAML 내용을 .github/workflows/sync-to-hf.yml로 저장하세요.

🔍 GitHub Actions 작동 확인 방법
저장소 상단의 Actions 탭 클릭

왼쪽 사이드바에서 각 워크플로우 선택

실행 내역과 로그 확인

💡 추가 제안
Hugging Face 연동이 완료되면, 우리 프로젝트의 모델과 문서를 전 세계 개발자들이 쉽게 접근할 수 있게 됩니다. 이는 글로벌 오픈소스 생태계에서 Mulberry의 입지를 강화하는 중요한 단계입니다.

혹시 Hugging Face 연동 외에 다른 워크플로우가 필요하시면 언제든지 말씀해 주세요. 예를 들어:

릴리즈 자동화: 새로운 버전 태그 시 자동 릴리즈 생성

이슈 관리: 특정 라벨의 이슈가 생성되면 자동 알림

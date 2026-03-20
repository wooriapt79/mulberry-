# 🌿 Mulberry Insurance Orchestrator AI Agent

![Mulberry Logo](mulberry_logo.png)

[![English](https://img.shields.io/badge/Language-English-blue?style=flat-square)](README_en.md) [![Korean](https://img.shields.io/badge/Language-Korean-red?style=flat-square)](README_ko.md) [![Vietnamese](https://img.shields.io/badge/Language-Vietnamese-green?style=flat-square)](README_vi.md)

[![Hugging Face Spaces](https://img.shields.io/badge/Hugging_Face-Spaces-blue?style=flat-square&logo=huggingface&logoColor=white)](https://huggingface.co/spaces/re-eul/mulberry-demo) [![Server Status](https://img.shields.io/badge/Server-Live-brightgreen?style=flat-square)](https://mulberry-open-api-production.up.railway.app/)

## 프로젝트 설명
`Mulberry Insurance Orchestrator`는 보험 청구 처리 워크플로우를 자동화하고 간소화하도록 설계된 AI 기반 에이전트입니다. 이 에이전트는 다양한 구성 요소를 통합하여 의료 기록을 수집하고, 관련 데이터를 추출하며, 보험 정책 보장을 확인하고, 사용자 승인을 촉진하며, 여러 채널(API, PDF, 팩스)을 통해 보험사에 청구를 제출합니다.

## 기능
-   **자동화된 데이터 수집:** 의료 서비스 제공자로부터 원시 의료 기록을 수집합니다.
-   **지능형 데이터 추출:** NLP 및 정규식을 사용하여 비정형 의료 문서를 구조화된 '골드' 데이터 형식으로 변환합니다.
-   **동적 정책 보장 확인:** 보험 정책에 대해 청구를 평가하고, 공제액, 본인 부담금 및 예상 환급액을 계산합니다.
-   **인간 개입 승인:** 투명성과 동의를 보장하기 위해 제출 전에 정책 보유자(User A)가 생성된 청구 보고서를 확인하도록 요구합니다.
-   **유연한 청구 제출:** 보험사 기능에 따라 제출 방법을 조정합니다.
    -   최신 보험사를 위한 직접 API 통합.
    -   전통적이거나 보수적인 보험사를 위한 자동 PDF 생성 및 팩스 제출.

## 프로젝트 구조
```
mulberry-insurance-orchestrator/
├── .env                 # 환경 변수 구성
├── requirements.txt     # Python 종속성
├── src/
│   ├── __init__.py      # src를 Python 패키지로 표시
│   ├── user.py          # 청구 승인 로직을 위한 UserA 클래스 정의
│   ├── hospital.py      # 의료 기록 수집을 위한 HospitalB 클래스 정의
│   ├── insurer.py       # 보험사 세부 정보(API 기능)를 위한 Insurer 클래스 정의
│   ├── mulberry_mind.py # 데이터 추출, 정책 확인 및 제출 방법을 위한 MulberryMind 로직 포함
│   ├── orchestrator.py  # 메인 오케스트레이터 로직 (InsuranceClaimOrchestrator)
│   ├── settings.py      # 애플리케이션 구성을 위한 Pydantic BaseSettings
│   └── main.py          # 엔드투엔드 시나리오 실행 예제 스크립트
└── tests/
    └── test_orchestrator.py # InsuranceClaimOrchestrator에 대한 단위 테스트
```

## 설치

1.  **리포지토리 클론:**
    ```bash
    git clone [your-github-repo-url]
    cd mulberry-insurance-orchestrator
    ```

2.  **가상 환경 생성 (권장):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows에서는 `venv\\Scripts\\activate` 사용
    ```

3.  **종속성 설치:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **환경 변수 설정:**
    루트 디렉토리에 `.env` 파일을 생성하고 구성 정보를 입력합니다. 참조를 위해 `.env` 파일 예시가 프로젝트 구조에 제공됩니다.

    ```ini
    APP_NAME="Mulberry Insurance Orchestrator Dev"
    DEBUG=True

    API_INSURER_URL="https://dev.api.insurer.com/v1/claims"
    API_INSURER_API_KEY="dev-api-key-123"

    FAX_FROM_NUMBER="+15551234567" # Twilio 번호
    FAX_TO_NUMBER="+821098765432" # 수신 팩스 번호
    TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # Twilio 계정 SID
    TWILIO_AUTH_TOKEN="your_twilio_auth_token" # Twilio 인증 토큰

    MCCC_WEBHOOK_URL="https://dev.mccc.mulberry.com/webhook/approval"
    ```
    *참고: 실제 팩스 기능을 사용하려면 Twilio 계정과 PDF 미디어에 대한 공개적으로 액세스 가능한 URL이 필요합니다. 현재 `send_auto_fax` 함수는 플레이스홀더 URL을 사용합니다.*

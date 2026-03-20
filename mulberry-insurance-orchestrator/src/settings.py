from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Mulberry 기본 설정
    APP_NAME: str = "Mulberry Insurance Orchestrator"
    DEBUG: bool = False

    # 보험사 API 설정
    API_INSURER_URL: str = "https://api.insurer.com/v1/claims"
    API_INSURER_API_KEY: str = "dummy-key"

    # 팩스 설정 (예: Twilio Fax)
    FAX_FROM_NUMBER: str = "+1234567890"
    FAX_TO_NUMBER: str = "+821012345678"
    TWILIO_ACCOUNT_SID: str = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    TWILIO_AUTH_TOKEN: str = "your_twilio_auth_token"

    # Mulberry Control Center 연동
    MCCC_WEBHOOK_URL: str = "https://mccc.mulberry.com/webhook/approval"

    class Config:
        env_file = ".env"

print("src/settings.py created with the Pydantic Settings class.")

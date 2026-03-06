"""
Mulberry Phase 1 - Configuration Management
Pydantic Settings를 사용한 환경변수 관리
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, validator


class Settings(BaseSettings):
    """Application Configuration"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ============================================
    # Application Settings
    # ============================================
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    
    # CORS Origins
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        alias="CORS_ORIGINS"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # ============================================
    # Database Configuration
    # ============================================
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="mulberry", alias="DB_NAME")
    db_user: str = Field(default="mulberry_user", alias="DB_USER")
    db_password: str = Field(default="", alias="DB_PASSWORD")
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @property
    def async_database_url(self) -> str:
        """Construct async PostgreSQL connection URL"""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    # ============================================
    # Mastodon Configuration
    # ============================================
    mastodon_instance_url: str = Field(
        default="https://mastodon.social",
        alias="MASTODON_INSTANCE_URL"
    )
    mastodon_client_id: str = Field(default="", alias="MASTODON_CLIENT_ID")
    mastodon_client_secret: str = Field(default="", alias="MASTODON_CLIENT_SECRET")
    mastodon_access_token: str = Field(default="", alias="MASTODON_ACCESS_TOKEN")
    
    mastodon_hashtags: str = Field(
        default="#Mulberry_재고,#Mulberry_핫딜",
        alias="MASTODON_HASHTAGS"
    )
    
    @property
    def mastodon_hashtags_list(self) -> List[str]:
        """Convert comma-separated hashtags to list"""
        return [tag.strip() for tag in self.mastodon_hashtags.split(",")]
    
    mastodon_stream_reconnect_wait_sec: int = Field(
        default=5,
        alias="MASTODON_STREAM_RECONNECT_ASYNC_WAIT_SEC"
    )
    
    # ============================================
    # Qwen 2.5 API Configuration
    # ============================================
    qwen_api_key: str = Field(default="", alias="QWEN_API_KEY")
    qwen_api_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        alias="QWEN_API_BASE_URL"
    )
    qwen_model: str = Field(default="qwen-max", alias="QWEN_MODEL")
    qwen_timeout_seconds: int = Field(default=30, alias="QWEN_TIMEOUT_SECONDS")
    qwen_max_retries: int = Field(default=3, alias="QWEN_MAX_RETRIES")
    
    # ============================================
    # Redis Configuration
    # ============================================
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: str = Field(default="", alias="REDIS_PASSWORD")
    
    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # ============================================
    # Logging Configuration
    # ============================================
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    log_file_path: str = Field(default="logs/mulberry.log", alias="LOG_FILE_PATH")
    
    # ============================================
    # Business Logic Settings
    # ============================================
    hot_deal_min_farms: int = Field(default=3, alias="HOT_DEAL_MIN_FARMS")
    hot_deal_min_quantity: int = Field(default=100, alias="HOT_DEAL_MIN_QUANTITY")
    
    food_desert_radius_km: float = Field(default=5.0, alias="FOOD_DESERT_RADIUS_KM")
    
    delivery_base_fee: int = Field(default=3000, alias="DELIVERY_BASE_FEE")
    delivery_free_threshold: int = Field(default=30000, alias="DELIVERY_FREE_THRESHOLD")
    
    # ============================================
    # AI Agent Settings
    # ============================================
    orchestrator_scan_interval_minutes: int = Field(
        default=60,
        alias="ORCHESTRATOR_SCAN_INTERVAL_MINUTES"
    )
    policy_report_schedule_cron: str = Field(
        default="0 0 1 * *",
        alias="POLICY_REPORT_SCHEDULE_CRON"
    )
    
    # ============================================
    # Google Services Configuration
    # ============================================
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    google_oauth_client_id: str = Field(default="", alias="GOOGLE_OAUTH_CLIENT_ID")
    google_oauth_client_secret: str = Field(default="", alias="GOOGLE_OAUTH_CLIENT_SECRET")
    google_business_account_id: str = Field(default="", alias="GOOGLE_BUSINESS_ACCOUNT_ID")
    
    # Google Pay Configuration
    google_pay_merchant_id: str = Field(default="", alias="GOOGLE_PAY_MERCHANT_ID")
    google_pay_merchant_name: str = Field(default="Mulberry Platform", alias="GOOGLE_PAY_MERCHANT_NAME")
    google_pay_environment: str = Field(default="TEST", alias="GOOGLE_PAY_ENVIRONMENT")  # TEST or PRODUCTION
    
    # ============================================
    # Payment Configuration
    # ============================================
    payment_currency: str = Field(default="KRW", alias="PAYMENT_CURRENCY")
    payment_min_amount: int = Field(default=1000, alias="PAYMENT_MIN_AMOUNT")
    payment_max_amount: int = Field(default=10000000, alias="PAYMENT_MAX_AMOUNT")
    
    # Agent-to-Agent Payment (AP2)
    ap2_enabled: bool = Field(default=False, alias="AP2_ENABLED")
    ap2_settlement_interval_hours: int = Field(default=24, alias="AP2_SETTLEMENT_INTERVAL_HOURS")
    
    # ============================================
    # Reservation Configuration
    # ============================================
    reservation_advance_days: int = Field(default=7, alias="RESERVATION_ADVANCE_DAYS")
    reservation_max_items: int = Field(default=20, alias="RESERVATION_MAX_ITEMS")
    reservation_auto_confirm_minutes: int = Field(default=30, alias="RESERVATION_AUTO_CONFIRM_MINUTES")
    
    # ============================================
    # Security
    # ============================================
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        alias="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency injection용 설정 getter
    FastAPI의 Depends()와 함께 사용
    """
    return settings


if __name__ == "__main__":
    # Configuration test
    print("=== Mulberry Configuration ===")
    print(f"Environment: {settings.app_env}")
    print(f"Database URL: {settings.database_url}")
    print(f"Mastodon Instance: {settings.mastodon_instance_url}")
    print(f"Mastodon Hashtags: {settings.mastodon_hashtags_list}")
    print(f"Qwen Model: {settings.qwen_model}")
    print(f"Redis URL: {settings.redis_url}")
    print(f"CORS Origins: {settings.cors_origins_list}")

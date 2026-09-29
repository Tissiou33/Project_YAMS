from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Igname Express API"
    env: str = "dev"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://igname:igname@db:5432/igname"
    redis_url: str | None = None  # None -> stockage OTP en mémoire (dev/tests)
    auto_create_tables: bool = True  # dev uniquement ; en prod -> Alembic

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    refresh_token_days: int = 14

    otp_length: int = 6
    otp_ttl_seconds: int = 300
    otp_max_attempts: int = 5
    otp_request_cooldown_seconds: int = 60
    max_failed_logins: int = 5
    lock_minutes: int = 15

    # Règles métier par défaut (surchargeables via PlatformSetting)
    commission_rate: float = 0.08
    delivery_base_fee: int = 1000        # FCFA
    delivery_fee_per_km: int = 150       # FCFA
    delivery_express_multiplier: float = 1.5
    delivery_rural_multiplier: float = 1.3

    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

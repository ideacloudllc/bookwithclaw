"""Configuration for BookWithClaw Exchange."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Exchange configuration from environment variables."""

    # Database
    database_url: str

    # Redis
    redis_url: str

    # Exchange
    exchange_secret_key: str  # 32-byte hex secret for JWT signing
    exchange_host: str = "localhost"
    exchange_port: int = 8000
    environment: str = "development"  # development | production

    # Stripe Connect
    stripe_secret_key: str
    stripe_webhook_secret: str
    stripe_platform_account: str

    # SendGrid
    sendgrid_api_key: str
    sendgrid_from_email: str = "notifications@bookwithclaw.com"

    # Exchange fee (basis points - 180 = 1.80%)
    platform_fee_bps: int = 180

    # Session timeouts (seconds)
    session_open_timeout: int = 30
    session_negotiation_timeout: int = 120
    session_settlement_timeout: int = 30

    # Order book
    order_book_ttl_seconds: int = 3600
    max_intents_per_minute: int = 10
    max_asks_per_minute: int = 50
    max_negotiation_rounds: int = 10

    class Config:
        env_file = "../../.env"
        case_sensitive = False


settings = Settings()

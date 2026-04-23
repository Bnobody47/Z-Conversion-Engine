from __future__ import annotations

import os


class Settings:
    app_env: str = os.getenv("APP_ENV", "dev")
    default_timezone: str = os.getenv("DEFAULT_TIMEZONE", "UTC")
    enable_live_sending: bool = os.getenv("ENABLE_LIVE_SENDING", "false").lower() == "true"
    tenacious_outbound_enabled: bool = os.getenv("TENACIOUS_OUTBOUND_ENABLED", "").lower() == "true"
    seed_repo_path: str = os.getenv(
        "SEED_REPO_PATH",
        r"c:\Users\Bnobody_47\Downloads\tenacious_sales_data\tenacious_sales_data",
    )
    email_provider: str = os.getenv("EMAIL_PROVIDER", "resend").lower()
    resend_api_key: str = os.getenv("RESEND_API_KEY", "")
    mailersend_api_key: str = os.getenv("MAILERSEND_API_KEY", "")
    email_from: str = os.getenv("EMAIL_FROM", "draft@gettenacious.com")
    africastalking_username: str = os.getenv("AFRICASTALKING_USERNAME", "")
    africastalking_api_key: str = os.getenv("AFRICASTALKING_API_KEY", "")
    hubspot_access_token: str = os.getenv("HUBSPOT_ACCESS_TOKEN", "")


settings = Settings()

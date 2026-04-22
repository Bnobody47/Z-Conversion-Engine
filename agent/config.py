from __future__ import annotations

import os


class Settings:
    app_env: str = os.getenv("APP_ENV", "dev")
    default_timezone: str = os.getenv("DEFAULT_TIMEZONE", "UTC")
    enable_live_sending: bool = os.getenv("ENABLE_LIVE_SENDING", "false").lower() == "true"


settings = Settings()

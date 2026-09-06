from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class EnvFileLoader(BaseSettings):
    """
    Configuration class that inherits from BaseSettings.
    It is designed to ONLY load environment variables from a .env file.
    This way, we can have multiple configuration classes that STORE different environment variables.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class SrcSetting(EnvFileLoader):
    DB_URL: str

    # development | production. Controls HSTS and can drive other prod-only behavior.
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    # console | json. Use "json" for log aggregators (Datadog, Loki, CloudWatch, ...).
    LOG_FORMAT: str = "console"

    # Comma-separated list of allowed CORS origins (empty = CORS disabled).
    CORS_ORIGINS: str = ""


src_setting = SrcSetting()

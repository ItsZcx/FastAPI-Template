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


src_setting = SrcSetting()

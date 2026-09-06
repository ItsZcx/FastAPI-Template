# auth-specific config/constants
from src.core.config import EnvFileLoader


class AuthSetting(EnvFileLoader):
    AUTH_SECRET_KEY: str
    AUTH_ALGORITHM: str = "HS256"
    AUTH_TOKEN_EXPIRE_MINUTES: int = 60


auth_setting = AuthSetting()

# package-specific config/constants
from src.config import EnvFileLoader


class PackageSetting(EnvFileLoader):
    CUSTOM_ENV_VAR: str


package_setting = PackageSetting()

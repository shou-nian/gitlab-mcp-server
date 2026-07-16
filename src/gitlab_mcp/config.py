"""应用配置。"""

from functools import cached_property

from pydantic import Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """从环境变量和可选的 .env 文件加载 GitLab 配置。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    gitlab_url: HttpUrl
    gitlab_token: SecretStr
    gitlab_timeout: float = Field(default=30.0, gt=0)
    log_level: str = "INFO"

    @cached_property
    def gitlab_api_url(self) -> str:
        """返回不带尾斜杠的 GitLab v4 API 地址。"""

        return f"{str(self.gitlab_url).rstrip('/')}/api/v4"

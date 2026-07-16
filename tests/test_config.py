"""配置模块测试。"""

from pydantic import SecretStr

from gitlab_mcp.config import Settings


def test_settings_load_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("GITLAB_URL", "https://gitlab.example.com/")
    monkeypatch.setenv("GITLAB_TOKEN", "secret-token")
    monkeypatch.setenv("GITLAB_TIMEOUT", "12.5")
    monkeypatch.setenv("LOG_LEVEL", "debug")

    settings = Settings(_env_file=None)

    assert settings.gitlab_api_url == "https://gitlab.example.com/api/v4"
    assert settings.gitlab_token == SecretStr("secret-token")
    assert settings.gitlab_timeout == 12.5
    assert settings.log_level == "debug"


def test_secret_token_is_masked() -> None:
    settings = Settings(
        gitlab_url="https://gitlab.example.com",
        gitlab_token="secret-token",
        _env_file=None,
    )

    assert "secret-token" not in repr(settings)

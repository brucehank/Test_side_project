import logging
import os
from typing import List

import pytest

from utils.config_toml import (
    ClientCommonConfig,
    ClientConfig,
    EnvConfig,
    get_config,
)

log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def env_name(request):
    markexpr = getattr(request.config.option, "markexpr", "") or ""
    m = str(markexpr).strip().lower()
    if m in {"dev", "prod"}:
        return m
    raise pytest.UsageError(
        f"無法判斷環境，請用 -m dev or prod 執行測試（目前為: {markexpr!r}）。"
    )


@pytest.fixture(scope="session")
def get_env_config(env_name):
    # 透過 Env 標記載入對應的 TOML 設定 (e.g., dev.toml / prod.toml)
    return get_config(EnvConfig, env=env_name)


@pytest.fixture(scope="session")
def client_common_config(get_env_config: EnvConfig):
    return get_env_config.client_common


@pytest.fixture(scope="session")
def all_clients(get_env_config: EnvConfig):
    return get_env_config.clients


@pytest.fixture(scope="session")
def user_config(request, all_clients: List[ClientConfig]):
    user_tag = request.config.getoption("--user")
    selected = None
    if user_tag and user_tag != "null":
        for c in all_clients:
            if c.name.lower() == str(user_tag).lower():
                selected = c
                break
    if selected is None:
        selected = all_clients[0]
        log.debug("--user 未指定或找不到；使用第一個客戶端: %s", selected.name)
    return selected


@pytest.fixture(scope="session")
def user_token(user_config: ClientConfig):
    token = (user_config.access_token or "").strip()
    if not token:
        token = os.getenv("TEST_ACCESS_TOKEN", "").strip()
    if not token:
        raise pytest.UsageError(
            "缺少 access token：請在 config/<env>.toml 的 clients[].access_token 填入，"
            "或設定環境變數 TEST_ACCESS_TOKEN。"
        )
    return token

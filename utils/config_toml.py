from __future__ import annotations

import tomllib  # Python 3.11+ 標準庫
from pathlib import Path
from typing import Literal, Type, TypeVar, cast

from pydantic import AnyUrl, BaseModel, ConfigDict, ValidationError


# ----- Common 環境設定（/config/common.toml） 型別定義 -----
class BaseConfig(BaseModel):
    # 允許用欄位別名填充，並禁止未知鍵
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    env: Literal["dev", "prod"]
    enable_api: bool
    enable_web: bool | None = None
    enable_android: bool | None = None
    enable_ios: bool | None = None


class DebugTestCaseConfig(BaseModel):
    test_case_name: str
    enable_reruns: bool


class TestLaneConfig(BaseModel):
    name: str | None = None
    user: str
    jobs: list[list[str]]


class LaneGroups(BaseModel):
    dev: list[TestLaneConfig] | None = None
    prod: list[TestLaneConfig] | None = None


class TestLanesConfig(BaseModel):
    api: LaneGroups | None = None
    web: LaneGroups | None = None
    android: LaneGroups | None = None
    ios: LaneGroups | None = None


class Config(BaseModel):
    base: BaseConfig
    debug_test_case: DebugTestCaseConfig
    test_lanes: TestLanesConfig | None = None


# ----- DEV PROD 環境設定（/Config/*.toml） 型別定義 -----
class AppPackageConfig(BaseModel):
    android: str
    ios: str


class ClientCommonConfig(BaseModel):
    base_url: AnyUrl
    x_api_key: str


class ClientConfig(BaseModel):
    name: str
    phone_number: str
    password: str
    access_token: str | None = None


class EnvConfig(BaseModel):
    # 允許以欄位別名（TOML 的區塊名稱/鍵名）填充
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    app_package: AppPackageConfig
    client_common: ClientCommonConfig
    clients: list[ClientConfig]


# ----- 通用載入 & 快取（Common / Env） -----
# 通用快取（依 model 類名 + 絕對路徑作為 Key）
_CONFIG_CACHE_MAP: dict[str, BaseModel] = {}


T = TypeVar("T", bound=BaseModel)


def load_config(model: Type[T], path: Path | str) -> T:
    """讀取 TOML 設定檔並依指定 pydantic model 做型別驗證。"""
    p = Path(path)
    with p.open("rb") as f:
        data = tomllib.load(f)
    try:
        return model.model_validate(data)
    except ValidationError as e:
        raise RuntimeError(f"TOML 設定格式錯誤於 {p}：\n{e}") from e


def get_config(
    model: Type[T],
    path: Path | str | None = None,
    *,
    env: Literal["dev", "prod"] | None = None,
) -> T:
    """
    通用取得設定（含快取）。
    - 若提供 `path`，直接以該路徑載入。
    - 若未提供 `path`：
        * 當 model 是 `Config`（common 設定），預設路徑為 <repo_root>/config/common.toml
        * 當 model 是 `EnvConfig`（環境設定），須提供 `env`，路徑為 <repo_root>/config/{env}.toml
    """
    if path is None:
        base_dir = Path(__file__).resolve().parent.parent / "config"
        if model.__name__ == "Config":
            path = base_dir / "common.toml"
        elif model.__name__ == "EnvConfig":
            if env is None:
                raise RuntimeError("請提供 env（dev 或 prod）或明確給定 path。")
            path = base_dir / f"{env}.toml"
        else:
            # 預設回退：與 common 相同目錄
            path = base_dir / "common.toml"

    key = f"{model.__name__}::{Path(path).resolve()}"
    cached = _CONFIG_CACHE_MAP.get(key)
    if cached is not None:
        return cast(T, cached)

    cfg = load_config(model, path)
    _CONFIG_CACHE_MAP[key] = cfg
    return cfg

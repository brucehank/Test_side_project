# utils 維護指南

`utils/` 的角色是「共用基礎能力」，避免在 `action/` 與 `test/` 重複實作。

- `action/api/*`：封裝各服務 API 行為。
- `test/api/*`：測試流程與斷言。
- `utils/*`：跨模組共用的底層工具。

## 1. 目前實際結構

目前 `utils` 只有兩個核心模組：

- `utils/config_toml.py`
  - 讀取 `config/*.toml`
  - 以 Pydantic 做型別驗證
  - 提供快取式 `get_config(...)`
- `utils/httpclient.py`
  - `ApiRequest` / `HttpResponse` 資料結構
  - `HttpClient` 統一發送 HTTP 請求

> 本文件以目前實際檔案為準；若新增模組，請同步更新本文件。

## 2. 設計原則

1. 單一職責：一個模組只做一類基礎能力。
2. 介面穩定：優先維持既有函式簽名，避免連鎖改動。
3. 無業務邏輯：`utils` 不處理 domain 規則與測試判斷。
4. 可回溯：錯誤資訊要可定位（status code、response、exception）。

## 3. 使用方式

### 3.1 載入設定

```python
from utils.config_toml import Config, EnvConfig, get_config

common_cfg = get_config(Config)
env_cfg = get_config(EnvConfig, env="dev")
```

### 3.2 發送 HTTP 請求

```python
from utils.httpclient import ApiRequest, HttpClient

client = HttpClient()
resp = client.request(
    ApiRequest(
        url="https://example.com/ping",
        method="get",
        headers={"x-api-key": "demo"},
    )
)
```

## 4. 何時應該放進 utils

- 同一能力在兩個以上地方重複出現。
- 與特定 API domain 無關（可跨模組重用）。
- 主要價值是「降低重複」與「統一介面」。

## 5. 反模式（避免）

- 在 `utils` 內引入測試案例資料或斷言。
- 在 `utils` 內直接寫特定 endpoint 的商業流程。
- 為了單次需求在 `utils` 新增一次性 helper。

## 6. 變更後驗證

```bash
python3 -m py_compile utils/config_toml.py utils/httpclient.py
python3 -m py_compile action/api/*.py test/api/*.py
```

若改到 request/response 結構，建議再跑一組最小 API 測試確認相容性。

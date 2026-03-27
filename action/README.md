# action 維護指南

`action/` 的角色是 API client 層，負責把 endpoint 呼叫封裝成可重用方法。

- `test/api/*`：負責測試流程與斷言。
- `action/api/*`：負責呼叫服務 API。
- `utils/httpclient.py`：提供共用傳輸能力。

## 1. 目前實際結構

目前 `action/api` 有兩個 client：

- `action/api/hal.py`
  - class: `Hal(HttpClient)`
  - 目前方法：`get_workout_begin_actions_api(...)`
- `action/api/dummyjson_users.py`
  - class: `DummyJsonUsers(HttpClient)`
  - 目前方法：
    - `get_all_users_api(...)`
    - `login_user_api(...)`
    - `get_current_authenticated_user_api(...)`

> 本文件以目前實際檔案為準；新增 client 時請同步更新本文件。

## 2. 設計原則

1. 單一職責：`action` 只做 API 呼叫封裝，不做測試斷言。
2. 不讀設定：不要在 `action` 內呼叫 `get_config(...)`。
3. 介面穩定：輸入參數與回傳型別要清楚且一致。
4. 低耦合：不要在 `action` 內塞入環境分支與測資邏輯。

## 3. 標準實作模式

新增 client 請沿用以下模式：

1. class 繼承 `HttpClient`
2. `__init__` 只接收必要建構參數（例如 `base_url`, `auth_token`, `x_api_key`）
3. 提供 `_headers(extra)` 處理共用 header
4. 每個 API 方法都用 `ApiRequest(...)` 建 request
5. 回傳 `HttpResponse`，由測試層做斷言

範例（簡化）：

```python
class Xxx(HttpClient):
    def __init__(self, auth_token: str, base_url: str, x_api_key: str):
        super().__init__()
        self.auth_token = auth_token
        self.base_url = f"{base_url}/svc-xxx"
        self.x_api_key = x_api_key

    def _headers(self, extra: dict | None = None) -> dict:
        headers = {
            "x-api-key": self.x_api_key,
            "Authorization": f"Bearer {self.auth_token}",
        }
        if extra:
            headers.update({k: v for k, v in extra.items() if v is not None})
        return headers
```

## 4. 命名規範

- API 方法命名：`<http_method>_<resource>_api`
- 參數命名：`snake_case`
- 可選參數預設為 `None`，送出前過濾 `None` 值

## 5. 反模式（避免）

- 在 `action` 裡讀 TOML 設定或環境變數拼業務邏輯。
- 在 `action` 裡做測試斷言。
- 同一份 headers 在多個方法重複貼上不抽 `_headers(...)`。
- 把 test case data 放進 client。

## 6. 變更後驗證

```bash
python3 -m py_compile action/api/*.py
python3 -m py_compile test/api/*.py
```

若新增或調整 endpoint，建議再跑對應測試檔做最小回歸。

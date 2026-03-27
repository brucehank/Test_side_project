# Test Architecture Guide

本文件說明 `test/` 目錄的測試架構，目標是讓開發者與 AI 都能快速理解「資料放哪裡、邏輯寫哪裡、該怎麼擴充」。

> 目前狀態：`test/app` 與 `test/web` 已暫停開發，現階段主要開發與維護重心在 `test/api`。
>
> 範圍說明：本文件聚焦 `test/` 分層與測試寫法；整體執行流程（`run.py`、`test_lanes`）請看專案根目錄 `README.md`。

## 1. 目錄定位

- `test/api/`
  API E2E 測試主體。包含：
  - 測試案例：`test_*.py`
  - fixture：`conftest.py`
  - helper/assertion：`helpers.py`
  - 共用型別：`types.py`
- `test/app/`
  App UI 測試（目前停止開發，僅保留既有內容）。
- `test/web/`
  Web 測試（目前停止開發，僅保留既有內容）。

## 2. API 測試分層（建議長期維持）

- Action 層：`action/api/*.py`
  - 純 API client，不放測試斷言。
- TestData 層：`testdata/api/*.py`
  - 只放測試資料、dataclass、case 常數、按環境分組資料。
  - 測試資料優先使用 dataclass，不用 dict。
- Helper 層：`test/api/helpers.py`
  - 放 reusable assertion 與共用驗證工具。
  - 目前以 `DummyJsonUsersHelper`（`assert_get_all_users` / `assert_login_user` /
    `assert_get_current_authenticated_user`）等 API 回應驗證為主。
- Fixture 層：`test/api/conftest.py`
  - 放環境解析、config 載入、client 選擇與 `user_token` fixture。
- Spec 層：`test/api/test_*.py`
  - 測試流程編排與 `pytest.mark.parametrize`。
  - 不直接堆大量 raw test data。

## 3. 目前 API 區關鍵檔案

- `test/api/conftest.py`
  - `env_name`：從 `-m` 解析 `dev/prod`。
  - `get_env_config`：讀取對應 TOML。
  - `user_config`：依 `--user` 選 client（預設第一個）。
  - `user_token`：優先讀 `clients[].access_token`，否則使用 `TEST_ACCESS_TOKEN`。
- `test/api/helpers.py`
  - 目前主要為 `DummyJsonUsersHelper` 與共用 API 回應檢核函式。
- `test/api/types.py`
  - `TestUserTokens` 統一型別定義，避免各檔重複宣告。

## 4. 匯入規範

- `test/api` 不使用 wildcard import（`import *`）。
- 以顯式 import 為準：
  - helper 從 `test/api/helpers.py` 引入。
  - case dataclass/常數 從 `testdata/api/*.py` 引入。
  - 共用型別從 `test/api/types.py` 引入。

## 5. 命名規範

- dataclass：
  - case：`SomethingCaseData`
  - expected：`SomethingExpectedData`
- case 常數：
  - `SOMETHING_POSITIVE_CASES`
  - `SOMETHING_NEGATIVE_CASES`
  - `SOMETHING_SECURITY_CASES`
- 單一測試函式內固定 expected 可直接在測試內宣告，不必額外抽成全域常數。

## 6. 新增 API 測試的標準流程

1. 在 `testdata/api/<domain>.py` 建立或擴充 dataclass 與 case 常數。
2. 如果已有相同資料結構，優先共用既有 dataclass。
3. 在 `test/api/helpers.py` 新增可重用 assertion（必要時）。
4. 在 `test/api/test_<domain>.py` 使用 `@pytest.mark.parametrize` 串接 case。
5. 測試檔只保留流程與驗證，不放大量 raw dict data。

## 7. 執行方式（常用）

- 跑整體（依 `config/common.toml` 的 `test_lanes`）：
  - `python run.py`
- 跑單一 API 檔案（例：dev）：
  - `pytest -m dev test/api/test_video.py -v`
- 跑單一案例關鍵字：
  - `pytest -m dev test/api/test_video.py -k T88 -v`

## 8. 現況與技術債

- API 區已移除舊的匯入聚合層，全面採顯式 import。
- `test/app`、`test/web` 目前暫停開發，仍保留 legacy `common` 與 wildcard import；若未來重啟，建議比照 `test/api` 重構。

## 9. 給 AI 的實作準則

- 變更測試資料時，優先改 `testdata/api`，避免直接塞回 `test/api/test_*.py`。
- 遇到 dict expected 舊寫法，優先改 dataclass；若需相容，先保留 helper fallback 再分批清理。
- 新增 helper 時以可重用為優先，不新增 domain-specific 重複 helper class。
- 先做小範圍可驗證改動，至少跑 `py_compile` 或最小 pytest 範圍驗證。

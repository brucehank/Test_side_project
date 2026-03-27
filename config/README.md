# Config 架構說明

本文件說明 `config/` 的結構、使用方式與維護規範，提供開發者與 AI 一致的設定管理準則。

## 1. 目錄與用途

- `config/common.toml`
  - 測試執行層共用設定（例如 `base`、`debug_test_case`、`test_lanes`）。
- `config/dev.toml`
- `config/prod.toml`
  - 各環境專屬設定（`client_common`、`clients` 等）。

## 2. 目前實際使用的核心欄位

`common.toml` 目前主流程重點使用：

- `[base]`
  - `env`
  - `enable_api`
- `[debug_test_case]`
  - `enable_reruns`
  - `test_case_name`
- `[test_lanes.api]`
  - 各環境對應的 API lane 清單（`user` 與 `jobs` 明確綁定）
  - `jobs` 內每個 module 會被 runner 拆成獨立 pytest 命令。

其他欄位可保留做未來擴充，但現階段非主要路徑。

## 3. 安全與版控原則（必須遵守）

1. Git 內只保留「空值/範本」配置，真實機密不進版控。  
2. 禁止提交真實密碼到 repo；請以本機私有檔或環境變數注入。

## 4. 執行時設定來源

- 本機開發：
  - 使用本地 `config/*.toml`（通常為空值模板或測試用途配置）。
- 其他執行環境：
  - 建議在執行時注入真實 `config` 檔案或等價機密來源。
  - repo 內模板檔僅作為結構參考，不作為真實機密來源。

## 5. 維護建議

1. 修改欄位前先同步 `utils/config_toml.py` 的 Pydantic model。
2. 新增環境檔時，命名與 `base.env` 值保持一致（`dev/prod`）。
3. 調整 `test_lanes` 內 `jobs` 路徑後，確認檔案存在且平台對應正確。
4. 若某欄位已不使用，優先調整為 optional，而非直接刪除欄位。

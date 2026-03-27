# 專案維護指南

本專案目前是 API 測試主線，入口為 `python run.py`。

## 1. 目前實際結構

| 目錄 | 主要用途 |
| --- | --- |
| `run.py` | 測試主入口，負責 lane 調度與整體 exit code。 |
| `action/api/` | API client 層（目前有 `hal.py`）。 |
| `test/api/` | 測試案例、fixture、helper、共用型別。 |
| `testdata/api/` | 測資定義（目前為 `video.py`）。 |
| `config/` | `common.toml` 與各環境設定（`dev.toml`, `prod.toml`）。 |
| `utils/` | 共用工具（`config_toml.py`, `httpclient.py`）。 |

## 2. 執行流程（run.py）

1. 載入 `config/common.toml`
2. 清理 `allure-results/`
3. 依 `test_lanes` 啟動 pytest subprocess
4. lane 與 lane 並行、lane 內 module 序列執行
5. 同帳號 `user` 採互斥鎖避免並發
6. 收斂所有 job 結果並回傳整體 exit code

## 3. 設定重點

`config/common.toml` 的核心區塊：

- `[base]`：`env`、平台開關（`enable_api` 等）
- `[debug_test_case]`：`enable_reruns`、`test_case_name`
- `[test_lanes.<platform>]`：`dev/prod` 的 lane 清單（`user + jobs`）

更多細節請看 [config/README.md](/Users/brucechen/Documents/GitHub/Test_side_project/config/README.md)。

## 4. 本機快速開始

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
python run.py
```

## 5. 開發維護原則

- 測試流程寫在 `test/api/*`，測資寫在 `testdata/api/*`。
- `action/api/*` 只封裝 API 呼叫，不放測試斷言。
- `utils/*` 只放可重用基礎能力，不放業務流程。
- 優先做小範圍修改，並跑最小驗證命令。

## 6. 常用驗證

```bash
python3 -m py_compile run.py utils/*.py action/api/*.py test/api/*.py testdata/api/*.py
pytest -m dev -k video -v
```

## 7. 延伸文件

- [action/README.md](/Users/brucechen/Documents/GitHub/Test_side_project/action/README.md)
- [utils/README.md](/Users/brucechen/Documents/GitHub/Test_side_project/utils/README.md)
- [testdata/README.md](/Users/brucechen/Documents/GitHub/Test_side_project/testdata/README.md)
- [test/README.md](/Users/brucechen/Documents/GitHub/Test_side_project/test/README.md)

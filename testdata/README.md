# testdata 維護指南

`testdata/` 的角色是「只放測試資料」，把資料與測試流程分離：

- `test/api/*`：負責流程、呼叫 API、斷言。
- `testdata/api/*`：負責測資定義（dataclass + case 常數）。

這樣做可以降低重複、讓資料修改更安全、也更容易做批次調整。

## 1. 目前實際結構

目前 `testdata/api` 只有一個資料模組：

- `testdata/api/video.py`
  - `ContentData`：Video 測資資料結構
  - `PROGRAM_CONTENT_CASE`：目前使用中的 case 清單

> 本文件以目前實際檔案為準；若新增 domain，再擴充本文件。

## 2. 資料層設計原則

1. 單一職責：`testdata` 只放資料，不放 API 呼叫與商業流程。
2. 型別優先：優先使用 `@dataclass(frozen=True)`，不要散落 raw dict。
3. 穩定命名：常數命名要清楚可讀，避免語意含糊。
4. 可追蹤：每筆 case 應該能對應到明確測試情境。

## 3. 命名建議

- 資料結構：`XXXData`（例如 `ContentData`）
- case 常數：
  - 單一主題可用 `*_CASE`
  - 多組集合可用 `*_CASES`
  - 依情境再加語意（例如 `PROGRAM_*`, `VIDEO_*`, `NEGATIVE_*`）

重點是同一檔案內保持一致，不要混用多種風格。

## 4. 新增或調整測資流程

1. 先確認是否能重用既有 dataclass；不能重用再新增。
2. 在 `testdata/api/<domain>.py` 增加或修改 case 常數。
3. 在對應 `test/api/test_<domain>.py` 更新 import 與 `parametrize`。
4. 確認 `ids=` 可讀（例如使用 `modality` 或 `desc`）。
5. 做最小驗證（語法 + 目標測試）。

## 5. 反模式（避免）

- 在 test function 裡面直接貼大型資料陣列。
- 在 `testdata` 內做 API 呼叫或環境判斷流程。
- 為了單次測試改動而破壞既有命名一致性。

## 6. 驗證建議

```bash
python3 -m py_compile testdata/api/*.py
pytest -m dev -k video -v
```

如果你修改的是特定 case，建議直接用 `-k <關鍵字>` 跑最小範圍回歸。

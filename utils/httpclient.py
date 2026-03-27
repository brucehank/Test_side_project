import logging
from dataclasses import dataclass

import requests

log = logging.getLogger(__name__)


@dataclass
class ApiRequest:
    url: str
    method: str
    paramsType: str | None = None
    headers: dict | None = None
    params: dict | None = None
    body: dict | None = None
    files: dict | None = None


@dataclass
class HttpResponse:
    status_code: int | None
    ok: bool
    response: any
    elapsed: float | None


class HttpClient:
    """
    Simple HTTP Client with requests.Session().
    支援 GET/POST/PUT/PATCH/DELETE + raw/form-data/GraphQL。
    """

    def __init__(self):
        self.session = requests.Session()

    def request(self, api: ApiRequest, **kwargs) -> HttpResponse:
        """
        傳送 HTTP 請求並回傳所有資訊，404/500都會拿到 response 物件。

        Args:
            僅支援傳入 ApiRequest。

        Returns:
            HttpResponse: 包含狀態碼、ok、response物件、花費時間(秒)。
        """
        data = None
        json_data = None

        if api.paramsType in {"raw", "GraphQL"}:
            json_data = api.body
        elif api.paramsType in {"form-data", "binary", "x-www-form-urlencoded"}:
            data = api.body
        elif api.paramsType is None:
            data = api.body

        # 檢查 method
        api.method = api.method.lower()
        if api.method not in {"get", "post", "put", "delete", "patch"}:
            raise ValueError(f"Unsupported HTTP method: {api.method}")

        try:
            response = self.session.request(
                method=api.method,          # 從 ApiRequest 取出 HTTP 方法
                url=api.url,                # 從 ApiRequest 取出 URL
                params=api.params,          # 查詢參數
                data=data,                  # 表單 body
                json=json_data,             # JSON body
                headers=api.headers,        # headers
                files=api.files,            # 上傳檔案
                **kwargs                    # 保留額外可選參數
            )
            return HttpResponse(
                status_code=response.status_code,
                ok=response.ok,
                response=response,
                elapsed=response.elapsed.total_seconds()
            )
        except Exception as e:
            log.error(f"Request failed: {e}")
            return HttpResponse(
                status_code=None,
                ok=False,
                response=str(e),
                elapsed=None
            )

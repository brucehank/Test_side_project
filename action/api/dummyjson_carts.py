import logging

from utils.httpclient import ApiRequest, HttpClient, HttpResponse

log = logging.getLogger(__name__)


class DummyJsonCarts(HttpClient):
    def __init__(
        self,
        base_url: str | None = None,
        access_token: str | None = None,
    ) -> None:
        super().__init__()
        self.base_url = (base_url or "").rstrip("/")
        self.access_token = access_token

    def _headers(self, access_token: str | None = None, extra: dict | None = None) -> dict:
        headers = {"Accept": "application/json"}
        resolved_access_token = access_token or self.access_token
        if resolved_access_token:
            headers["Authorization"] = f"Bearer {resolved_access_token}"
        if extra:
            headers.update({k: v for k, v in extra.items() if v is not None})
        return headers

    @staticmethod
    def _normalize_json_response(resp: HttpResponse) -> HttpResponse:
        raw_response = resp.response
        if hasattr(raw_response, "json"):
            try:
                resp.response = raw_response.json()
            except ValueError:
                log.warning("Response is not valid JSON")
        return resp

    def get_user_carts_api(
        self,
        user_id: int,
        **kwargs,
    ) -> HttpResponse:
        req = ApiRequest(
            url=f"{self.base_url}/carts/user/{user_id}",
            method="get",
            headers=self._headers(),
        )
        resp = self.request(req, **kwargs)
        log.debug("Call GET user carts api, user_id=%s", user_id)
        return self._normalize_json_response(resp)

    def get_single_cart_api(
        self,
        cart_id: int,
        **kwargs,
    ) -> HttpResponse:
        req = ApiRequest(
            url=f"{self.base_url}/carts/{cart_id}",
            method="get",
            headers=self._headers(),
        )
        resp = self.request(req, **kwargs)
        log.debug("Call GET single cart api, cart_id=%s", cart_id)
        return self._normalize_json_response(resp)

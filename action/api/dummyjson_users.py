import logging

from utils.httpclient import ApiRequest, HttpClient, HttpResponse

log = logging.getLogger(__name__)


class DummyJsonUsers(HttpClient):
    def __init__(self, base_url: str = "https://dummyjson.com") -> None:
        super().__init__()
        self.base_url = base_url.rstrip("/")

    def _headers(self, access_token: str | None = None, extra: dict | None = None) -> dict:
        headers = {"Accept": "application/json"}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
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

    def get_all_users_api(
        self,
        limit: int | None = None,
        skip: int | None = None,
        select: str | None = None,
        **kwargs,
    ) -> HttpResponse:
        params = {
            "limit": limit,
            "skip": skip,
            "select": select,
        }
        req = ApiRequest(
            url=f"{self.base_url}/users",
            method="get",
            params={k: v for k, v in params.items() if v is not None},
            headers=self._headers(),
        )
        resp = self.request(req, **kwargs)
        log.debug("Call GET all users api")
        return self._normalize_json_response(resp)

    def login_user_api(
        self,
        username: str,
        password: str,
        expires_in_mins: int | None = None,
        **kwargs,
    ) -> HttpResponse:
        body = {
            "username": username,
            "password": password,
            "expiresInMins": expires_in_mins,
        }
        req = ApiRequest(
            url=f"{self.base_url}/user/login",
            method="post",
            paramsType="raw",
            body={k: v for k, v in body.items() if v is not None},
            headers=self._headers(extra={"Content-Type": "application/json"}),
        )
        resp = self.request(req, **kwargs)
        log.debug("Call POST login user api")
        return self._normalize_json_response(resp)

    def get_current_authenticated_user_api(
        self,
        access_token: str | None = None,
        **kwargs,
    ) -> HttpResponse:
        req = ApiRequest(
            url=f"{self.base_url}/user/me",
            method="get",
            headers=self._headers(access_token=access_token),
        )
        resp = self.request(req, **kwargs)
        log.debug("Call GET current authenticated user api")
        return self._normalize_json_response(resp)

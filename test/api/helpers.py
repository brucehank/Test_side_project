import logging

import allure

from action.api.dummyjson_users import DummyJsonUsers

log = logging.getLogger(__name__)


class DummyJsonUsersHelper:
    def assert_get_all_users(
        self,
        dummy_json_users: DummyJsonUsers,
    ) -> dict:
        expected_status = 200
        response_time_limit = 5.0

        with allure.step("Call get_all_users_api"):
            resp = dummy_json_users.get_all_users_api()
            if not resp.ok:
                log.error(
                    "get_all_users_api failed, status_code=%s, response=%s",
                    resp.status_code,
                    resp.response,
                )

            with allure.step("Check response object exists"):
                assert resp is not None, "response should not be None"

            with allure.step(f"Check status code is {expected_status}"):
                assert resp.status_code == expected_status, (
                    f"應回傳 {expected_status}，實際為 {resp.status_code}"
                )

            with allure.step("Check response ok is True"):
                assert resp.ok, f"API call failed, status_code={resp.status_code}"

            with allure.step(f"Check response time less than {response_time_limit} seconds"):
                assert resp.elapsed is not None, "response.elapsed should not be None"
                assert resp.elapsed < response_time_limit, (
                    f"API 響應時間過長，實際為 {resp.elapsed} 秒"
                )

        payload = resp.response
        with allure.step("Check payload is dict"):
            assert isinstance(
                payload, dict), f"response payload should be dict, got {type(payload)}"

        with allure.step("Check users summary fields"):
            total = payload.get("total")
            skip = payload.get("skip")
            limit = payload.get("limit")
            assert isinstance(total, int) and total >= 0, "total should be non-negative int"
            assert isinstance(skip, int) and skip >= 0, "skip should be non-negative int"
            assert isinstance(limit, int) and limit > 0, "limit should be positive int"

        with allure.step("Check users list exists"):
            users = payload.get("users")
            assert isinstance(users, list), "users should be list"
            assert len(users) > 0, "users should not be empty"
            assert total >= len(users), "total should be >= users length"

        with allure.step("Check key fields in users data"):
            for index, user in enumerate(users):
                assert isinstance(user, dict), f"users[{index}] should be dict"
                assert isinstance(user.get("id"), int) and user.get("id") > 0, (
                    f"users[{index}].id should be positive int"
                )
                assert isinstance(user.get("username"), str) and user.get("username"), (
                    f"users[{index}].username should be non-empty string"
                )
                assert isinstance(user.get("email"), str) and "@" in user.get("email", ""), (
                    f"users[{index}].email should be valid email string"
                )
                assert isinstance(user.get("firstName"), str) and user.get("firstName"), (
                    f"users[{index}].firstName should be non-empty string"
                )
                assert isinstance(user.get("lastName"), str) and user.get("lastName"), (
                    f"users[{index}].lastName should be non-empty string"
                )

        return payload

    def assert_login_user(
        self,
        dummy_json_users: DummyJsonUsers,
        username: str,
        password: str,
    ) -> dict:
        expected_status = 200
        response_time_limit = 5.0

        with allure.step("Call login_user_api"):
            resp = dummy_json_users.login_user_api(
                username=username,
                password=password,
            )
            if not resp.ok:
                log.error(
                    "login_user_api failed, status_code=%s, response=%s",
                    resp.status_code,
                    resp.response,
                )

            with allure.step("Check response object exists"):
                assert resp is not None, "response should not be None"

            with allure.step(f"Check status code is {expected_status}"):
                assert resp.status_code == expected_status, (
                    f"應回傳 {expected_status}，實際為 {resp.status_code}"
                )

            with allure.step("Check response ok is True"):
                assert resp.ok, f"API call failed, status_code={resp.status_code}"

            with allure.step(f"Check response time less than {response_time_limit} seconds"):
                assert resp.elapsed is not None, "response.elapsed should not be None"
                assert resp.elapsed < response_time_limit, (
                    f"API 響應時間過長，實際為 {resp.elapsed} 秒"
                )

        payload = resp.response
        with allure.step("Check payload is dict"):
            assert isinstance(
                payload, dict), f"response payload should be dict, got {type(payload)}"

        with allure.step("Check login payload key fields"):
            assert isinstance(payload.get("id"), int) and payload.get("id") > 0, (
                "id should be positive int"
            )
            assert isinstance(payload.get("username"), str) and payload.get("username"), (
                "username should be non-empty string"
            )
            assert isinstance(payload.get("email"), str) and "@" in payload.get("email", ""), (
                "email should be valid email string"
            )

        with allure.step("Check token fields"):
            access_token = payload.get("accessToken") or payload.get("token")
            assert isinstance(access_token, str) and access_token, (
                "access token should be non-empty string"
            )
            dummy_json_users.access_token = access_token
            refresh_token = payload.get("refreshToken")
            if refresh_token is not None:
                assert isinstance(refresh_token, str) and refresh_token, (
                    "refreshToken should be non-empty string"
                )

        return payload

    def assert_get_current_authenticated_user(
        self,
        dummy_json_users: DummyJsonUsers,
    ) -> dict:
        expected_status = 200
        response_time_limit = 5.0

        with allure.step("Check DummyJsonUsers has access token"):
            assert isinstance(dummy_json_users.access_token, str) and dummy_json_users.access_token, (
                "dummy_json_users.access_token should be non-empty"
            )

        with allure.step("Call get_current_authenticated_user_api"):
            resp = dummy_json_users.get_current_authenticated_user_api()
            if not resp.ok:
                log.error(
                    "get_current_authenticated_user_api failed, status_code=%s, response=%s",
                    resp.status_code,
                    resp.response,
                )

            with allure.step("Check response object exists"):
                assert resp is not None, "response should not be None"

            with allure.step(f"Check status code is {expected_status}"):
                assert resp.status_code == expected_status, (
                    f"應回傳 {expected_status}，實際為 {resp.status_code}"
                )

            with allure.step("Check response ok is True"):
                assert resp.ok, f"API call failed, status_code={resp.status_code}"

            with allure.step(f"Check response time less than {response_time_limit} seconds"):
                assert resp.elapsed is not None, "response.elapsed should not be None"
                assert resp.elapsed < response_time_limit, (
                    f"API 響應時間過長，實際為 {resp.elapsed} 秒"
                )

        payload = resp.response
        with allure.step("Check payload is dict"):
            assert isinstance(
                payload, dict), f"response payload should be dict, got {type(payload)}"

        with allure.step("Check current user profile fields"):
            assert isinstance(payload.get("id"), int) and payload.get("id") > 0, (
                "id should be positive int"
            )
            assert isinstance(payload.get("username"), str) and payload.get("username"), (
                "username should be non-empty string"
            )
            assert isinstance(payload.get("email"), str) and "@" in payload.get("email", ""), (
                "email should be valid email string"
            )
            assert isinstance(payload.get("firstName"), str) and payload.get("firstName"), (
                "firstName should be non-empty string"
            )
            assert isinstance(payload.get("lastName"), str) and payload.get("lastName"), (
                "lastName should be non-empty string"
            )

        return payload

"""DummyJSON users API tests."""

import allure
import pytest

from action.api.dummyjson_users import DummyJsonUsers
from test.api.helpers import DummyJsonUsersHelper
from utils.config_toml import ClientCommonConfig


@pytest.mark.dev
@pytest.mark.prod
class TestDummyJsonUsers(DummyJsonUsersHelper):
    """Entry class for DummyJSON users API tests."""

    @allure.title("[DummyJSON] login -> me -> single user consistency flow")
    def test_login_me_single_user_consistency_flow(
        self,
        client_common_config: ClientCommonConfig,
    ) -> None:
        with allure.step("Build DummyJsonUsers client"):
            dummy_json_users = DummyJsonUsers(
                base_url=str(client_common_config.base_url),
            )

        with allure.step("Get all users"):
            all_users_payload = self.assert_get_all_users(dummy_json_users)

        with allure.step("Pick one random loginable user from users list"):
            users = all_users_payload.get("users")
            assert isinstance(users, list) and users, "users should be non-empty list"
            random_user = self.pick_random_loginable_user(users)
            username = random_user["username"]
            password = random_user["password"]

        with allure.step("Login with selected user"):
            login_payload = self.assert_login_user(
                dummy_json_users=dummy_json_users,
                username=username,
                password=password,
            )

        with allure.step("Call current authenticated user API (/user/me)"):
            me_payload = self.assert_get_current_authenticated_user(dummy_json_users)

        with allure.step("Call single user API (/users/{id}) by login id"):
            login_user_id = login_payload.get("id")
            assert isinstance(login_user_id, int) and login_user_id > 0, (
                "login id should be positive int"
            )
            single_user_payload = self.assert_get_single_user(
                dummy_json_users=dummy_json_users,
                user_id=login_user_id,
            )

        with allure.step("Check flow responses are dict"):
            assert isinstance(login_payload, dict), "login payload should be dict"
            assert isinstance(me_payload, dict), "me payload should be dict"
            assert isinstance(single_user_payload, dict), "single user payload should be dict"

        with allure.step("Check id consistency: login.id == me.id == users/{id}.id"):
            login_id = login_payload.get("id")
            me_id = me_payload.get("id")
            single_user_id = single_user_payload.get("id")
            assert login_id == me_id == single_user_id, (
                "id mismatch: "
                f"login.id={login_id}, me.id={me_id}, users/{{id}}.id={single_user_id}"
            )

        with allure.step("Check username/email/firstName consistency"):
            assert login_payload.get("username") == me_payload.get("username") == single_user_payload.get(
                "username"
            ), "username mismatch among login/me/users/{id}"
            assert login_payload.get("email") == me_payload.get("email") == single_user_payload.get(
                "email"
            ), "email mismatch among login/me/users/{id}"
            assert login_payload.get("firstName") == me_payload.get(
                "firstName"
            ) == single_user_payload.get("firstName"), (
                "firstName mismatch among login/me/users/{id}"
            )

        with allure.step("Check me and users/{id} core fields consistency"):
            core_fields = ["id", "username", "email", "firstName", "lastName"]
            for field in core_fields:
                assert me_payload.get(field) == single_user_payload.get(field), (
                    f"Field mismatch for '{field}': "
                    f"me={me_payload.get(field)!r}, users/{{id}}={single_user_payload.get(field)!r}"
                )

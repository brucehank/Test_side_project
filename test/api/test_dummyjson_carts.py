"""DummyJSON carts API tests."""

import allure
import pytest

from action.api.dummyjson_carts import DummyJsonCarts
from action.api.dummyjson_users import DummyJsonUsers
from test.api.helpers import DummyJsonCartsHelper, DummyJsonUsersHelper
from utils.config_toml import ClientCommonConfig


@pytest.mark.dev
@pytest.mark.prod
@allure.feature("DummyJSON Carts")
@allure.story("User Cart Relationships")
class TestDummyJsonCarts(DummyJsonCartsHelper, DummyJsonUsersHelper):
    """Entry class for DummyJSON carts API tests."""

    @allure.title("[DummyJSON Carts] user carts flow by random loginable user")
    def test_get_user_carts_and_single_cart_flow(
        self,
        client_common_config: ClientCommonConfig,
    ) -> None:
        with allure.step("Build DummyJSON users/carts clients"):
            base_url = str(client_common_config.base_url)
            dummy_json_users = DummyJsonUsers(base_url=base_url)
            dummy_json_carts = DummyJsonCarts(base_url=base_url)

        with allure.step("Call get_all_users_api"):
            users_payload = self.assert_get_all_users(dummy_json_users)

        with allure.step("Pick random loginable user and get user id"):
            users = users_payload.get("users")
            assert isinstance(users, list) and users, "users should be non-empty list"
            untried_users = list(users)
            user_id: int | None = None
            user_carts_payload: dict | None = None

            while untried_users:
                random_user = self.pick_random_loginable_user(untried_users)
                user_id_candidate = random_user.get("id")
                assert isinstance(user_id_candidate, int) and user_id_candidate > 0, (
                    "selected user_id should be positive int"
                )

                with allure.step(f"Call GET /users/{user_id_candidate}"):
                    _ = self.assert_get_single_user(
                        dummy_json_users=dummy_json_users,
                        user_id=user_id_candidate,
                    )

                with allure.step(f"Call GET /carts/user/{user_id_candidate}"):
                    candidate_payload = self.assert_get_user_carts(
                        dummy_json_carts=dummy_json_carts,
                        user_id=user_id_candidate,
                    )

                carts = candidate_payload.get("carts")
                if isinstance(carts, list) and carts:
                    user_id = user_id_candidate
                    user_carts_payload = candidate_payload
                    break

                untried_users = [
                    user for user in untried_users
                    if isinstance(user, dict) and user.get("id") != user_id_candidate
                ]

            assert user_id is not None, "No random loginable user with non-empty carts found"
            assert isinstance(user_carts_payload, dict), "user carts payload should be dict"

        with allure.step("Pick first cart id from carts list"):
            assert user_id is not None, "user_id should be available before reading carts"
            assert user_carts_payload is not None, "user_carts_payload should be available"
            carts = user_carts_payload.get("carts")
            assert isinstance(carts, list) and carts, "carts should be non-empty list"
            first_cart = carts[0]
            assert isinstance(first_cart, dict), "first cart should be dict"
            cart_id = first_cart.get("id")
            assert isinstance(cart_id, int) and cart_id > 0, "cart_id should be positive int"

        with allure.step("Call GET /carts/{cartId}"):
            cart_detail_payload = self.assert_get_single_cart(
                dummy_json_carts=dummy_json_carts,
                cart_id=cart_id,
            )

        with allure.step("Check flow payload types"):
            assert isinstance(user_carts_payload, dict), "user carts payload should be dict"
            assert isinstance(cart_detail_payload, dict), "single cart payload should be dict"

        with allure.step("Check carts/total/skip/limit structure"):
            carts = user_carts_payload.get("carts")
            total = user_carts_payload.get("total")
            skip = user_carts_payload.get("skip")
            limit = user_carts_payload.get("limit")
            assert isinstance(carts, list) and carts, "carts should be non-empty list"
            assert isinstance(total, int) and total >= 0, "total should be non-negative int"
            assert isinstance(skip, int) and skip >= 0, "skip should be non-negative int"
            assert isinstance(limit, int) and limit >= len(carts), (
                "limit should be >= len(carts)"
            )
            assert total >= len(carts), "total should be >= len(carts)"

        with allure.step("Check all carts belong to selected user and products is non-empty list"):
            for index, cart in enumerate(carts):
                assert isinstance(cart, dict), f"carts[{index}] should be dict"
                assert cart.get("userId") == user_id, (
                    f"carts[{index}].userId should be {user_id}, got {cart.get('userId')}"
                )
                products = cart.get("products")
                assert isinstance(products, list) and products, (
                    f"carts[{index}].products should be non-empty list"
                )
                self.assert_cart_summary_fields(cart)

        with allure.step("Check list cart and detail cart consistency"):
            self.assert_cart_list_detail_consistency(
                cart_from_list=first_cart,
                cart_detail=cart_detail_payload,
            )

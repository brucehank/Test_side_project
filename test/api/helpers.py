import logging
import random

import allure

from action.api.dummyjson_carts import DummyJsonCarts
from action.api.dummyjson_users import DummyJsonUsers

log = logging.getLogger(__name__)


class DummyJsonCartsHelper:
    def assert_get_user_carts(
        self,
        dummy_json_carts: DummyJsonCarts,
        user_id: int,
    ) -> dict:
        expected_status = 200
        response_time_limit = 5.0

        with allure.step("Call get_user_carts_api"):
            resp = dummy_json_carts.get_user_carts_api(user_id=user_id)
            if not resp.ok:
                log.error(
                    "get_user_carts_api failed, user_id=%s, status_code=%s, response=%s",
                    user_id,
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
            assert isinstance(payload, dict), f"response payload should be dict, got {type(payload)}"

        with allure.step("Check carts/total/skip/limit fields"):
            carts = payload.get("carts")
            total = payload.get("total")
            skip = payload.get("skip")
            limit = payload.get("limit")
            assert isinstance(carts, list), "carts should be list"
            assert isinstance(total, int) and total >= 0, "total should be non-negative int"
            assert isinstance(skip, int) and skip >= 0, "skip should be non-negative int"
            assert isinstance(limit, int) and limit >= 0, "limit should be non-negative int"
            assert total >= len(carts), "total should be >= carts length"

        with allure.step("Check each cart belongs to user and products is list"):
            for index, cart in enumerate(carts):
                assert isinstance(cart, dict), f"carts[{index}] should be dict"
                assert cart.get("userId") == user_id, (
                    f"carts[{index}].userId should be {user_id}, got {cart.get('userId')}"
                )
                products = cart.get("products")
                assert isinstance(products, list), f"carts[{index}].products should be list"
                assert products, f"carts[{index}].products should be non-empty list"

        return payload

    def assert_get_single_cart(
        self,
        dummy_json_carts: DummyJsonCarts,
        cart_id: int,
    ) -> dict:
        expected_status = 200
        response_time_limit = 5.0

        with allure.step("Call get_single_cart_api"):
            resp = dummy_json_carts.get_single_cart_api(cart_id=cart_id)
            if not resp.ok:
                log.error(
                    "get_single_cart_api failed, cart_id=%s, status_code=%s, response=%s",
                    cart_id,
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
            assert isinstance(payload, dict), f"response payload should be dict, got {type(payload)}"

        with allure.step("Check single cart core fields"):
            assert payload.get("id") == cart_id, (
                f"cart id mismatch, expected={cart_id}, actual={payload.get('id')}"
            )
            assert isinstance(payload.get("userId"), int) and payload.get("userId") > 0, (
                "userId should be positive int"
            )
            assert isinstance(payload.get("products"), list), "products should be list"
            assert payload.get("products"), "products should be non-empty list"

        self.assert_cart_summary_fields(payload)
        return payload

    def assert_cart_summary_fields(self, cart: dict) -> None:
        with allure.step("Check cart summary fields"):
            assert isinstance(cart, dict), f"cart should be dict, got {type(cart)}"
            products = cart.get("products")
            assert isinstance(products, list), "products should be list"
            assert products, "products should be non-empty list"

            total_products = cart.get("totalProducts")
            total_quantity = cart.get("totalQuantity")
            total = cart.get("total")
            discounted_total = cart.get("discountedTotal")
            assert isinstance(total_products, int) and total_products >= 0, (
                "totalProducts should be non-negative int"
            )
            assert isinstance(total_quantity, int) and total_quantity >= 0, (
                "totalQuantity should be non-negative int"
            )
            assert isinstance(total, (int, float)) and total >= 0, (
                "total should be non-negative number"
            )
            assert isinstance(discounted_total, (int, float)) and discounted_total >= 0, (
                "discountedTotal should be non-negative number"
            )

            assert total_products == len(products), (
                f"totalProducts mismatch, expected={len(products)}, actual={total_products}"
            )

            quantities: list[int] = []
            for index, product in enumerate(products):
                assert isinstance(product, dict), f"products[{index}] should be dict"
                quantity = product.get("quantity")
                assert isinstance(quantity, int) and quantity >= 0, (
                    f"products[{index}].quantity should be non-negative int"
                )
                quantities.append(quantity)

            assert total_quantity == sum(quantities), (
                f"totalQuantity mismatch, expected={sum(quantities)}, actual={total_quantity}"
            )
            assert discounted_total <= total, (
                f"discountedTotal should be <= total, discountedTotal={discounted_total}, total={total}"
            )

    def assert_cart_list_detail_consistency(
        self,
        cart_from_list: dict,
        cart_detail: dict,
    ) -> None:
        with allure.step("Check cart list/detail summary consistency"):
            assert isinstance(cart_from_list, dict), "cart_from_list should be dict"
            assert isinstance(cart_detail, dict), "cart_detail should be dict"

            compare_fields = [
                "id",
                "userId",
                "total",
                "discountedTotal",
                "totalProducts",
                "totalQuantity",
            ]
            for field in compare_fields:
                assert cart_from_list.get(field) == cart_detail.get(field), (
                    f"{field} mismatch: list={cart_from_list.get(field)!r}, detail={cart_detail.get(field)!r}"
                )

        with allure.step("Check cart list/detail products id & quantity consistency"):
            list_products = cart_from_list.get("products")
            detail_products = cart_detail.get("products")
            assert isinstance(list_products, list), "cart_from_list.products should be list"
            assert isinstance(detail_products, list), "cart_detail.products should be list"

            def _extract_pairs(products: list[dict], source_name: str) -> list[tuple[int, int]]:
                pairs: list[tuple[int, int]] = []
                for index, product in enumerate(products):
                    assert isinstance(product, dict), f"{source_name}.products[{index}] should be dict"
                    product_id = product.get("id")
                    quantity = product.get("quantity")
                    assert isinstance(product_id, int) and product_id > 0, (
                        f"{source_name}.products[{index}].id should be positive int"
                    )
                    assert isinstance(quantity, int) and quantity >= 0, (
                        f"{source_name}.products[{index}].quantity should be non-negative int"
                    )
                    pairs.append((product_id, quantity))
                pairs.sort(key=lambda item: (item[0], item[1]))
                return pairs

            list_pairs = _extract_pairs(list_products, "cart_from_list")
            detail_pairs = _extract_pairs(detail_products, "cart_detail")
            assert list_pairs == detail_pairs, (
                f"products (id, quantity) mismatch: list={list_pairs}, detail={detail_pairs}"
            )


class DummyJsonUsersHelper:
    def assert_get_user_carts(
        self,
        dummy_json_users: DummyJsonUsers,
        user_id: int,
    ) -> dict:
        expected_status = 200
        response_time_limit = 5.0

        with allure.step("Call get_user_carts_api"):
            resp = dummy_json_users.get_user_carts_api(user_id=user_id)
            if not resp.ok:
                log.error(
                    "get_user_carts_api failed, user_id=%s, status_code=%s, response=%s",
                    user_id,
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

        with allure.step("Check carts summary fields"):
            carts = payload.get("carts")
            total = payload.get("total")
            skip = payload.get("skip")
            limit = payload.get("limit")
            assert isinstance(carts, list), "carts should be list"
            assert isinstance(total, int) and total >= 0, "total should be non-negative int"
            assert isinstance(skip, int) and skip >= 0, "skip should be non-negative int"
            assert isinstance(limit, int) and limit >= 0, "limit should be non-negative int"
            assert total >= len(carts), "total should be >= carts length"

        with allure.step("Check each cart belongs to requested user and products is list"):
            for index, cart in enumerate(carts):
                assert isinstance(cart, dict), f"carts[{index}] should be dict"
                assert cart.get("userId") == user_id, (
                    f"carts[{index}].userId should be {user_id}, got {cart.get('userId')}"
                )
                assert isinstance(cart.get("products"), list), (
                    f"carts[{index}].products should be list"
                )

        return payload

    def pick_random_loginable_user(
        self,
        users: list[dict],
    ) -> dict:
        candidates = [
            user for user in users
            if isinstance(user, dict)
            and isinstance(user.get("username"), str) and user.get("username")
            and isinstance(user.get("password"), str) and user.get("password")
        ]
        assert candidates, "No loginable user found in get_all_users response"
        return random.choice(candidates)

    def assert_get_single_user(
        self,
        dummy_json_users: DummyJsonUsers,
        user_id: int,
    ) -> dict:
        expected_status = 200
        response_time_limit = 5.0

        with allure.step("Call get_single_user_api"):
            resp = dummy_json_users.get_single_user_api(user_id=user_id)
            if not resp.ok:
                log.error(
                    "get_single_user_api failed, user_id=%s, status_code=%s, response=%s",
                    user_id,
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

        with allure.step("Check single user core fields"):
            assert isinstance(payload.get("id"), int) and payload.get("id") > 0, (
                "id should be positive int"
            )
            assert payload.get("id") == user_id, (
                f"user id mismatch, expected={user_id}, actual={payload.get('id')}"
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

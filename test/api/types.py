from dataclasses import dataclass


@dataclass(frozen=True)
class TestUserTokens:
    username: str
    access_token: str
    refresh_token: str

from __future__ import annotations

import re
import sys
from typing import Any

from pydantic import SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings

_config: _Config


# XXX: Typisierung
def init(**kwargs) -> _Config:
    global _config
    try:
        _config = _Config(**kwargs)
        return get()
    except ValidationError as err:
        print(err, file=sys.stderr)
        sys.exit(1)


def get() -> _Config:
    return _config


class _Config(BaseSettings):
    MSSQL_HOSTNAME: str
    MSSQL_PORT: int
    MSSQL_USER: str
    MSSQL_PASSWORD: SecretStr
    MSSQL_DB: str
    MSSQL_TARGET_ENCRYPT_CONNECTION: bool
    MSSQL_TRUST_SERVER_CERTIFICATE: bool

    DASHBOARD_HOSTNAME: str
    DASHBOARD_PORT: int
    DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT: bool
    DASHBOARD_TEST_CLIENTS_REGEX: re.Pattern
    DASHBOARD_APP_CLIENT_TYPE_REGEX: re.Pattern

    @field_validator(
        "MSSQL_TARGET_ENCRYPT_CONNECTION",
        "MSSQL_TRUST_SERVER_CERTIFICATE",
        "DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT",
        mode="before",
    )
    @classmethod
    def validate_booleans(cls, value: str, ctx) -> bool:
        return _Config.validate_true_false_boolean(value, ctx.field_name)

    @field_validator(
        "MSSQL_PORT",
        "DASHBOARD_PORT",
        mode="before",
    )
    @classmethod
    def validate_ports(cls, value: str, ctx) -> int:
        return _Config.validate_port(value, ctx.field_name)

    @field_validator(
        "DASHBOARD_TEST_CLIENTS_REGEX",
        "DASHBOARD_APP_CLIENT_TYPE_REGEX",
        mode="before",
    )
    @classmethod
    def validate_regexs(cls, value: str, ctx) -> re.Pattern:
        return _Config.validate_regex(value, ctx.field_name)

    @staticmethod
    def validate_port(value: str, fieldname: str | Any) -> int:
        errmsg = f"Environment variable '{fieldname}' must be an integer in the range 1-65535, received '{value}'."
        try:
            port = int(value)
        except ValueError as e:
            raise ValueError(errmsg) from e
        if not 1 <= port <= 65535:
            raise ValueError(errmsg)
        return port

    @staticmethod
    def validate_true_false_boolean(value: str | Any, fieldname: str) -> bool:
        if isinstance(value, bool):
            return value
        if value == "true":
            return True
        if value == "false":
            return False
        raise ValueError(f"Environment variable '{fieldname}' must be set to either 'true' or 'false'.")

    @staticmethod
    def validate_regex(value: str | Any, fieldname: str) -> re.Pattern:
        try:
            return re.compile(value)
        except Exception as e:
            raise ValueError(f"Environment variable '{fieldname}' must be a valid regex") from e

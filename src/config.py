from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr, field_validator

APP_SETTINGS: Config


class Config(BaseSettings):
    # XXX: Kann ich die Feldnamen klein schreiben?
    MSSQL_HOSTNAME: str
    MSSQL_PORT: str
    MSSQL_USER: str
    MSSQL_PASSWORD: SecretStr
    MSSQL_DB: str
    MSSQL_TARGET_ENCRYPT_CONNECTION: bool
    MSSQL_TRUST_SERVER_CERTIFICATE: bool

    DASHBOARD_HOSTNAME: str
    DASHBOARD_PORT: int
    DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT: bool

    @field_validator("MSSQL_TARGET_ENCRYPT_CONNECTION", mode="before")
    def validate_mssql_target_encrypt_connection(cls, value: str) -> bool:
        return Config.validate_true_false_boolean("MSSQL_TARGET_ENCRYPT_CONNECTION", value)

    @field_validator("MSSQL_TRUST_SERVER_CERTIFICATE", mode="before")
    def validate_mssql_trust_server_certificate(cls, value: str) -> bool:
        return Config.validate_true_false_boolean("MSSQL_TRUST_SERVER_CERTIFICATE", value)

    @field_validator("MSSQL_PORT", mode="before")
    def validate_tcp_port(cls, value: str) -> int:
        return Config.validate_port("MSSQL_PORT", value)

    @field_validator("DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT", mode="before")
    def validate_dashboard_hist_test_clients_default(cls, value: str) -> bool:
        return Config.validate_true_false_boolean("DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT", value)

    @field_validator("DASHBOARD_PORT", mode="before")
    def validate_tcp_port(cls, value: str) -> int:
        return Config.validate_port("DASHBOARD_PORT", value)

    @staticmethod
    def validate_port(fieldname: str, value: str) -> int:
        errmsg = f"Environment variable '{fieldname}' must be an integer in the range 1-65535."
        try:
            port = int(value)
        except ValueError as _:
            raise ValueError(errmsg) # XXX: raise ... from ????
        if not (1 <= port <= 65535):
            raise ValueError(errmsg)
        return port


    @staticmethod
    def validate_true_false_boolean(fieldname: str, value: str) -> bool:
        # XXX: muss ich hier value auch boolean zulassen, falls die Klasse explizit instanziiert wird? dito oben
        if value == "true":
            return True
        if value == "false":
            return False
        raise ValueError(
            f"Environment variable '{fieldname}' must be set to either 'true' or 'false'."
        )


import os
from warnings import filterwarnings

import pyodbc
import sqlalchemy
from flask import Flask
from sqlalchemy.dialects import mssql

from src import config
from src.dashboard import DashboardApp

# See https://stackoverflow.com/questions/71082494.
filterwarnings("ignore", category=UserWarning, message=".*pandas only supports SQLAlchemy connectable.*")


def create_app(*, init_config_from_env=True) -> Flask:
    if init_config_from_env:
        config.init()
    cfg = config.get()

    def make_conn():
        return pyodbc.connect(
            f"SERVER={cfg.MSSQL_HOSTNAME},{cfg.MSSQL_PORT};"
            f"UID={cfg.MSSQL_USER};"
            f"PWD={cfg.MSSQL_PASSWORD.get_secret_value()};"
            f"DATABASE={cfg.MSSQL_DB};"
            "Driver=ODBC Driver 18 for SQL Server;"
            f"TargetEncryptConnection={"yes" if cfg.MSSQL_TARGET_ENCRYPT_CONNECTION else "no"};"
            f"TrustServerCertificate={"yes" if cfg.MSSQL_TRUST_SERVER_CERTIFICATE else "no"};",
            readonly=True,
        )

    cnxn_pool = sqlalchemy.QueuePool(
        make_conn,
        pool_size=1,
        max_overflow=0,
        reset_on_return=True,
        pre_ping=True,
        dialect=mssql.dialect(),  # required when pre_ping is set.
    )
    return DashboardApp(cnxn_pool)._app.server


def main():
    debug = os.getenv("DEBUG") is not None
    cfg = config.init(
        MSSQL_HOSTNAME="localhost",
        MSSQL_PORT=int(os.environ.get("MSSQL_PORT", "1433")),
        MSSQL_USER="sa",
        MSSQL_PASSWORD="Bohemian_Rhapsody2024",
        MSSQL_TARGET_ENCRYPT_CONNECTION="false",
        MSSQL_TRUST_SERVER_CERTIFICATE="true",
        DASHBOARD_HOSTNAME=os.environ.get("DASHBOARD_HOSTNAME", "localhost"),
        DASHBOARD_PORT=int(os.environ.get("DASHBOARD_PORT", "5000")),
        DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT=os.environ.get("DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT", "false"),
    )

    app = create_app(init_config_from_env=False)
    app.run(
        debug=debug,
        host=cfg.DASHBOARD_HOSTNAME,
        port=cfg.DASHBOARD_PORT,
    )


if __name__ == "__main__":
    main()

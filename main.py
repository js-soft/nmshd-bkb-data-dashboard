import os
from warnings import filterwarnings

import pyodbc
import sqlalchemy
from flask import Flask
from sqlalchemy.dialects import mssql

from src.dashboard import DashboardApp

# See https://stackoverflow.com/questions/71082494.
filterwarnings("ignore", category=UserWarning, message=".*pandas only supports SQLAlchemy connectable.*")


def create_app() -> Flask:
    mssql_hostname = os.getenv("MSSQL_HOSTNAME")
    mssql_port = os.getenv("MSSQL_PORT")
    mssql_user = os.getenv("MSSQL_USER")
    mssql_password = os.getenv("MSSQL_PASSWORD")
    mssql_database = os.getenv("MSSQL_DB")
    mssql_target_encrypt_connection = os.getenv("MSSQL_TARGET_ENCRYPT_CONNECTION", "no")
    mssql_trust_server_certificate = os.getenv("MSSQL_TRUST_SERVER_CERTIFICATE", "yes")

    def make_conn():
        return pyodbc.connect(
            f"SERVER={mssql_hostname},{mssql_port};"
            f"UID={mssql_user};"
            f"PWD={mssql_password};"
            f"DATABASE={mssql_database};"
            "Driver=ODBC Driver 18 for SQL Server;"
            f"TargetEncryptConnection={mssql_target_encrypt_connection};"
            f"TrustServerCertificate={mssql_trust_server_certificate};",
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


if __name__ == "__main__":
    debug = os.getenv("DEBUG") is not None
    webserver_hostname = os.getenv("WEBSERVER_HOSTNAME", "localhost")
    webserver_port = int(os.getenv("WEBSERVER_PORT", "5000"))
    app = create_app()
    app.run(
        debug=debug,
        host=webserver_hostname,
        port=webserver_port,
    )

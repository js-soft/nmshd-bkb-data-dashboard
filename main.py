import os
from warnings import filterwarnings

import pyodbc
import sqlalchemy
from sqlalchemy.dialects import mssql

from src.dashboard import DashboardApp

# See https://stackoverflow.com/questions/71082494.
filterwarnings("ignore", category=UserWarning, message=".*pandas only supports SQLAlchemy connectable.*")


def main():
    HOST = os.getenv("MSSQL_HOST")
    USER = os.getenv("MSSQL_USER")
    PASSWORD = os.getenv("MSSQL_PASSWORD")
    DATABASE = os.getenv("MSSQL_DB")
    DEBUG = os.getenv("DEBUG") is not None

    def make_conn():
        return pyodbc.connect(
            f"SERVER={HOST};"
            f"UID={USER};"
            f"PWD={PASSWORD};"
            f"DATABASE={DATABASE};"
            "Driver=ODBC Driver 18 for SQL Server;"
            "TargetEncryptConnection=false;"
            "TrustServerCertificate=yes;"
            "MARS_Connection=yes;",
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

    app = DashboardApp(cnxn_pool)
    app.run(debug=DEBUG, host="0.0.0.0")


if __name__ == "__main__":
    main()

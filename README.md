# Development setup
Please make sure you have a proper *python* setup with version >= 3.12.
Another prerequisite is *poetry* since we use it for dependency management.
If it's not already installed on your system, have a look at https://python-poetry.org/docs/.

## Install dependencies
```bash
poetry install --with dev
```

## Database
This project expects the data of [nmshd-backbone](https://github.com/nmshd/backbone) to be available in a MSSQL database.
For easier development setups, the *docker-compose.yml* avaiable in *docker/development* provides a way to automatically load *.bacpac* files and provides a MSSQL server containing this backup.
For now, the database used within the development environment uses the default mssql port (1433) and the default mssql user (sa).
The password for this user, the database name and the path to the backup file have to be specified in the environment before starting the dev stack:
```bash
MSSQL_PASSWORD=Is1This2The3Real4Life?  # Password for the sa database user
MSSQL_DB=MyDatabase  # Name of the database to which backup is imported
DB_BACKUP_FILE=MyDatabaseBackup.bacpac  # path to database backup
```

Run the database server (and initialisation, if DB does not exist yet):
```bash
cd ./docker/development && docker-compose up
```

# Production setup

The docker setup for production like environments (using a proper WSGI server with multipe workers) can be found in `docker/production`.

Please set the following environment variables before starting the production container:

```bash
DASHBOARD_VERSION=v0.0.0  # The version of the dashboard app to use
MSSQL_HOSTNAME=localhost  # Host of the MSSQL server
MSSQL_PORT=1433  # Port of the MSSQL server
MSSQL_DB=MyDatabase  # Database name
MSSQL_USER=MyUser  # The user to use to connect to the MSSQL server
MSSQL_PASSWORD=Is1This2The3Real4Life?  # The password to use to connect to the MSSQL server
MSSQL_TARGET_ENCRYPT_CONNECTION=no  # Whether to use an encrypted connection to the MSSQL server
MSSQL_TRUST_SERVER_CERTIFICATE=yes  # Whether to blindly trust the TSL certificate
```

Start the docker compose stack:
```bash
cd docker/production && docker-compose up
```
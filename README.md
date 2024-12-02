**Enmeshed Backbone Data Dashboard**

# Usage

Releases are available as Docker images in the [project's Github container registry](https://github.com/js-soft/nmshd-bkb-data-dashboard/pkgs/container/nmshd-bkb-data-dashboard). Containers are configured using the following obligatory environment variables:

- `MSSQL_HOSTNAME`: Hostname or IP-address of the backbone MSSQL server, e.g. _localhost_ or _10.8.16.44_.
- `MSSQL_PORT`: Port of MSSQL server, e.g. _1433_.
- `MSSQL_DB`: Name of the backbone database to target within the MSSQL server, e.g. _bkb-data_.
- `MSSQL_USER`: Username, e.g. _admin_.
- `MSSQL_PASSWORD`: Password for above user, e.g. _pa$$w0rd554_.
- `MSSQL_TARGET_ENCRYPT_CONNECTION`: Specifies if SQL encryption should be used for the target database connection. Must be either _yes_ or _no_.
- `MSSQL_TRUST_SERVER_CERTIFICATE`: Specifies whether to use TLS to encrypt the target database connection and bypass walking the certificate chain to validate trust. Must be either _yes_ or _no_.

The dashboard is exposed at port 5000 by default. For example, to launch a dashboard listening at _http://localhost:80_, which connects to a MSSQL server with the above exemplary credentials the following command may be used:

```bash
docker run --rm                             \
	-p 80:5000                              \
	-e MSSQL_HOSTNAME='10.8.16.44'          \
	-e MSSQL_PORT='1433'                    \
	-e MSSQL_DB='bkb-data'                  \
	-e MSSQL_USER='admin'                   \
	-e MSSQL_PASSWORD='pa$$w0rd554'         \
	-e MSSQL_TARGET_ENCRYPT_CONNECTION='no' \
	-e MSSQL_TRUST_SERVER_CERTIFICATE='yes' \
	"ghcr.io/js-soft/nmshd-bkb-data-dashboard:latest"
```

- [ ] TODO: GUNICORN_WORKER

# Dev Setup

1. Clone the repository, ensure [Python ≥3.12](https://github.com/pyenv/pyenv) and [Poetry](https://python-poetry.org/) are installed. Install all dependencies and activate your virtual environment.

    ```bash
    poetry install --with dev
    poetry shell
    ```

2. Provide the location and credentials for the backbone database server to use during development by setting the environment variables listed in the usage instructions above.

3. (Optional) A local backbone database server can be bootstrapped from a local _.bacpac_ backup file using the following command. The path to the file has to be specified via the `MSSQL_DB_BACKUP_FILE` environment variable.

    ```bash
    docker compose                                  \
        -e MSSQL_DB_BACKUP_FILE=./my-backup.bacpac  \
        -f ./dev/bootstrap-mssql.docker-compose.yml \
        up
    ```

4. Start the dashboard server locally via `python main.py`. The hostname and port default to _localhost_ and _5000_, respectively. To override these defaults use the environment variables:
    - `DASHBOARD_HOSTNAME`: Hostname or IP-address of dashboard server
    - `DASHBOARD_PORT`: Port of dashboard server

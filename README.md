**Enmeshed Backbone Data Dashboard**

# Usage

Releases are available as Docker images in the [project's Github container registry](https://github.com/js-soft/nmshd-bkb-data-dashboard/pkgs/container/nmshd-bkb-data-dashboard). Containers are configured using the following obligatory environment variables:

- `MSSQL_HOSTNAME`: Hostname or IP-address of the backbone MSSQL server, e.g. _localhost_ or _10.8.16.44_.
- `MSSQL_PORT`: Port of MSSQL server, e.g. _1433_.
- `MSSQL_DB`: Name of the backbone database to target within the MSSQL server, e.g. _bkb-data_.
- `MSSQL_USER`: Username, e.g. _admin_.
- `MSSQL_PASSWORD`: Password for above user, e.g. _pa$$w0rd554_.
- `MSSQL_TARGET_ENCRYPT_CONNECTION`: Specifies if SQL encryption should be used for the target database connection. Must be either _true_ or _false_.
- `MSSQL_TRUST_SERVER_CERTIFICATE`: Specifies whether to use TLS to encrypt the target database connection and bypass walking the certificate chain to validate trust. Must be either _true_ or _false_.
- `DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT`: Configures whether to hide or show data associated with test clients by default. Must be either _true_ or _false_.
- `DASHBOARD_TEST_CLIENTS_PATTERN`: Configures which client ids to consider test clients (Match of the pattern to the client id --> test client). Note: Regular expression have to be in python syntax (see https://docs.python.org/3/library/re.html for more details) and the **entire** client id has to be match (e.g. if one wants to match all client ids with the prefix _test-_, one valid pattern would be `test-.*`).

The dashboard is exposed at port 5000 by default. For example, to launch a dashboard listening at _http://localhost:80_, which connects to a MSSQL server with the above exemplary credentials the following command may be used:

```bash
docker run --rm                                 		\
	-p 80:5000                                    		\
	-e MSSQL_HOSTNAME='10.8.16.44'                		\
	-e MSSQL_PORT='1433'                          		\
	-e MSSQL_DB='bkb-data'                        		\
	-e MSSQL_USER='admin'                         		\
	-e MSSQL_PASSWORD='pa$$w0rd554'               		\
	-e MSSQL_TARGET_ENCRYPT_CONNECTION='false'    		\
	-e MSSQL_TRUST_SERVER_CERTIFICATE='true'      		\
    -e DASHBOARD_HIDE_TEST_CLIENTS_DEFAULT='true' 		\
	-e DASHBOARD_TEST_CLIENTS_PATTERN='test-.*|.*-dev'  \
	"ghcr.io/js-soft/nmshd-bkb-data-dashboard:latest"
```

The dashboard server uses multi-process load balancing by default. The number of workers defaults to 4 can be set via the environment variable `DASHBOARD_NUM_WORKERS`. If your method of deployment has other means of horizontal scaling the built-in load balancing can be disabled by setting the number of workers to 1.

# Dev Setup

1. Clone the repository, ensure [Python ≥3.12](https://github.com/pyenv/pyenv), [Poetry](https://python-poetry.org/) and the [Work Sans font](https://fonts.google.com/specimen/Work+Sans) are installed. Then install all dependencies and activate your virtual environment.

    ```bash
    poetry install --with dev
    poetry shell
    ```

2. Provide the location and credentials for the backbone database server to use during development by setting the environment variables listed in the usage instructions above. `DASHBOARD_NUM_WORKERS` is not used in a dev setting.

3. (Optional) A local backbone mssql server and database can be bootstrapped from a local _.bacpac_ backup file using _dev/bootstrap-mssql.docker-compose.yml_. Check the file for information on what to configure.

4. Start the dashboard server locally via `python main.py`. The hostname and port default to _localhost_ and _5000_, respectively. To override these defaults use the environment variables:
    - `DASHBOARD_HOSTNAME`: Hostname or IP-address of dashboard server
    - `DASHBOARD_PORT`: Port of dashboard server

FROM ubuntu:22.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        wget \
        unzip \
        libunwind8 \
        libicu-dev \
    && rm -rf /var/lib/apt/lists/*


# Install sqlpackage following https://learn.microsoft.com/de-de/sql/tools/sqlpackage/sqlpackage-download?view=sql-server-ver16
ARG SQLPACKAGE_FOLDER="/opt/sqlpackage"
RUN wget https://aka.ms/sqlpackage-linux -O sqlpackage-linux-latest.zip \
    && unzip sqlpackage-linux-latest.zip -d ${SQLPACKAGE_FOLDER} \
    && rm sqlpackage-linux-latest.zip
RUN chmod +x ${SQLPACKAGE_FOLDER}/sqlpackage \
    && ln -s ${SQLPACKAGE_FOLDER}/sqlpackage /usr/local/bin


# Install mssql-tools following https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-setup-tools?view=sql-server-ver16&tabs=redhat-instal
RUN wget -O- -q https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc
RUN wget -O- -q https://packages.microsoft.com/config/ubuntu/22.04/prod.list | tee /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
        mssql-tools18 \
        unixodbc-dev \
        && rm -rf /var/lib/apt/lists/*

# Make executables of sqltools and sqlpackage available in PATH
ENV PATH="$PATH:/opt/mssql-tools18/bin"

COPY load_bacpac.sh /db-init/load_bacpac.sh
RUN chmod +x /db-init/load_bacpac.sh

ENTRYPOINT [ "/bin/sh", "-c" ]

FROM ubuntu:22.04

# Install basic tooling and dependencies
RUN apt-get update \
    && apt-get install -y \
        wget \
        unzip \
        libunwind8 \
        libicu-dev \
    && rm -rf /var/lib/apt/lists/*


# Install sqlpackage following https://learn.microsoft.com/de-de/sql/tools/sqlpackage/sqlpackage-download?view=sql-server-ver16
ARG SQLPACKAGE_FILE_NAME="sqlpackage-linux-latest.zip"
ARG SQLPACKAGE_FOLDER="/usr/local/sqlpackage"
RUN wget https://aka.ms/sqlpackage-linux -O ${SQLPACKAGE_FILE_NAME} \
    && unzip ${SQLPACKAGE_FILE_NAME} -d ${SQLPACKAGE_FOLDER} \
    && rm ${SQLPACKAGE_FILE_NAME}
RUN chmod a+x ${SQLPACKAGE_FOLDER}/sqlpackage


# Install mssql-tools following https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-setup-tools?view=sql-server-ver16&tabs=redhat-instal
RUN wget -O- -q https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc
RUN wget -O- -q https://packages.microsoft.com/config/ubuntu/22.04/prod.list | tee /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y \
        mssql-tools18 \
        unixodbc-dev \
        && rm -rf /var/lib/apt/lists/*

# Make executables of sqltools and sqlpackage available in PATH
ENV PATH="$PATH:/opt/mssql-tools18/bin"

ADD load_bacpac.sh /db-init/load_bacpac.sh
RUN chmod +x /db-init/load_bacpac.sh

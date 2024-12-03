#! /usr/bin/env bash

# Make sure sqlpackage is installed
if ! command -v sqlcmd &> /dev/null; then
    echo "sqlcmd is not installed. Please install it before running $0."
    exit 1
fi

# Make sure sqlpackage is installed
if ! command -v sqlpackage &> /dev/null; then
    echo "sqlpackage is not installed. Please install it before running $0."
    exit 1
fi

# check if connection to database is possible
if ! sqlcmd -S $MSSQL_HOSTNAME,$MSSQL_PORT -U $MSSQL_USER -P $MSSQL_PASSWORD -C -Q "SELECT 1" &> /dev/null; then
    echo "Connection to database at $MSSQL_HOSTNAME:$MSSQL_PORT failed for user $MSSQL_USER. Please check your connection settings."
    exit 1
fi

# if database exists, exit
if sqlcmd -S $MSSQL_HOSTNAME,$MSSQL_PORT -U $MSSQL_USER -P $MSSQL_PASSWORD -C -Q "SELECT name FROM sys.databases WHERE name = '$MSSQL_DB'" | grep -q $MSSQL_DB; then
    echo "Database $MSSQL_DB already exists. Please drop it before running $0 or start hacking."
    exit 0
fi

# import
sqlpackage \
    /Action:Import \
    /TargetServerName:$MSSQL_HOSTNAME,$MSSQL_PORT \
    /TargetDatabaseName:$MSSQL_DB \
    /TargetUser:$MSSQL_USER \
    /TargetPassword:$MSSQL_PASSWORD \
    /TargetEncryptConnection:false \
    /SourceFile:/db-init/backup.bacpac

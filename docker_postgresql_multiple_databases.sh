#!/bin/bash

set -e
set -u

function create_user_and_database() {
    local database=$(echo $1 | tr ',' ' ' | awk  '{print $1}')
    local owner=$(echo $1 | tr ',' ' ' | awk  '{print $2}')
    echo "  Creating user and database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE $database;
        GRANT ALL PRIVILEGES ON DATABASE $database TO $owner;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ':' ' '); do
        create_user_and_database $db
    done
    echo "Multiple databases created"
fi

# We have 8 gateway cluster workers with 10 connections each,
# dipdup and hasura. Let's take a guess and say we need 100 * 2.5.
echo "setting max connections"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    ALTER SYSTEM SET max_connections = 250;
EOSQL
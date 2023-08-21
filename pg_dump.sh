#! /usr/bin/env bash
# Puts the current date and time in the generated file.  Removed so it writes to stdout and can be passed to gzip.
# -f --file "pg_dump_$(date +"%Y-%d-%m_%H%M%S").sql"

# include commands to create database in dump
# -c --create

# dump data as INSERT commands with column names
# --column-inserts ?

# Connection info pulled from the .env file.  It does not account for quotes around the value.
# -d --dbname=$(grep "^DB_NAME" .env | cut -c9-)
# -h --host=$(grep "^DB_HOST" .env | cut -c9-)
# -p --port=$(grep "^DB_PORT" .env | cut -c9-)
# -U --username=$(grep "^DB_USER" .env | cut -c9-)

# use IF EXISTS when dropping objects
# --if-exists

# The output of pg_dump is piped to gzip which is redirected to the same date/time named file with ".gz" appended.
# gzip --stdout > "pg_dump_$(date +"%Y-%d-%m_%H%M%S").sql.gz"

# The full pg_dump command without gzip
# pg_dump -f "pg_dump_$(date +"%Y-%d-%m_%H%M%S").sql" -c -d $(grep "^DB_NAME" .env | cut -c9-) -h $(grep "^DB_HOST" .env | cut -c9-) -p $(grep "^DB_PORT" .env | cut -c9-) -U $(grep "^DB_USER" .env | cut -c9-) --if-exists

# The full pg_dump/gzip command
pg_dump -c -d $(grep "^DB_NAME" .env | cut -c9-) -h $(grep "^DB_HOST" .env | cut -c9-) -p $(grep "^DB_PORT" .env | cut -c9-) -U $(grep "^DB_USER" .env | cut -c9-) --if-exists | gzip --stdout > "data/pg_dump_$(date +"%Y-%d-%m_%H%M%S").sql.gz"


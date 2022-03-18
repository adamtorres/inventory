\set new_database `echo "$DB_NAME"`
\set new_user `echo "$DB_USER"`
\set new_user_password `echo "$DB_PASSWORD"`

CREATE DATABASE :new_database;
CREATE USER :new_user WITH PASSWORD :'new_user_password';
ALTER ROLE :new_user SET client_encoding TO 'utf8';
ALTER ROLE :new_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE :new_database TO :new_user;
ALTER ROLE :new_user CREATEDB;

-- Switch to the new database still as postgres user so we can add extensions
\c :new_database

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Switch to the :new_user so new tables will automatically be owned by :new_user.
\c :new_database :new_user

-- Would put the create table/view/etc statements here but am using Django to manage that part.

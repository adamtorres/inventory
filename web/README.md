### Setting an environment variable for just the run of the command.

```bat
cmd /V /C "set SHELL_PLUS_PYGMENTS_ENABLED=False&&python manage.py runscript report_test"
```

### load sql script directly on linux

```shell
psql -d $(grep "^DB_NAME" .env | cut -c9-) -h $(grep "^DB_HOST" .env | cut -c9-) -p $(grep "^DB_PORT" .env | cut -c9-) -U $(grep "^DB_USER" .env | cut -c9-) -f data/pg_dump_2023-09-10_160542_inventory_commonname.sql
```

The `$(grep "^DB_NAME" .env | cut -c9-)` bits grab the values from the `.env` file so they don't show in your shell history and so you can just copy/paste without having to change the command.


#### Or, if you don't mind usernames and passwords in your shell history
```shell
psql -d DATABASE_NAME -h localhost -p 5432 -U db_user -f data/pg_dump_2023-09-10_160542_inventory_commonname.sql
```

### load sql script directly on windows

Create a [pgpass.conf](https://www.postgresql.org/docs/current/libpq-pgpass.html) file as `%APPDATA%\postgresql\pgpass.conf`.
In my case, `%APPDATA%` was `C:\Users\____\AppData\Roaming`.  I had to create the `postgresql` folder as it wasn't
already there.

```bat
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -f data\pg_dump_2023-09-11_160615_inventory_commonname.sql "host='localhost' port='5432' dbname='inventory_test' user='inventory_user'" 2>>&1
```
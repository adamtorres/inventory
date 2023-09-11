
Setting an environment variable for just the run of the command.

```commandline
cmd /V /C "set SHELL_PLUS_PYGMENTS_ENABLED=False&&python manage.py runscript report_test"
```

load sql script directly on linux

```shell
psql -d $(grep "^DB_NAME" .env | cut -c9-) -h $(grep "^DB_HOST" .env | cut -c9-) -p $(grep "^DB_PORT" .env | cut -c9-) -U $(grep "^DB_USER" .env | cut -c9-) -f data/pg_dump_2023-09-10_160542_inventory_commonname.sql
```
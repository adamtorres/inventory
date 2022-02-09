# Layout

For development, I've decided to run the Django project locally and have the Postgres database in a docker container.
This is mainly because Django creates files based on commands (mainly `makemigrations`) and I didn't feel like working
out how to do that reliably in docker and still have the code in a repository.  Look at `bogus_example_redux` to see how a docker-hosted django project could be run from PyCharm.  The readme for that project seemed to be heading down that path and I believe I had it working.


# Running

The summary is the docker components need to start first.  Then the Django project.  Starting the docker components is
done with the basic `up` command.

```
docker-compose -f docker-compose.yml up --detach
```

Once the docker services are running, the Django project can be started.  Django needs the current working folder to be
the root of the Django project.  Before any further steps, change to the `web` folder.

## First Run

For the first run, migrations must be run.  The output shown is from when the custom app did not have any migrations so
all are from the Django apps.

```
./manage.py migrate
    Operations to perform:
      Apply all migrations: admin, auth, contenttypes, sessions
    Running migrations:
      Applying contenttypes.0001_initial... OK
      Applying auth.0001_initial... OK
      Applying admin.0001_initial... OK
      Applying admin.0002_logentry_remove_auto_add... OK
      Applying admin.0003_logentry_add_action_flag_choices... OK
      Applying contenttypes.0002_remove_content_type_name... OK
      Applying auth.0002_alter_permission_name_max_length... OK
      Applying auth.0003_alter_user_email_max_length... OK
      Applying auth.0004_alter_user_username_opts... OK
      Applying auth.0005_alter_user_last_login_null... OK
      Applying auth.0006_require_contenttypes_0002... OK
      Applying auth.0007_alter_validators_add_error_messages... OK
      Applying auth.0008_alter_user_username_max_length... OK
      Applying auth.0009_alter_user_last_name_max_length... OK
      Applying auth.0010_alter_group_name_max_length... OK
      Applying auth.0011_update_proxy_permissions... OK
      Applying auth.0012_alter_user_first_name_max_length... OK
      Applying sessions.0001_initial... OK
```

To make the admin portion of the site functional, a super user needs to be created.  In this example, I used a simple 
password as this database will be very short-lived and not contain anything of import.

```
./manage.py createsuperuser
    Username (leave blank to use 'adam'):
    Email address: adam@example.com
    Password:
    Password (again):
    This password is too common.
    Bypass password validation and create user anyway? [y/N]: y
    Superuser created successfully.
```

Or, including the user/email on the command line

```
./manage.py createsuperuser --username adam --email adam@example.com
    Password:
    Password (again):
    This password is too common.
    Bypass password validation and create user anyway? [y/N]: y
    Superuser created successfully.
```

Switched from using fixtures to using exports from two spreadsheets.  One has all of the invoices for 2021 and starting
into 2022.  The other is a unique listing of item names with associated common names and locations.  The following will
create the various objects including sources.
Missing the custom IncomingItemGroupDetail fields so some of this data is getting lost.  Might add some custom logic or
simply a new sheet from which to import the templates.

```
./manage.py ingest_common_items -f ../../invoices/common_names-2022-02-08.tsv
./manage.py ingest_invoices -f ../../invoices/incoming-2022-02-08.tsv --case LOWER --skip-lines 1
./manage.py apply_common_names -f ../../invoices/common_names-2022-02-08.tsv
```

For the debug service, the simple runserver is used.  That is started from within the `web` folder.  The following
assumes a terminal is opened to the root of the repository.

```
./manage.py runserver
```

## pgadmin4 and any other infrequently used services
The `pgadmin4` service adds a web-based graphical interface to Postgres.  Since it won't be needed often, it was
isolated via the `profiles` feature in the `docker-compose.yml` file.  By default, this allows the basic `up` command
to run without the additional service.

To start the `pgadmin4` service, add `--profile debug` to the command line.  In addition to services without a stated
profile, any services with the specified profile will start.  If no services in the project are currently running, this
will start all of them.  On the other hand, if the project was already started with a plain `up`, this command appears
to attach to the existing services and just starts the additional services.  The command line app seemed to not handle
stopping the second call cleanly so I've added the `--detach` to this one.

```
docker-compose -f docker-compose.yml --profile debug up --detach
```


# Development

Reinstalling a custom package while forcing pip to not use the cache.

```
pip install --force-reinstall --no-cache-dir git+https://github.com/adamtorres/unit-convert@master#egg=unit-convert
```

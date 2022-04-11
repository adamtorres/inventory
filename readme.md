# Layout

For development, I've decided to run the Django project locally and have the Postgres database in a docker container.
This is mainly because Django creates files based on commands (mainly `makemigrations`) and I didn't feel like working
out how to do that reliably in docker and still have the code in a repository.  Look at `bogus_example_redux` to see
how a docker-hosted django project could be run from PyCharm.  The readme for that project seemed to be heading down
that path and I believe I had it working.


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

To make the admin portion of the site functional, a super user needs to be created.  The seetings file has the simple password restrictions commented out for ease of entering in passwords while developing.  The boring and manual option for creating a super user is to use the built-in command and then manually set the password later.

```
./manage.py createsuperuser [--username some_name] [--email some_name@example.com]
```

Or, add `INITIAL_ADMIN_USER`, `INITIAL_ADMIN_EMAIL`, and `INITIAL_ADMIN_PASSWORD` to the `.env` file and run the following command which will create the user with the password.  This is how the ansible project creates the user.

```
./manage.py runscript create_super_user
```

Load the states for incoming records.
```
./manage.py loaddata raw_state
```

Current steps to import and process data from the spreadsheet.
```
# Remove all data at start - I've not tested updates much at all.
./manage.py show_counts
./manage.py runscript remove_data --script-args truncate

# Load the data.
./manage.py show_counts
./manage.py ingest_items -f ../../invoices/incoming-2022-03-29.tsv

# Clean the loaded records.
./manage.py process_items --clean
./manage.py show_counts
    # Check for new unit failures if there are failed records.
    ./manage.py show_issues --unit-size
    # If all is good, rerun do_clean with additional kwarg.
    ./manage.py process_items --clean --force-clean
    # Recheck for any more failures.  There should be none.
    ./manage.py show_counts

# Calculate totals.
./manage.py process_items --calculate
./manage.py show_counts

# Create supporting records.
./manage.py process_items --create
./manage.py show_counts

# Load common item names and assign to existing items.
./manage.py ingest_common_item_names -f ../../invoices/common_names-2022-03-31.tsv
# Show items missing common item names.
./manage.py show_issues --common-name

# Do the final import converting raw items to inventory in stock.
./manage.py process_items --import
./manage.py show_counts
```

For the debug service, the simple `runserver_plus` is used.  That is started from within the `web` folder.  The following assumes a terminal is opened to the root of the repository.

```
./manage.py runserver_plus
```

# Development

For development, the password restrictions are reduced.  I might see about switching to django-configurations so these
can be enabled/disabled simply by .env setting instead of commenting code.

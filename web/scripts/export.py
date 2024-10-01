import datetime
import locale
import os
import pathlib
import platform
import re
import subprocess

import dotenv

from django.apps import apps
from django.conf import settings
from django import db


def dump_pg_settings():
    output_formats = {
        "category": 70,
        "name": 40,
        "setting": 30,
        "short_desc": 30,
    }
    with db.connection.cursor() as cur:
        cur.execute("select * from pg_settings;")
        headers = [c.name for c in cur.description]
        for row in cur.fetchall():
            dict_row = {h: v for h, v in zip(headers, row)}
            print(" | ".join([str(dict_row[k]).ljust(v) for k, v in output_formats.items()]))


def get_models_to_sort():
    ignore_apps = ['admin', 'auth', 'contenttypes', 'sessions', 'drf_messages']
    return [m for m in apps.get_models() if m._meta.app_label not in ignore_apps]


def sort_models(models_to_sort, models_in_order=None):
    _models_in_order = (models_in_order or list())[:]
    _needs_work = []
    for m in models_to_sort:
        depends_on = set()
        for field in m._meta.fields:
            if field.related_model:
                depends_on.add(field.related_model)
        if depends_on.issubset(_models_in_order):
            # If depends_on is empty or all items are already in models_in_order.
            _models_in_order.append(m)
        else:
            _needs_work.append(m)
    if _needs_work:
        _models_in_order = sort_models(_needs_work, _models_in_order)
    return _models_in_order


def find_pg_dump_binary():
    tmp = "pg_dump"
    if platform.system().lower() == "windows":
        p = pathlib.Path(os.environ["ProgramFiles"])  # "C:\Program Files
        pg_path = p / "PostgreSQL"
        if not pg_path.exists():
            raise FileNotFoundError(f"Could not find pg_dump.  {pg_path} not found.")
        pg_version = max([int(folder.stem) for folder in pg_path.glob("*") if folder.stem.isdigit()])
        tmp = pg_path / str(pg_version) / "bin" / tmp
    return str(tmp)


def generate_datetime_slug():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")


def generate_export_filename(datetime_slug, table_name, prefix="pg_dump", extension="sql"):
    return pathlib.Path(os.environ.get("DATA_FOLDER", ".")) / f"{prefix}_{datetime_slug}_{table_name}.{extension}"


def generate_pg_dump_command(model, datetime_slug, for_script=False):
    db_args = [
        {"switch": "-d", "arg": "DB_NAME"},
        {"switch": "-h", "arg": "DB_HOST"},
        {"switch": "-p", "arg": "DB_PORT"},
        {"switch": "-U", "arg": "DB_USER"}
    ]
    read_from_env_template = '$(grep "^_ARG_=" .env | cut -c_LEN_-)'
    sql_file = generate_export_filename(datetime_slug, model._meta.db_table, prefix="pg_dump", extension="sql")
    kwargs = {
        "output_file": ["-f", f'{sql_file}'],
        "data-only": ["-a"],
        "inserts with column names instead of copy": ["--column-inserts"],
        "stub the on-conflict clause": ["--on-conflict-do-nothing"],
    }
    for arg in db_args:
        if for_script:
            tmp = read_from_env_template.replace("_ARG_", arg["arg"]).replace("_LEN_", str(len(arg["arg"])+2))
        else:
            tmp = os.environ.get(arg["arg"])
        kwargs[arg["arg"]] = [arg['switch'], tmp]
    command = [find_pg_dump_binary()]
    for kwarg in kwargs.values():
        command.extend(kwarg)
    command.append(f"--table={model._meta.db_table}")
    return {"command": command, "label": model._meta.db_table, "output_file": sql_file}


def generate_pg_dump_commands(sorted_model_list, datetime_slug):
    commands = []
    for model in sorted_model_list:
        commands.append(generate_pg_dump_command(model, datetime_slug))
    return commands


def execute_command(command):
    print(f"Exporting {command['label']}...")
    command_result = subprocess.run(command["command"], capture_output=True)
    if command_result.returncode:
        print(command_result)
        return
    modify_sql_script_insert_into_upsert(command["output_file"])


def execute_commands(commands):
    for command_dict in commands:
        execute_command(command_dict)


def modify_sql_script_insert_into_upsert(sql_file):
    """
    The scripts are generated with "ON CONFLICT DO NOTHING;".  This changes the "DO NOTHING" into an update.
    Creates a temp sql file with the modified INSERT commands, then renames the original to "..._noupdate.sql" and the
    new file to the original's original name.

    Example - Manually added line breaks and indentation.  Original had no line breaks.
    INSERT INTO public.recipe_recipe (
        id, created, modified, name, source, description, reason_to_not_make, star_acceptance, star_effort,
        common_multipliers, template)
        VALUES (
        '4e573964-f6fa-445b-9c9e-6df98e15e2cf', '2023-08-14 23:22:22.166051-06', '2023-08-14 23:22:22.166064-06',
        'Pumpkin Chocolate Chip', 'Center', 'Results in mounds.  Does not flatten.', '', 4, 4, '{2,4,8,16}', false)
        ON CONFLICT DO NOTHING;

    ./manage.py dbshell < ../data/pg_dump_2023-08-26_185702_recipe_recipe.sql
    """
    # Find field list.
    #   Should start with "(id, " and end at the first available ")".
    # Find "ON CONFLICT DO NOTHING;"
    field_list_pattern = r".* \(id, (.+?)\)"
    field_list_re = re.compile(field_list_pattern)
    new_sql_file = sql_file.with_suffix(".sql_tmp")
    with sql_file.open() as old_file, new_sql_file.open("w") as new_file:
        for original_line in old_file:
            # TODO: will data containing newlines be escaped and stay on one line?
            line = original_line.strip()
            new_line_characters = original_line[len(line):]
            if not (line.startswith("INSERT") and line.endswith("ON CONFLICT DO NOTHING;")):
                new_file.write(line + new_line_characters)
                continue
            field_list_matched = field_list_re.match(line)
            field_list = [f.strip() for f in field_list_matched.groups()[0].split(",")]
            update_str = "UPDATE SET "
            update_str += ", ".join(f"{field} = EXCLUDED.{field}" for field in field_list)
            update_str += ";"
            new_line = line[:-(len("DO NOTHING;"))] + "(id) DO " + update_str + new_line_characters
            new_file.write(new_line)
    sql_file = sql_file.rename(sql_file.with_stem(sql_file.stem + "_noupdate"))
    new_sql_file = new_sql_file.rename(new_sql_file.with_suffix(".sql"))


def run_pg_dump(models_in_order, datetime_slug):
    """
    Exports each table as a separate sql file.  To be used with the import runscript.
    """
    pg_dump_commands = generate_pg_dump_commands(models_in_order, datetime_slug)
    execute_commands(pg_dump_commands)


def run_dumpdata(models_in_order, datetime_slug):
    """
    Uses django's dumpdata manage command
    """
    if platform.system().lower() == "windows" and locale.getpreferredencoding() != "utf-8":
        raise UnicodeError("Please run as 'python -Xutf8 ...'")
    # python -Xutf8 manage.py dumpdata --output data\dumpdata_min.json
    from django.core import management
    # from django.core.management.commands import loaddata, dumpdata
    # dumpdata.Command()
    for model in models_in_order:
        print(f"Exporting {model._meta.label}")
        management.call_command("dumpdata",
            # "--indent", "2",
            "--output", generate_export_filename(
                datetime_slug, model._meta.db_table, prefix="dumpdata", extension="json"),
            model._meta.label
        )


def run():
    dotenv.read_dotenv('../../.env')
    model_list = get_models_to_sort()
    models_in_order = sort_models(model_list)
    datetime_slug = generate_datetime_slug()
    # Setting PGPASSWORD makes it so psql doesn't ask for a password each time.
    os.environ["PGPASSWORD"] = os.getenv("DB_PASSWORD")
    run_pg_dump(models_in_order, datetime_slug)
    run_dumpdata(models_in_order, datetime_slug)


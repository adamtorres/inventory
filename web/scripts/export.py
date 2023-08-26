import datetime
import locale
import os
import pathlib
import platform
import subprocess

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
    kwargs = {
        "output_file": [
            "-f",
            f'{generate_export_filename(datetime_slug, model._meta.db_table, prefix="pg_dump", extension="sql")}'],
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
    return command


def generate_pg_dump_commands(sorted_model_list, datetime_slug):
    commands = []
    for model in sorted_model_list:
        commands.append(generate_pg_dump_command(model, datetime_slug))
    return commands


def execute_command(command):
    command_result = subprocess.run(command, capture_output=True)
    if command_result.returncode:
        print(command_result)


def execute_commands(commands):
    for command in commands:
        execute_command(command)


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
    if locale.getpreferredencoding() != "utf-8":
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
    model_list = get_models_to_sort()
    models_in_order = sort_models(model_list)
    datetime_slug = generate_datetime_slug()
    # run_pg_dump(models_in_order, datetime_slug)
    run_dumpdata(models_in_order, datetime_slug)

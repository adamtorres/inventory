import datetime
import os
import subprocess

from django.apps import apps


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


def generate_pg_dump_command(model, datetime_slug, for_script=False):
    db_args = [
        {"switch": "-d", "arg": "DB_NAME"},
        {"switch": "-h", "arg": "DB_HOST"},
        {"switch": "-p", "arg": "DB_PORT"},
        {"switch": "-U", "arg": "DB_USER"}
    ]
    read_from_env_template = '$(grep "^_ARG_=" .env | cut -c_LEN_-)'
    kwargs = {
        "output_file": ["-f", f'pg_dump_{datetime_slug}_{model._meta.db_table}.sql'],
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
    command = ["pg_dump"]
    for kwarg in kwargs.values():
        command.extend(kwarg)
    command.append(f"--table={model._meta.db_table}")
    return command


def generate_pg_dump_commands(sorted_model_list):
    commands = []
    datetime_slug = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
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


def run():
    """
    Exports each table as a separate sql file.  To be used with the import runscript.
    """
    model_list = get_models_to_sort()
    models_in_order = sort_models(model_list)
    pg_dump_commands = generate_pg_dump_commands(models_in_order)
    execute_commands(pg_dump_commands)

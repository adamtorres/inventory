import collections
import os
import pathlib
import platform
import re
import subprocess

from . import export

datetime_pattern = (
    r".*(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})_(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})_.*")
datetime_re = re.compile(datetime_pattern)
datetime_slug_pattern = r".*(?P<slug>\d{4}-\d{2}-\d{2}_\d{6})_.*"
datetime_slug_re = re.compile(datetime_slug_pattern)


def get_datetime_slug_from_filename(filename):
    # pg_dump_2023-08-26_094300_inventory_commonname.sql
    m = datetime_slug_re.match(filename.stem)
    if not m:
        return ""
    return m.group("slug")


def find_exports(prefix="pg_dump", extension="sql", folder=".", models=None):
    """
    Searches path for files matching pattern "{prefix}_YYYY-MM-DD_HHMMSS_{table_name}.{extension}".  Returns list of
    files with the most recent datetime slug.  Expects all files in the same export to have the same slug.
    """
    export_batches = collections.defaultdict(list)
    data_folder = pathlib.Path(folder)
    for model in models:
        for data_file in data_folder.glob(f"{prefix}_*_{model._meta.db_table}.{extension}"):
            export_batches[get_datetime_slug_from_filename(data_file)].append(data_file)
    valid_export_batches = []
    for datetime_slug in export_batches.keys():
        if len(export_batches[datetime_slug]) != len(models):
            # batch is missing some files.  Ignore it.
            continue
        valid_export_batches.append(datetime_slug)
    selected_export_batch = max(valid_export_batches)
    return [data_file for data_file in export_batches[selected_export_batch]]


def find_psql_binary():
    tmp = "psql"
    if platform.system().lower() == "windows":
        p = pathlib.Path(os.environ["ProgramFiles"])  # "C:\Program Files
        pg_path = p / "PostgreSQL"
        if not pg_path.exists():
            raise FileNotFoundError(f"Could not find psql.  {pg_path} not found.")
        pg_version = max([int(folder.stem) for folder in pg_path.glob("*") if folder.stem.isdigit()])
        tmp = pg_path / str(pg_version) / "bin" / tmp
    return str(tmp)


def sort_files_based_on_models(files_to_sort, models_in_order):
    """
    Uses models_in_order to sort the files.  Files should be named with the pattern
    "pg_dump_YYYY-MM-DD_HHMMSS_{table_name}.sql" Or
    "dumpdata_YYYY-MM-DD_HHMMSS_{table_name}.json"
    Should work regardless so we don't have to pass prefix and extension.
    """
    table_names = [m._meta.db_table for m in models_in_order]
    files_in_order = [None for i in range(len(table_names))]
    for filename in files_to_sort:
        m = re.match(r".*\d_(?P<table_name>.*)\..*", filename.name)
        if not m:
            continue
        files_in_order[table_names.index(m.group("table_name"))] = filename
    return files_in_order


def execute_command(command):
    print(f"Importing {command['input_file']}...")
    command_result = subprocess.run(command["command"], capture_output=True)
    if command_result.returncode:
        print(command_result)
        return
    print(command_result.stdout.decode())


def execute_commands(commands):
    for command_dict in commands:
        execute_command(command_dict)


def generate_import_command(file_to_import, psql_binary):
    command = [psql_binary]
    # "C:\Program Files\PostgreSQL\15\bin\psql.exe"
    # -f data\pg_dump_2023-09-11_160615_inventory_commonname.sql
    # "host='localhost' port='5432' dbname='inventory_test' user='inventory_user'"
    # 2>>&1
    command.append("-f")
    command.append(str(file_to_import))
    # TODO: find windows way to grep the .env file.
    command.append("host='127.0.0.1' port='5432' dbname='inventory_db_v7' user='inventory_user'")
    command.append("2>>&1")
    return {"command": command, "label": "?", "input_file": file_to_import}


def generate_import_commands(files_to_import):
    """
    Generates a list of commands to import the specified files.
    """
    psql_binary = find_psql_binary()
    commands = []
    for file_to_import in files_to_import:
        commands.append(generate_import_command(file_to_import, psql_binary))
    return commands


def run():
    """
    Imports each model's data in the order that respects dependencies.  To be used with sql files generated by the
    export runscript.
    """
    model_list = export.get_models_to_sort()
    models_in_order = export.sort_models(model_list)
    import_formats = {
        "json": {"prefix": "dumpdata", "extension": "json"},
        "sql": {"prefix": "pg_dump", "extension": "sql"},
    }
    import_format = "sql"

    files_to_import = find_exports(
        prefix=import_formats[import_format]["prefix"], extension=import_formats[import_format]["extension"],
        folder=os.environ.get("DATA_FOLDER", "."), models=models_in_order)
    sorted_files_to_import = sort_files_based_on_models(files_to_import, models_in_order)
    import_commands = generate_import_commands(sorted_files_to_import)
    print(import_commands[-1])
    execute_commands(import_commands)

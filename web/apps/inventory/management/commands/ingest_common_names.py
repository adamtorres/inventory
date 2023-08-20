from collections import defaultdict

from ... import models as inv_models
from scrap import commands


class Command(commands.IngestCommand):
    script_name = "ingest_source_items"
    help_text = "Load source items from a file."
    # replace_empty_str_fields = []
    # replace_empty_str_value = 0
    data_row_fields = [
        "x1", "x2", "x6", "x3", "source_item_name", "better_name", "x4", "common_name_1",
        "common_name_2", "common_name_3", "common_name_4", "x5",
    ]

    def create_common_names(self, data):
        items_to_create = []
        for cryptic_name in data["cryptic_names"].keys():
            items_to_create.append(inv_models.CommonName(
                cryptic_name=cryptic_name,
                verbose_name=data["cryptic_names"][cryptic_name]["verbose_name"],
                common_names=data["cryptic_names"][cryptic_name]["common_names"],
            ))
            if len(items_to_create) > 100:
                print("Saving a batch...")
                inv_models.CommonName.objects.bulk_create(items_to_create)
                items_to_create.clear()
        if items_to_create:
            print("Saving last batch...")
            inv_models.CommonName.objects.bulk_create(items_to_create)
            items_to_create.clear()

    def initialize_data(self):
        return {
            "record_count": 0,
            "cryptic_names": {},
            "dupes": defaultdict(int),
        }

    def process_output(self, data):
        print("Output:")
        for k in data.keys():
            if k != "cryptic_names":
                print(f"{k}: {data[k]}")
            else:
                print(f"{k}: {len(data[k])} items in list.")
        self.create_common_names(data)

    def process_row(self, row_number, named_row, data):
        data["record_count"] += 1
        common_names = [
            cn for cn in [
                named_row.common_name_1, named_row.common_name_2, named_row.common_name_3, named_row.common_name_4
            ] if cn]

        if named_row.source_item_name in data["cryptic_names"]:
            data["dupes"][named_row.source_item_name] += 1
        else:
            data["cryptic_names"][named_row.source_item_name] = {
                "verbose_name": named_row.better_name,
                "common_names": common_names
            }

from collections import defaultdict

from scrap import commands


class Command(commands.IngestCommand):
    script_name = "ingest_source_items"
    help_text = "Load source items from a file."
    # replace_empty_str_fields = []
    # replace_empty_str_value = 0
    data_row_fields = [
        "source", "order_date", "delivered_date", "customer_number", "department", "po_text", "order_number",
        "line_item_number", "category", "delivered_quantity", "pack_quantity", "unit_size", "item_name", "extra_code",
        "item_code", "pack_cost", "pack_tax", "extended_cost", "total_weight", "extra_notes", "scan_file", "checked"
    ]

    def initialize_data(self):
        return {
            "record_count": 0,
            "sources": defaultdict(int),
            "categories": defaultdict(int),
        }

    def process_output(self, data):
        print("Output:")
        for k in data.keys():
            print(f"{k}: {data[k]}")

    def process_row(self, row_number, named_row, data):
        data["record_count"] += 1
        data["sources"][named_row.source] += 1
        data["categories"][named_row.category] += 1

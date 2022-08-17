import datetime
from collections import defaultdict

from ... import models as inv_models
from scrap import commands


class Command(commands.IngestCommand):
    script_name = "ingest_source_items"
    help_text = "Load source items from a file."
    # replace_empty_str_fields = []
    # replace_empty_str_value = 0
    data_row_fields = [
        "source", "order_date", "delivered_date", "customer_number", "department", "po_text", "order_number",
        "line_item_number", "source_category", "delivered_quantity", "pack_quantity", "unit_size", "item_name",
        "extra_code", "item_code", "pack_cost", "pack_tax", "extended_cost", "total_weight", "extra_notes", "scan_file",
        "checked"
    ]

    def create_source_items(self, data):
        items_to_create = []
        for rec in data["records"]:
            items_to_create.append(inv_models.SourceItem(
                source=data["source_objs"][rec.source],
                customer_number=rec.customer_number,
                order_number=rec.order_number,
                po_text=rec.po_text,
                line_item_number=rec.line_item_number,
                source_category=rec.source_category,
                cryptic_name=rec.item_name,
                item_code=rec.item_code,
                delivered_quantity=rec.delivered_quantity,
                pack_cost=rec.pack_cost,
                pack_quantity=rec.pack_quantity,
                unit_size=rec.unit_size,
                extended_cost=rec.extended_cost,
                total_weight=rec.total_weight,
                extra_notes=rec.extra_notes,
                extra_code=rec.extra_code,
                scanned_filename=rec.scan_file,
                delivered_date=rec.delivered_date,
            ))
            if len(items_to_create) > 100:
                print("Saving a batch...")
                inv_models.SourceItem.objects.bulk_create(items_to_create)
                items_to_create.clear()
        if items_to_create:
            print("Saving last batch...")
            inv_models.SourceItem.objects.bulk_create(items_to_create)
            items_to_create.clear()

    def initialize_data(self):
        return {
            "record_count": 0,
            "sources": defaultdict(int),
            "source_categories": defaultdict(int),
            "records": [],
            "min_date": None,
            "max_date": None,
        }

    def postclean_row(self, named_row):
        if named_row.pack_quantity <= 0:
            named_row.pack_quantity = 1
        return named_row

    def preclean_row(self, raw_row_data):
        raw_row_data = self.text_to_date(raw_row_data, ['delivered_date'])
        raw_row_data = self.text_to_number(
            raw_row_data, ["delivered_quantity", "line_item_number", "pack_quantity"], int, 1)
        raw_row_data = self.text_to_number(raw_row_data, ["total_weight", "pack_cost", "extended_cost"], float, 0)
        return super().preclean_row(raw_row_data)

    def process_output(self, data):
        print("Output:")
        for k in data.keys():
            if k != "records":
                print(f"{k}: {data[k]}")
            else:
                print(f"{k}: {len(data[k])} items in list.")
        self.update_sources(data)
        self.create_source_items(data)

    def process_row(self, row_number, named_row, data):
        data["record_count"] += 1
        data["sources"][named_row.source] += 1
        data["source_categories"][named_row.source_category] += 1
        data["records"].append(named_row)
        if data["min_date"] is None or named_row.delivered_date < data["min_date"]:
            data["min_date"] = named_row.delivered_date
        if data["max_date"] is None or named_row.delivered_date > data["max_date"]:
            data["max_date"] = named_row.delivered_date

    def update_sources(self, data):
        existing_sources = inv_models.Source.objects.filter(
            name__in=data["sources"].keys()).values_list('name', flat=True)
        print(f"Existing sources: {existing_sources}")
        file_sources = set(data["sources"].keys())
        new_sources = list(file_sources.difference(existing_sources))
        if new_sources:
            print(f"Creating sources: {new_sources}")
            inv_models.Source.objects.bulk_create(inv_models.Source(name=n) for n in new_sources)
        data["source_objs"] = {
            obj.name: obj
            for obj in inv_models.Source.objects.filter(name__in=data["sources"].keys())
        }

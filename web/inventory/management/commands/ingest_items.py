from scrap import commands
from ... import models as inv_models


class Command(commands.Command):
    script_name = "ingest_items"
    help_text = """
    Ingest data from a tsv exported from the inventory Google Sheet.
    """
    replace_empty_str_fields = ['pack_quantity', 'pack_tax', 'quantity']
    data_row_fields = [
        "source", "order_date", "delivery_date", "customer_number", "department", "po_text", "order_number",
        "line_item_number", "category", "quantity", "pack_quantity", "unit_size", "item_name", "extra_code",
        "item_code", "pack_cost", "pack_tax", "extended_cost", "total_weight", "handwritten_notes", "scan_file",
        "checked"]

    def initialize_data(self):
        data = {
            "records": 0,
            "min_delivery_date": None,
            "max_delivery_date": None,
            "objects": [],
        }
        return data

    def preclean_row(self, raw_row_data):
        raw_row_data = super().preclean_row(raw_row_data)
        must_be_int_fields = ["quantity", "pack_quantity", "line_item_number"]
        must_be_float_fields = ["pack_cost", "pack_tax", "extended_cost", "total_weight"]
        must_be_date_fields = ["delivery_date", "order_date"]
        raw_row_data = self.text_to_number(raw_row_data, must_be_int_fields, int, 0)
        raw_row_data = self.text_to_number(raw_row_data, must_be_float_fields, float, 0)
        raw_row_data = self.text_to_date(raw_row_data, must_be_date_fields)
        return raw_row_data

    def process_output(self, data):
        print(f"records = {data['records']}")
        print(f"min_delivery_date = {data['min_delivery_date']}")
        print(f"max_delivery_date = {data['max_delivery_date']}")
        print(f"Attempting to insert {len(data['objects'])} objects...")
        inv_models.RawIncomingItem.objects.bulk_create(data['objects'])
        inv_models.RawIncomingItem.reports.console_group_by_current_state()
        print("done.")

    def process_row(self, row_number, named_row, data):
        data["records"] += 1
        if data["min_delivery_date"] is None:
            data["min_delivery_date"] = named_row.delivery_date
        elif data["min_delivery_date"] > named_row.delivery_date:
            data["min_delivery_date"] = named_row.delivery_date

        if data["max_delivery_date"] is None:
            data["max_delivery_date"] = named_row.delivery_date
        elif data["max_delivery_date"] < named_row.delivery_date:
            data["max_delivery_date"] = named_row.delivery_date

        data["objects"].append(inv_models.RawIncomingItem(
            source=named_row.source,
            customer_number=named_row.customer_number,
            department=named_row.department,
            order_number=named_row.order_number,
            po_text=named_row.po_text,
            order_date=named_row.order_date,
            delivery_date=named_row.delivery_date,
            line_item_position=named_row.line_item_number,
            category=named_row.category,
            name=named_row.item_name,
            item_code=named_row.item_code,
            extra_code=named_row.extra_code,
            unit_size=named_row.unit_size,
            ordered_quantity=named_row.quantity,
            delivered_quantity=named_row.quantity,
            total_weight=named_row.total_weight,
            pack_quantity=named_row.pack_quantity,
            pack_price=named_row.pack_cost,
            pack_tax=named_row.pack_tax,
            extended_price=named_row.extended_cost,
            item_comment=named_row.handwritten_notes,
            scanned_image_filename=named_row.scan_file,
        ))

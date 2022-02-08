from dateutil import parser

from incoming import models as inc_models
from inventory import models as inv_models
from scrap import ingest_file


class Command(ingest_file.Command):
    script_name = "ingest_invoices"
    help_text = """
    Ingest invoice data from a tsv exported from the inventory Google Sheet.
    """
    replace_empty_str_fields = ['pack_quantity', 'pack_tax', 'quantity']
    data_row_fields = [
        "source", "order_date", "delivery_date", "customer_number", "department", "po_text", "order_number",
        "line_item_number", "category", "quantity", "pack_quantity", "unit_size", "item_name", "extra_crap",
        "item_code", "pack_cost", "pack_tax", "extended_cost", "total_weight", "handwritten_notes", "scan_file"]

    def initialize_data(self):
        return {
            "records": 0,  # total record count for the file.
            "invoices": {},
            "sources": set(),
            "items": set(),
            "categories": set(),
        }

    def preclean_row(self, raw_row_data):
        must_be_number_fields = ["quantity", "pack_quantity", "extended_cost"]
        raw_row_data = super().preclean_row(raw_row_data)
        for field in must_be_number_fields:
            value = raw_row_data[self.field_index[field]]
            if isinstance(value, (int, float)):
                continue
            try:
                value = float(value)
            except ValueError:
                value = 0
            raw_row_data[self.field_index[field]] = value

        as_date = ["delivery_date", "order_date"]
        for field in as_date:
            value = raw_row_data[self.field_index[field]]
            if value:
                try:
                    raw_row_data[self.field_index[field]] = parser.parse(value).strftime("%Y-%m-%d")
                except parser.ParserError:
                    raw_row_data[self.field_index[field]] = ""

        # if raw_row_data[self.field_index["category"]] == "":
        #     raw_row_data[self.field_index["category"]] = "missing"
        return raw_row_data

    def process_row(self, row_number, named_row, data):
        data["records"] += 1
        data["sources"].add(named_row.source)
        if named_row.category:
            data["categories"].add(named_row.category)
        data["items"].add(named_row.item_name)

        # Build the invoice key leaving out empty fields.
        invoice_key = " - ".join([
            v for v in [
                named_row.delivery_date, named_row.department, named_row.order_number, named_row.po_text]
            if v])
        if invoice_key not in data["invoices"]:
            data["invoices"][invoice_key] = {
                "source": named_row.source,
                "order_date": named_row.order_date,
                "delivery_date": named_row.delivery_date,
                "department": named_row.department,
                "order_number": named_row.order_number,
                "po_text": named_row.po_text,
                "customer_number": named_row.customer_number,
                "line_items": [],
                "total_cost": 0.0,
                "total_packs": 0,
            }
        data["invoices"][invoice_key]["line_items"].append({
            "line_item_number": named_row.line_item_number,
            "category": named_row.category,
            "quantity": named_row.quantity,
            "pack_quantity": named_row.pack_quantity,
            "unit_size": named_row.unit_size,
            "item_name": named_row.item_name,
            "extra_crap": named_row.extra_crap,
            "item_code": named_row.item_code,
            "pack_cost": named_row.pack_cost,
            "pack_tax": named_row.pack_tax,
            "extended_cost": named_row.extended_cost,
            "total_weight": named_row.total_weight,
            "handwritten_notes": named_row.handwritten_notes,
        })
        data["invoices"][invoice_key]["total_cost"] += named_row.extended_cost
        data["invoices"][invoice_key]["total_packs"] += named_row.quantity * named_row.pack_quantity

    def process_output(self, data):
        print(f"Total records: {data['records']}")
        print()
        print(f"Sources: {data['sources']}")
        sources = inc_models.Source.objects.filter(name__in=data["sources"]).values_list('name', flat=True)
        print(f"DB sources: {sources}")
        if data["sources"].difference(sources):
            print("Source mismatch!")
            missing_sources = []
            for source in data["sources"].difference(sources):
                print(f"Missing {source}, creating...")
                missing_sources.append(inc_models.Source(name=source))
            inc_models.Source.objects.bulk_create(missing_sources)
        print()
        print(f"Categories: {data['categories']}")
        categories = inv_models.Category.objects.filter(name__in=data["categories"]).values_list('name', flat=True)
        print(f"DB categories: {categories}")
        if data["categories"].difference(categories):
            print("Category mismatch!")
            missing_categories = []
            for category in data["sources"].difference(sources):
                print(f"Missing {category}, creating...")
                missing_categories.append(inv_models.Category(name=category))
            inv_models.Category.objects.bulk_create(missing_categories)
        print()
        print(f"Invoices({len(data['invoices'])}):")
        # for invoice_key, invoice_data in data["invoices"].items():
        #     print(f"\t{invoice_key} has {len(invoice_data['line_items'])} records.")

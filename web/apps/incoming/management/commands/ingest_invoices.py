from dateutil import parser

from django.db import models
from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper

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
            "items": {},
            "categories": set(),
        }

    def preclean_row(self, raw_row_data):
        raw_row_data = super().preclean_row(raw_row_data)

        must_be_int_fields = ["quantity", "pack_quantity", "line_item_number"]
        for field in must_be_int_fields:
            value = raw_row_data[self.field_index[field]]
            if isinstance(value, int):
                continue
            try:
                value = int(value)
            except ValueError:
                value = 0
            raw_row_data[self.field_index[field]] = value

        must_be_float_fields = ["pack_cost", "pack_tax", "extended_cost", "total_weight"]
        for field in must_be_float_fields:
            value = raw_row_data[self.field_index[field]]
            if isinstance(value, float):
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
        item = {
            "source": named_row.source,
            "identifier": named_row.item_code,
            "name": named_row.item_name,
            "pack_quantity": named_row.pack_quantity,
            "unit_size": named_row.unit_size,
            "records": 0,
            "first_delivery_date": named_row.delivery_date,
            "last_delivery_date": named_row.delivery_date,
        }
        item_key = f"{item['source']}/{item['identifier']}/{item['name']}/{item['pack_quantity']}/{item['unit_size']}"
        if item_key not in data["items"]:
            data["items"][item_key] = item
        data["items"][item_key]["records"] += 1
        data["items"][item_key]["last_delivery_date"] = named_row.delivery_date

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

    def do_sources(self, data):
        # TODO: Add source details somehow.
        print(f"Sources: {data['sources']}")
        sources = list(inc_models.Source.objects.filter(name__in=data["sources"]).values_list('name', flat=True))
        if data["sources"].difference(sources):
            print("Source mismatch!")
            missing_sources = []
            for source in data["sources"].difference(sources):
                print(f"Missing {source}, creating...")
                missing_sources.append(inc_models.Source(name=source))
            inc_models.Source.objects.bulk_create(missing_sources)

    def do_categories(self, data):
        print(f"Categories: {data['categories']}")
        categories = list(
            inv_models.Category.objects.filter(name__in=data["categories"]).values_list('name', flat=True))
        if data["categories"].difference(categories):
            print("Category mismatch!")
            missing_categories = []
            for category in data["categories"].difference(categories):
                print(f"Missing {category}, creating...")
                missing_categories.append(inv_models.Category(name=category))
            inv_models.Category.objects.bulk_create(missing_categories)

    def do_incoming_items(self, data):
        print(f"Items({len(data['items'])})")
        data["item_cache"] = {
            f"{i.source.name}/{i.identifier}/{i.name}/{int(i.pack_quantity)}/{i.unit_size}": i
            for i in inc_models.Item.objects.all()
        }
        db_items = set(data["item_cache"].keys())
        file_items = set(data["items"].keys())
        if file_items.difference(db_items):
            print("Item mismatch!")
            in_file_only = file_items.difference(db_items)
            in_file_and_db = file_items.intersection(db_items)
            print(f"Items only in file: {len(in_file_only)}")
            print(f"Items in both file and db: {len(in_file_and_db)}")
            missing_items = []
            sources = {s.name: s for s in inc_models.Source.objects.filter(name__in=data["sources"])}
            for item in in_file_only:
                item_dict = data["items"][item]
                print(
                    f"\t{item}: hits({item_dict['records']}) first({item_dict['first_delivery_date']}) "
                    f"last({item_dict['last_delivery_date']})")
                missing_items.append(inc_models.Item(
                    source=sources[item_dict["source"]],
                    identifier=item_dict["identifier"],
                    name=item_dict["name"],
                    # individual_serving="?",
                    pack_quantity=item_dict["pack_quantity"],
                    unit_size=item_dict["unit_size"],
                ))
            inc_models.Item.objects.bulk_create(missing_items)
        # bulk_create doesn't return the created items.  Could possibly work out how to select only the new ones.
        # Just redo the entire dict.
        data["item_cache"] = {
            f"{i.source.name}/{i.identifier}/{i.name}/{int(i.pack_quantity)}/{i.unit_size}": i
            for i in inc_models.Item.objects.all()
        }

    def do_invoices(self, data):
        item_cache = data["item_cache"]
        print(f"Invoices({len(data['invoices'])}):")
        limit = 3
        source_dict = {s.name: s for s in inc_models.Source.objects.all()}
        for invoice_key, invoice_data in data["invoices"].items():
            limit -= 1
            # if limit < 0:
            #     break
            print(f"\t{invoice_key} has {len(invoice_data['line_items'])} records.")
            iig = inc_models.IncomingItemGroup(
                source=source_dict[invoice_data["source"]],
                action_date=invoice_data["delivery_date"],
                descriptor=invoice_key,
            )
            iig.save()
            iig.add_details()
            # department=invoice_data["department"],
            # order_number=invoice_data["order_number"],
            # po_text=invoice_data["po_text"],
            # customer_number=invoice_data["customer_number"],
            details_to_update = []
            for detail in iig.details.all():
                if detail.name == 'order date' and invoice_data["order_date"]:
                    detail.content = invoice_data["order_date"]
                    details_to_update.append(detail)
                if detail.name == 'department' and invoice_data["department"]:
                    detail.content = invoice_data["department"]
                    details_to_update.append(detail)
                if detail.name == 'order number' and invoice_data["order_number"]:
                    detail.content = invoice_data["order_number"]
                    details_to_update.append(detail)
                if detail.name == 'customer number' and invoice_data["customer_number"]:
                    detail.content = invoice_data["customer_number"]
                    details_to_update.append(detail)
                if detail.name == 'po text' and invoice_data["po_text"]:
                    detail.content = invoice_data["po_text"]
                    details_to_update.append(detail)
            if details_to_update:
                inc_models.IncomingItemGroupDetail.objects.bulk_update(details_to_update, ['content'])
            items_to_add = []
            for item in invoice_data["line_items"]:
                items_to_add.append(inc_models.IncomingItem(
                    parent=iig,
                    item=item_cache[
                        f"{invoice_data['source']}/{item['item_code']}/{item['item_name']}/{item['pack_quantity']}/"
                        f"{item['unit_size']}"],
                    ordered_quantity=float(item["quantity"]),
                    delivered_quantity=float(item["quantity"]),
                    total_weight=item["total_weight"],
                    pack_price=item["pack_cost"],
                    pack_tax=item["pack_tax"],
                    extended_price=item["extended_cost"],
                    line_item_position=item["line_item_number"],
                    comment=item["handwritten_notes"]
                ))
            inc_models.IncomingItem.objects.bulk_create(items_to_add)
            # "category": named_row.category,
            # "pack_quantity": named_row.pack_quantity,
            # "unit_size": named_row.unit_size,
            # "item_name": named_row.item_name,
            # "extra_crap": named_row.extra_crap,
            # "item_code": named_row.item_code,

    def process_output(self, data):
        print(f"Total records: {data['records']}")
        self.do_sources(data)
        self.do_categories(data)
        self.do_incoming_items(data)
        self.do_invoices(data)
        print()

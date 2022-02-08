from scrap import ingest_file


class Command(ingest_file.Command):
    script_name = "ingest_invoices"
    help_text = """
    Ingest invoice data from a tsv exported from the inventory Google Sheet.
    """
    replace_empty_str_fields = ['pack_quantity', 'pack_tax']

    def initialize_data(self):
        return {
            "records": 0,
            "categories": {},
            "sources": {}
        }

    def process_row(self, row_number, named_row, data):
        data["records"] += 1

        if named_row.category not in data["categories"]:
            data["categories"][named_row.category] = []
        data["categories"][named_row.category].append(named_row)

        if named_row.source not in data["sources"]:
            data["sources"][named_row.source] = {"records": 0}
        data["sources"][named_row.source]["records"] += 1

    def process_output(self, data):
        print(f"Total records: {data['records']}")
        
        print("Categories:")
        for category, category_data in data["categories"].items():
            print(f"\t{category} has {len(category_data)} records.")

        print("Sources:")
        for source, source_data in data["sources"].items():
            print(f"\t{source} has {source_data['records']} records.")

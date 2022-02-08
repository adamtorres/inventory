from scrap import ingest_file


class Command(ingest_file.Command):
    script_name = "ingest_invoices"
    help_text = """
    Ingest invoice data from a tsv exported from the inventory Google Sheet.
    """
    replace_empty_str_fields = ['pack_tax']

    def process_row(self, row_number, named_row):
        if row_number == 10:
            print(named_row)

    def process_output(self, data):
        print(f"data has keys: {data.keys()}")

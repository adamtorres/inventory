from django.test.client import RequestFactory
from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper

from inventory import views as inv_views


def run():
    empty_url_data = {
        'empty': 'true',
        'wide_filter_fields[]': ['name', 'order_number', 'general', 'quantity', 'unit_size'],
        'name': '',
        'order_number': '',
        'general': '',
        'quantity': '27',
        'unit_size': '',
    }
    current_url_data = empty_url_data.copy()
    current_url_data.update({
        'name': 'milk',
        'unit_size': '8oz',
        'empty': 'false',
    })
    # %5B%5D
    url = "/inventory/api/sourceitem/wide_filter/"

    with monkey_patch_cursordebugwrapper(print_sql=False, confprefix="SHELL_PLUS", print_sql_location=False):
        request_factory = RequestFactory()
        request = request_factory.get(url, current_url_data)
        print(f"request: {request}")
        api_view = inv_views.SourceItemWideFilterView()
        search_terms = api_view.request_params_to_search_terms(request)
        print(f"search_terms: {search_terms}\n")
        qs = api_view.filter_qs(search_terms)
        print(f"qs = {qs}")

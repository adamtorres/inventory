import logging

from inventory import models as inv_models


logger = logging.getLogger(__name__)


def run_search(search_criteria):
    logger.debug(f"Name: {search_criteria.name}")
    logger.debug(f"Description: {search_criteria.description}")
    logger.debug(f"Criteria: {search_criteria.criteria}")
    last_item = search_criteria.get_last_result()
    fields = [
        "delivered_date", "source", "name", "pack_cost", "pack_quantity",
        "unit_quantity", "unit_size", "extended_cost", "delivered_quantity", "total_weight", "use_type"]
    for f in fields:
        print(f"{f} = {getattr(last_item, f)!r}")
    print(f"per_use_cost = {last_item.per_use_cost(round_places=4)}")
    print(f"calculated pack_cost = {last_item.calculated_pack_cost(round_places=4)}")


def run_searches():
    for search_criteria in inv_models.SearchCriteria.objects.all():
        run_search(search_criteria)


def show_searches_available():
    qs = inv_models.SearchCriteria.objects.all()
    for sc in qs:
        logger.debug(f"{sc.name}, {sc.description or 'no description'}")


def run():
    show_searches_available()
    run_searches()

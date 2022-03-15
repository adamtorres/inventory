from .. import models as inv_models


def _do_create(batch_size=1):
    """
    step 4
    """
    qs = inv_models.RawIncomingItem.objects.ready_to_create()
    if batch_size > 0:
        qs = qs[:batch_size]
    print(f"do_create found {qs.count()} records to create.")

    sources = create_sources(qs)
    print(f"do_create created {len(sources)} sources: {sources}")
    assigned_source_count = assign_sources(qs)
    print(f"do_create assigned {assigned_source_count} sources")
    departments = create_departments(qs)
    print(f"do_create created {len(departments)} departments: {departments}")
    categories = create_categories(qs)
    print(f"do_create created {len(categories)} categories: {categories}")

    items_to_update = []
    fields_to_update = {'state'}
    for i, item in enumerate(qs):
        item.state = item.state.next_state
        items_to_update.append(item)
    return items_to_update, fields_to_update


def assign_sources(qs):
    results = []
    for source in inv_models.Source.objects.active_sources():
        ret = qs.filter(source=source.name).update(source_obj=source)
        results.append(ret)
    return sum(results)


def create_things(qs, model, manager_func_name, raw_field):
    """
    generic function used to create categories, department, and sources
    """
    manager_func = getattr(inv_models.RawIncomingItem.objects, manager_func_name)
    objs_to_create = []
    obj_names = []
    for raw_thing in manager_func(qs=qs, only_new=True):
        objs_to_create.append(model(name=raw_thing[raw_field]))
        obj_names.append(raw_thing[raw_field])
    if objs_to_create:
        # Note: Postgresql seems to return the ids from bulk_create.  A comment in the Django code implies this might
        # be the only db as it says Oracle doesn't.  Makes no mention of other DBs.
        objs = model.objects.bulk_create(objs_to_create)
        if not objs[0].id:
            # In case the database being used is one which doesn't return the ids, fetch them.
            objs = model.objects.filter(name__in=obj_names)
        return objs
    return []


def create_categories(qs):
    return create_things(qs, inv_models.Category, 'categories', 'category')


def create_departments(qs):
    return create_things(qs, inv_models.Department, 'departments', 'department')


def create_sources(qs):
    return create_things(qs, inv_models.Source, 'sources', 'source')
